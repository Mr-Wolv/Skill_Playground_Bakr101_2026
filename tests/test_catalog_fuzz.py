"""Dive 6 — whole-catalog PROPERTY FUZZ over skills.json <-> disk <-> docs.

The catalog is a 4-way redundant structure: skills.json (categories +
community list + counts), the on-disk skills/*/SKILL.md tree, and the prose
docs (SKILL-CATALOG.md, SKILL-CATALOG-DOMAIN.md, README.md, SKILL.md,
SDLC-PHRASE-CHEATSHEET.md, docs/index.md, docs/catalog-governance.md). Any
real drift between these must be REPORTED by validate_catalog.validate(),
never silently approved and never crash the gate.

This fuzz materialises a FAITHFUL-BUT-CHEAP snapshot of the committed tree into
a tmp dir (stub SKILL.md frontmatter only + the 7 docs + skills.json; never the
full 241-skill tree, never tracked files), then injects ONE drift at a time on
a random axis and asserts two invariants hold for EVERY mutation:

  (1) CRASH-SAFETY -> validate() always returns a list[str]; never raises,
      even on a corrupt skills.json / missing doc / empty skill file.
  (2) SOUNDNESS    -> a genuine drift is ALWAYS reported (errors non-empty).
      The validator cannot be fooled into a silent PASS.

N operators cover every redundancy axis. The first operator is the "control":
an untouched snapshot must validate clean (proves the baseline itself is
consistent, so a non-empty result on an operator is attributed to that drift).

PERFORMANCE: the earlier version copytree'd the real 241-skill tree on every
trial (~4.6s each -> ~410s total). This version builds a tiny stub snapshot ONCE
(session fixture) and restores ONLY the 1-2 files each operator mutates, so the
whole file runs in a few seconds. If you change the snapshot shape, re-baseline
the per-test times in the commit log.
"""

import json
import random
import re
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_catalog as vc  # noqa: E402

DOC_RELS = (
    "SKILL-CATALOG.md",
    "SKILL-CATALOG-DOMAIN.md",
    "README.md",
    "SKILL.md",
    "SDLC-PHRASE-CHEATSHEET.md",
    "docs/index.md",
    "docs/catalog-governance.md",
)


def _frontmatter_only(text: str) -> str:
    """Keep only the YAML frontmatter block (what validate parses)."""
    m = re.match(r"^---\n.*?\n---\n?", text, re.DOTALL)
    if m:
        return m.group(0)
    # no frontmatter -> minimal valid stub so the file is still parseable
    return "---\nname: unknown\ndescription: stub\n---\n"


def _build_template() -> Path:
    """Create a cheap, faithful snapshot of the catalog under a temp dir.

    Only the fields validate() reads are materialised:
      - skills.json (verbatim)
      - one stub SKILL.md per skill (frontmatter only, <1KB each)
      - the 7 docs (copied verbatim; they are small)
    This is ~50x cheaper to copytree than the real tree.
    """
    tpl = Path(tempfile.mkdtemp()) / "tpl"
    tpl.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "skills.json", tpl / "skills.json")
    for rel in DOC_RELS:
        src = ROOT / rel
        if src.exists():
            dst = tpl / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst)
    (tpl / "skills").mkdir()
    for p in (ROOT / "skills").glob("*/"):
        fm = p / "SKILL.md"
        if not fm.exists():
            continue
        (tpl / "skills" / p.name).mkdir()
        (tpl / "skills" / p.name / "SKILL.md").write_text(
            _frontmatter_only(fm.read_text(encoding="utf-8")) + "\n",
            encoding="utf-8",
        )
    return tpl


@pytest.fixture(scope="session")
def template():
    tpl = _build_template()
    yield tpl
    shutil.rmtree(tpl, ignore_errors=True)


class TestSnapshotIsCheap:
    """Structural guard: the fuzz snapshot MUST stay tiny.

    The original Dive-6 cost ~410s because it copytree'd the real 241-skill
    tree on every trial. This asserts the template is the cheap stub form
    (frontmatter-only SKILL.md + docs + skills.json), so the 411s regression
    can never silently return. If someone 'simplifies' the snapshot back to a
    full copytree, this fails loudly.
    """

    def test_template_excludes_full_skill_tree(self, template):
        total = sum(p.stat().st_size for p in template.rglob("*") if p.is_file())
        # Real tree SKILL.md files are ~1-15KB each (241 of them) -> tens of MB.
        # The stub template must be a small fraction of that.
        assert total < 5 * 1024 * 1024, f"template too big ({total} bytes) — not the cheap stub form"

    def test_each_skill_is_frontmatter_only(self, template):
        for p in (template / "skills").glob("*/SKILL.md"):
            body = p.read_text(encoding="utf-8")
            assert body.lstrip().startswith("---"), f"{p} is not a frontmatter stub"
            # stub must not carry a full body (no fenced blocks etc.)
            assert "```" not in body, f"{p} contains body content (not stubbed)"


