"""Dive 6 — whole-catalog PROPERTY FUZZ over skills.json <-> disk <-> docs.

The catalog is a 4-way redundant structure: skills.json (categories +
community list + counts), the on-disk skills/*/SKILL.md tree, and the prose
docs (SKILL-CATALOG.md, SKILL-CATALOG-DOMAIN.md, README.md, SKILL.md,
SDLC-PHRASE-CHEATSHEET.md, docs/index.md, docs/catalog-governance.md). Any
real drift between these must be REPORTED by validate_catalog.validate(),
never silently approved and never crash the gate.

This fuzz materialises a real snapshot of the committed tree into a tmp dir
(copytree — never touches tracked files), then injects ONE drift at a time on
a random axis and asserts two invariants hold for EVERY mutation:

  (1) CRASH-SAFETY -> validate() always returns a list[str]; never raises,
      even on a corrupt skills.json / missing doc / empty skill file.
  (2) SOUNDNESS    -> a genuine drift is ALWAYS reported (errors non-empty).
      The validator cannot be fooled into a silent PASS.

N operators cover every redundancy axis. The first operator is the "control":
an untouched snapshot must validate clean (proves the baseline itself is
consistent, so a non-empty result on an operator is attributed to that drift).
"""

import json
import random
import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_catalog as vc  # noqa: E402


def _snapshot(tmp: Path) -> Path:
    """Build a minimal but faithful repo snapshot in tmp containing ONLY the
    files validate_catalog.validate() reads: skills.json, the skills/ tree,
    and the 7 docs. Copies just those (NOT the whole repo), so the fuzz stays
    fast and fully hermetic — tracked files untouched.
    """
    dst = tmp / "repo"
    dst.mkdir(parents=True, exist_ok=True)
    # skills.json + root docs (single copytree of the repo, then prune unneeded)
    shutil.copytree(
        ROOT, dst,
        ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "*.pyc", ".pytest_cache", "tests",
            "scripts", ".github", "docs", "*.txt",
        ),
        dirs_exist_ok=True,
    )
    # docs/ subtree (only the two files validate reads)
    docs = dst / "docs"
    docs.mkdir(exist_ok=True)
    for name in ("index.md", "catalog-governance.md"):
        src = ROOT / "docs" / name
        if src.exists():
            shutil.copy(src, docs / name)
    return dst


def _skills_on_disk(root: Path):
    return sorted(p.name for p in (root / "skills").glob("*/") if (p / "SKILL.md").exists())


def _load_json(root: Path):
    return json.loads((root / "skills.json").read_text(encoding="utf-8"))