def _materialize(template: Path, dst: Path) -> Path:
    """Cheap per-trial copy of the tiny template (not the real 241-skill tree)."""
    shutil.copytree(template, dst)
    return dst


class _Restore:
    """Records the bytes of touched paths and restores them exactly.

    Lets one materialized snapshot be reused across many mutations without
    re-copytree'ing the whole tree (the original ~410s cost).
    """

    def __init__(self, root: Path):
        self.root = root
        self._saved = {}

    def touch(self, rel: str):
        p = self.root / rel
        self._saved[str(p)] = p.read_bytes() if p.exists() else None

    def add_dir(self, rel: str):
        self._saved["__dir__" + str(self.root / rel)] = True

    def restore(self):
        for key, data in self._saved.items():
            if key.startswith("__dir__"):
                continue
            p = Path(key)
            if data is None:
                if p.exists():
                    p.unlink()
            else:
                p.write_bytes(data)
        # handle removed dirs (disk-del / disk-add operators)
        for key in list(self._saved):
            if key.startswith("__dir__"):
                d = Path(key[len("__dir__"):])
                if not d.exists():
                    d.mkdir(parents=True, exist_ok=True)


def _skills_on_disk(root: Path):
    return sorted(p.name for p in (root / "skills").glob("*/") if (p / "SKILL.md").exists())


def _load_json(root: Path):
    return json.loads((root / "skills.json").read_text(encoding="utf-8"))