class TestCatalogFuzz:
    # --- drift operators: each takes (root, rng) and returns True if it
    #     successfully mutated something (False = no-op, still must be clean) ---
    def _ops(self):
        return [
            self._op_control,          # 0  untouched (must be clean)
            self._op_json_drop_skill,  # 1  skills.json: drop a category skill
            self._op_json_bad_count,   # 2  skills.json: wrong total_skills
            self._op_json_orphan_comm, # 3  skills.json: community name not on disk
            self._op_json_comm_missing, # 4 skills.json: omit a real community skill
            self._op_disk_add_skill,   # 5  add an orphan skill dir (no docs)
            self._op_disk_del_skill,   # 6  delete a skill dir (json still refs it)
            self._op_disk_bad_fm,      # 7  corrupt a SKILL.md (no frontmatter)
            self._op_doc_drop_ref,     # 8  catalog doc drops a backtick ref
            self._op_doc_wrong_count,  # 9  README count snippet wrong
            self._op_json_corrupt,     # 10 skills.json invalid JSON
            self._op_doc_missing,      # 11 delete a required doc file
            self._op_disk_empty_skill, # 12 skill dir with empty SKILL.md
            self._op_json_dup_comm,    # 13 community list overlaps custom set
        ]

    def _op_control(self, root, rng):
        return False  # no mutation; baseline must validate clean

    def _op_json_drop_skill(self, root, rng):
        data = _load_json(root)
        cats = data["categories"]
        names = [n for arr in cats.values() for n in arr]
        if not names:
            return False
        victim = rng.choice(names)
        for c, arr in cats.items():
            if victim in arr:
                arr.remove(victim)
        (root / "skills.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True

    def _op_json_bad_count(self, root, rng):
        data = _load_json(root)
        data["total_skills"] = data["total_skills"] + rng.randint(1, 50) + 1
        (root / "skills.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True

    def _op_json_orphan_comm(self, root, rng):
        data = _load_json(root)
        existing = set(_skills_on_disk(root))
        ghost = "zzz-nonexistent-skill-12345"
        while ghost in existing:
            ghost += "x"
        data.setdefault("community_skill_names", []).append(ghost)
        data["community_skills"] = data.get("community_skills", 0) + 1
        (root / "skills.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True

    def _op_json_comm_missing(self, root, rng):
        data = _load_json(root)
        comm = data.get("community_skill_names", [])
        if not comm:
            return False
        victim = rng.choice(comm)
        comm.remove(victim)
        data["community_skill_names"] = comm
        (root / "skills.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True

    def _op_disk_add_skill(self, root, rng):
        name = "zzz-orphan-disk-skill-98765"
        d = root / "skills" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(
            "---\nname: %s\ndescription: orphan added by fuzz\n---\n# %s\n" % (name, name),
            encoding="utf-8",
        )
        return True

    def _op_disk_del_skill(self, root, rng):
        names = _skills_on_disk(root)
        if not names:
            return False
        victim = rng.choice(names)
        shutil.rmtree(root / "skills" / victim)
        return True

    def _op_disk_bad_fm(self, root, rng):
        names = _skills_on_disk(root)
        if not names:
            return False
        victim = rng.choice(names)
        (root / "skills" / victim / "SKILL.md").write_text(
            "# no frontmatter here\n", encoding="utf-8"
        )
        return True

    def _op_doc_drop_ref(self, root, rng):
        # Remove a skill's custom-label TABLE ROW from SKILL-CATALOG.md.
        # validate() checks exact custom-labeled set -> "missing custom label
        # for X" when the row is gone. This is a real, validator-defined drift.
        cat = root / "SKILL-CATALOG.md"
        text = cat.read_text(encoding="utf-8")
        m = re.search(r"^\| `(?P<n>[a-z0-9_-]+)` \| \*\*custom\*\*.*$", text, re.MULTILINE)
        if not m:
            return False
        victim = m.group("n")
        new = re.sub(
            r"^\| `" + re.escape(victim) + r"` \| \*\*custom\*\*.*$\n?",
            "", text, count=1, flags=re.MULTILINE,
        )
        if new == text:
            return False
        cat.write_text(new, encoding="utf-8")
        return True

    def _op_doc_wrong_count(self, root, rng):
        # Corrupt EVERY "<N> skills" count snippet in README so the validator's
        # expected-snippet check ("{fs_count} skills") can no longer match.
        readme = root / "README.md"
        text = readme.read_text(encoding="utf-8")
        new = re.sub(
            r"(\d+) skills",
            lambda m: f"{int(m.group(1)) + 111} skills",
            text,
        )
        if new == text:
            return False
        readme.write_text(new, encoding="utf-8")
        return True

    def _op_json_corrupt(self, root, rng):
        (root / "skills.json").write_text("{ not valid json,,,", encoding="utf-8")
        return True

    def _op_doc_missing(self, root, rng):
        targets = [
            root / "SKILL-CATALOG.md",
            root / "SKILL-CATALOG-DOMAIN.md",
            root / "README.md",
            root / "SDLC-PHRASE-CHEATSHEET.md",
            root / "SKILL.md",
        ]
        victim = rng.choice(targets)
        if victim.exists():
            victim.unlink()
            return True
        return False

    def _op_disk_empty_skill(self, root, rng):
        names = _skills_on_disk(root)
        if not names:
            return False
        victim = rng.choice(names)
        (root / "skills" / victim / "SKILL.md").write_text("", encoding="utf-8")
        return True

    def _op_json_dup_comm(self, root, rng):
        data = _load_json(root)
        cats = data["categories"]
        custom = [n for arr in cats.values() for n in arr]
        if not custom:
            return False
        victim = rng.choice(custom)
        data.setdefault("community_skill_names", []).append(victim)
        data["community_skills"] = data.get("community_skills", 0) + 1
        (root / "skills.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True

    def test_crash_safety(self, tmp_path):
        # For EVERY operator (incl. control) and MANY random seeds, validate()
        # must return a list and never raise. This is the property that proves
        # the gate cannot be exploded into silence by malformed input.
        ops = self._ops()
        for trial in range(40):
            root = _snapshot(tmp_path / f"t{trial}")
            try:
                rng = random.Random(trial)
                op = ops[rng.randrange(len(ops))]
                op(root, rng)
                result = vc.validate(root)
            except Exception as e:  # property (1): must never happen
                shutil.rmtree(tmp_path / f"t{trial}", ignore_errors=True)
                raise AssertionError(f"validate() crashed on trial {trial}: {e!r}")
            assert isinstance(result, list), f"validate() did not return list on trial {trial}"
            shutil.rmtree(root, ignore_errors=True)

    def test_soundness_drift_is_reported(self, tmp_path):
        # For EVERY drift operator (excluding the control at index 0), validate()
        # must return >=1 error. The control proves the baseline is clean, so a
        # non-empty result can only come from the injected drift.
        ops = self._ops()
        # baseline clean check
        base = _snapshot(tmp_path / "baseline")
        assert vc.validate(base) == [], "baseline snapshot must validate clean"
        shutil.rmtree(base, ignore_errors=True)

        missed = []
        for idx in range(1, len(ops)):  # skip control
            root = _snapshot(tmp_path / f"op{idx}")
            rng = random.Random(idx * 7 + 3)
            mutated = ops[idx](root, rng)
            errors = vc.validate(root)
            shutil.rmtree(root, ignore_errors=True)
            if not mutated:
                continue  # operator chose not to apply (e.g. empty list) -> n/a
            if not errors:
                missed.append(idx)
        assert not missed, f"drift operators produced SILENT PASS (no errors): {missed}"