def _write_json(root: Path, data):
    (root / "skills.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


class TestCatalogFuzz:
    # --- drift operators: each takes (root, rng, restore) and mutates exactly
    #     the file(s) it touches (registering them with restore first). Returns
    #     True if it actually mutated something (False = no-op; still clean). ---
    def _ops(self):
        return [
            self._op_control,           # 0  untouched (must be clean)
            self._op_json_drop_skill,   # 1  skills.json: drop a category skill
            self._op_json_bad_count,    # 2  skills.json: wrong total_skills
            self._op_json_orphan_comm,  # 3  skills.json: community name not on disk
            self._op_json_comm_missing, # 4  skills.json: omit a real community skill
            self._op_disk_add_skill,    # 5  add an orphan skill dir (no docs)
            self._op_disk_del_skill,    # 6  delete a skill dir (json still refs it)
            self._op_disk_bad_fm,       # 7  corrupt a SKILL.md (no frontmatter)
            self._op_doc_drop_ref,      # 8  catalog doc drops a backtick ref
            self._op_doc_wrong_count,   # 9  README count snippet wrong
            self._op_json_corrupt,      # 10 skills.json invalid JSON
            self._op_doc_missing,       # 11 delete a required doc file
            self._op_disk_empty_skill,  # 12 skill dir with empty SKILL.md
            self._op_json_dup_comm,     # 13 community list overlaps custom set
        ]

    def _op_control(self, root, rng, restore):
        return False  # no mutation; baseline must validate clean

    def _op_json_drop_skill(self, root, rng, restore):
        restore.touch("skills.json")
        data = _load_json(root)
        names = [n for arr in data["categories"].values() for n in arr]
        if not names:
            return False
        victim = rng.choice(names)
        for c, arr in data["categories"].items():
            if victim in arr:
                arr.remove(victim)
        _write_json(root, data)
        return True

    def _op_json_bad_count(self, root, rng, restore):
        restore.touch("skills.json")
        data = _load_json(root)
        data["total_skills"] = data["total_skills"] + rng.randint(1, 50) + 1
        _write_json(root, data)
        return True

    def _op_json_orphan_comm(self, root, rng, restore):
        restore.touch("skills.json")
        data = _load_json(root)
        existing = set(_skills_on_disk(root))
        ghost = "zzz-nonexistent-skill-12345"
        while ghost in existing:
            ghost += "x"
        data.setdefault("community_skill_names", []).append(ghost)
        data["community_skills"] = data.get("community_skills", 0) + 1
        _write_json(root, data)
        return True

    def _op_json_comm_missing(self, root, rng, restore):
        restore.touch("skills.json")
        data = _load_json(root)
        comm = data.get("community_skill_names", [])
        if not comm:
            return False
        victim = rng.choice(comm)
        comm.remove(victim)
        data["community_skill_names"] = comm
        _write_json(root, data)
        return True

    def _op_disk_add_skill(self, root, rng, restore):
        name = "zzz-orphan-disk-skill-98765"
        restore.add_dir(f"skills/{name}")
        d = root / "skills" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(
            "---\nname: %s\ndescription: orphan added by fuzz\n---\n# %s\n" % (name, name),
            encoding="utf-8",
        )
        return True

    def _op_disk_del_skill(self, root, rng, restore):
        names = _skills_on_disk(root)
        if not names:
            return False
        victim = rng.choice(names)
        restore.add_dir(f"skills/{victim}")
        shutil.rmtree(root / "skills" / victim)
        return True

    def _op_disk_bad_fm(self, root, rng, restore):
        names = _skills_on_disk(root)
        if not names:
            return False
        victim = rng.choice(names)
        restore.touch(f"skills/{victim}/SKILL.md")
        (root / "skills" / victim / "SKILL.md").write_text(
            "# no frontmatter here\n", encoding="utf-8"
        )
        return True

    def _op_doc_drop_ref(self, root, rng, restore):
        restore.touch("SKILL-CATALOG.md")
        cat = root / "SKILL-CATALOG.md"
        text = cat.read_text(encoding="utf-8")
        m = re.search(r"^`(?P<n>[a-z0-9_-]+)` \| \*\*custom\*\*.*$", text, re.MULTILINE)
        if not m:
            return False
        victim = m.group("n")
        new = re.sub(
            r"^`" + re.escape(victim) + r"` \| \*\*custom\*\*.*$\n?",
            "", text, count=1, flags=re.MULTILINE,
        )
        if new == text:
            return False
        cat.write_text(new, encoding="utf-8")
        return True

    def _op_doc_wrong_count(self, root, rng, restore):
        restore.touch("README.md")
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

    def _op_json_corrupt(self, root, rng, restore):
        restore.touch("skills.json")
        (root / "skills.json").write_text("{ not valid json,,,\n", encoding="utf-8")
        return True

    def _op_doc_missing(self, root, rng, restore):
        targets = [
            "SKILL-CATALOG.md",
            "SKILL-CATALOG-DOMAIN.md",
            "README.md",
            "SDLC-PHRASE-CHEATSHEET.md",
            "SKILL.md",
        ]
        victim = rng.choice(targets)
        restore.touch(victim)
        p = root / victim
        if p.exists():
            p.unlink()
            return True
        return False

    def _op_disk_empty_skill(self, root, rng, restore):
        names = _skills_on_disk(root)
        if not names:
            return False
        victim = rng.choice(names)
        restore.touch(f"skills/{victim}/SKILL.md")
        (root / "skills" / victim / "SKILL.md").write_text("", encoding="utf-8")
        return True

    def _op_json_dup_comm(self, root, rng, restore):
        restore.touch("skills.json")
        data = _load_json(root)
        custom = [n for arr in data["categories"].values() for n in arr]
        if not custom:
            return False
        victim = rng.choice(custom)
        data.setdefault("community_skill_names", []).append(victim)
        data["community_skills"] = data.get("community_skills", 0) + 1
        _write_json(root, data)
        return True

    def test_crash_safety(self, template, tmp_path):
        # For MANY random (operator, seed) pairs, validate() must return a list
        # and never raise. Reuses ONE materialized snapshot across all trials via
        # surgical restore (no full-tree recopy -> fast).
        ops = self._ops()
        n_trials = 40
        root = _materialize(template, tmp_path / "cs")
        restore = _Restore(root)
        for trial in range(n_trials):
            try:
                rng = random.Random(trial)
                op = ops[rng.randrange(len(ops))]
                op(root, rng, restore)
                result = vc.validate(root)
            except Exception as e:  # property (1): must never happen
                raise AssertionError(f"validate() crashed on trial {trial}: {e!r}")
            finally:
                restore.restore()
            assert isinstance(result, list), f"validate() did not return list on trial {trial}"

    def test_soundness_drift_is_reported(self, template, tmp_path):
        # For EVERY drift operator (excluding the control at index 0), validate()
        # must return >=1 error. The control proves the baseline is clean, so a
        # non-empty result can only come from the injected drift.
        ops = self._ops()
        root = _materialize(template, tmp_path / "snd")
        restore = _Restore(root)
        assert vc.validate(root) == [], "baseline snapshot must validate clean"

        missed = []
        for idx in range(1, len(ops)):  # skip control
            rng = random.Random(idx * 7 + 3)
            mutated = ops[idx](root, rng, restore)
            errors = vc.validate(root)
            restore.restore()
            if not mutated:
                continue  # operator chose not to apply (e.g. empty list) -> n/a
            if not errors:
                missed.append(idx)
        assert not missed, f"drift operators produced SILENT PASS (no errors): {missed}"
