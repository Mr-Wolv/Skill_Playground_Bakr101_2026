"""Tests for scripts/validate_catalog.py.

FOOL-PROOF BY CONSTRUCTION: these tests NEVER touch the real repo tree.

Every test runs against a throwaway COPY of the repo (real files cloned into a
temp dir by the `scratch` fixture). All mutations -- patching docs, corrupting
skills.json, dropping in an orphan skill -- happen ONLY inside that copy. The
committed tree is physically impossible to corrupt, so a test failure, a
keyboard interrupt, a timeout, or a teardown error can never leave a dirty file
behind. The temp dir is removed automatically by pytest's tmp_path lifetime.

This removes the hazard at the root: the old design mutated the real
skills.json / SKILL-CATALOG.md in place and relied on try/finally to restore
them. If pytest interrupted a test (timeout, Ctrl-C, exit), the restore was
skipped and the shared tree stayed corrupted -- which then failed unrelated
tests and required manual healing. We do not depend on cleanup running.

`validate(root)` derives every path from `root`, so pointing it at the scratch
copy exercises the same code paths as the real repo.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_catalog as vc  # noqa: E402


@pytest.fixture
def scratch(tmp_path):
    """A safe-to-mutate COPY of the repo, pointing validate() at `scratch`.

    The committed tree is never touched. We copy the whole repo EXCEPT the
    disk-hogs (.venv, .git, and any *.backup-* dirs left by sync scripts) --
    those are huge and pointless to copy. Skipping them keeps each scratch
    copy small/fast and avoids "No space left on device". This is immune to
    the validator's file list growing later, so the test won't silently rot.
    """
    dst = tmp_path / "repo"
    _copytree(ROOT, dst)
    vc.ROOT = dst
    yield dst
    vc.ROOT = ROOT


# Directories we must NEVER copy into a scratch repo (disk exhaustion hazard).
_EXCLUDE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".venv-cache"}


def _copytree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for child in src.iterdir():
        name = child.name
        if child.is_dir():
            if name in _EXCLUDE_DIRS or name.endswith(".backup"):
                continue  # skip disk-hogs and sync backups
            _copytree(child, dst / name)
        else:
            if name.endswith(".backup"):
                continue
            (dst / name).write_bytes(child.read_bytes())


def _patch(path: Path, old: str, new: str, count: int = 1):
    """Rewrite `old` -> `new` in a file; raises if anchor missing.

    Safe: only ever called on a scratch-copy path, never the real tree.
    """
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"anchor not found in {path.name}:\n{old!r}")
    replaced = text.replace(old, new) if count == 0 else text.replace(old, new, count)
    path.write_text(replaced, encoding="utf-8")


def _load_sj(scratch: Path) -> dict:
    return json.loads((scratch / "skills.json").read_text(encoding="utf-8"))


def _write_sj(scratch: Path, data: dict) -> None:
    # Preserve the repo's canonical formatting (indent=2, no ascii escaping).
    (scratch / "skills.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


class TestGreenPath:
    def test_green_path_passes(self, scratch):
        errs = vc.validate(scratch)
        assert errs == [], f"expected no errors on clean tree, got:\n{errs}"


class TestMissingSkillRefs:
    def test_readme_missing_ref_fails(self, scratch):
        rm = scratch / "README.md"
        _patch(rm, "repository-archaeology", "nonexistent-skill-xyz")
        errs = vc.validate(scratch)
        assert any("README.md references missing skill: nonexistent-skill-xyz" in e
                   for e in errs)

    def test_catalog_missing_ref_fails(self, scratch):
        cat = scratch / "SKILL-CATALOG.md"
        _patch(cat, "repository-archaeology", "nonexistent-skill-xyz")
        errs = vc.validate(scratch)
        assert any("SKILL-CATALOG.md references missing skill: nonexistent-skill-xyz" in e
                   for e in errs)

    def test_domain_missing_ref_fails(self, scratch):
        dom = scratch / "SKILL-CATALOG-DOMAIN.md"
        _patch(dom, "repository-archaeology", "nonexistent-skill-xyz")
        errs = vc.validate(scratch)
        assert any("SKILL-CATALOG-DOMAIN.md references missing skill: nonexistent-skill-xyz" in e
                   for e in errs)

    def test_skill_md_repr_missing_ref_fails(self, scratch):
        sm = scratch / "SKILL.md"
        _patch(sm, "unit-test-writer", "nonexistent-skill-xyz")
        errs = vc.validate(scratch)
        assert any("SKILL.md references missing skill: nonexistent-skill-xyz" in e
                   for e in errs)


class TestJsonCountDrift:
    def test_total_mismatch_fails(self, scratch):
        data = _load_sj(scratch)
        data["total_skills"] = 999
        _write_sj(scratch, data)
        errs = vc.validate(scratch)
        assert any("total_skills=999 but filesystem has" in e for e in errs)

    def test_custom_mismatch_fails(self, scratch):
        data = _load_sj(scratch)
        data["custom_skills"] = 1
        _write_sj(scratch, data)
        errs = vc.validate(scratch)
        assert any("custom_skills=1 but expected" in e for e in errs)


class TestLabelReconciliation:
    def test_relabel_custom_as_community_fails(self, scratch):
        cat = scratch / "SKILL-CATALOG.md"
        _patch(cat,
               "| `code-review` | **custom** |",
               "| `code-review` | community |")
        errs = vc.validate(scratch)
        assert any("missing custom label for `code-review`" in e for e in errs)


class TestDomainEnumeration:
    def test_missing_custom_skill_fails(self, scratch):
        dom = scratch / "SKILL-CATALOG-DOMAIN.md"
        _patch(dom,
               "| `code-review` | Two-axis review (Standards + Spec) |\n",
               "")
        errs = vc.validate(scratch)
        assert any("missing custom skill `code-review`" in e for e in errs)

    def test_intruding_community_skill_fails(self, scratch):
        dom = scratch / "SKILL-CATALOG-DOMAIN.md"
        extra = ("| `research-note` | Investigate a question against high-trust primary "
                 "sources and capture findings in the repo |\n")
        _patch(dom,
               "| `research-methodology` | Source hierarchy, CRAAP test, RFC analysis, "
               "synthesis |\n",
               "| `research-methodology` | Source hierarchy, CRAAP test, RFC analysis, "
               "synthesis |\n" + extra)
        errs = vc.validate(scratch)
        assert any("lists `research-note` in domain tables but it is not custom" in e
                   for e in errs)


class TestCommunitySkillNames:
    """skills.json must enumerate community skills by name, not just count."""

    def _corrupt(self, scratch, mutate):
        data = _load_sj(scratch)
        mutate(data)
        _write_sj(scratch, data)

    def test_green_path_passes(self, scratch):
        assert vc.validate(scratch) == []

    def test_missing_name_fails(self, scratch):
        self._corrupt(scratch, lambda d: d["community_skill_names"].pop())
        errs = vc.validate(scratch)
        assert any("community_skill_names missing" in e for e in errs)

    def test_extra_name_fails(self, scratch):
        self._corrupt(
            scratch, lambda d: d["community_skill_names"].append("does-not-exist-skill")
        )
        errs = vc.validate(scratch)
        assert any("community_skill_names lists non-community" in e for e in errs)

    def test_overlap_with_custom_fails(self, scratch):
        self._corrupt(
            scratch, lambda d: d["community_skill_names"].append(
                d["categories"]["testing"][0])
        )
        errs = vc.validate(scratch)
        assert any("community_skill_names overlaps custom set" in e for e in errs)

    def test_count_mismatch_fails(self, scratch):
        self._corrupt(
            scratch, lambda d: (d["community_skill_names"].append("extra-1"),
                                d["community_skill_names"].append("extra-2"))
        )
        errs = vc.validate(scratch)
        assert any("community_skill_names=" in e and "but community_skills=" in e
                   for e in errs)


class TestOrphanSkills:
    """Every on-disk skill must be documented (in skills.json or a doc)."""

    def test_orphan_skill_fails(self, scratch):
        probe = scratch / "skills" / "zzz-orphan-probe"
        probe.mkdir(parents=True, exist_ok=True)
        (probe / "SKILL.md").write_text(
            "---\nname: zzz-orphan-probe\ndescription: probe\n---\n\n# probe\n",
            encoding="utf-8",
        )
        errs = vc.validate(scratch)
        assert any(
            "orphan skill (on disk, documented nowhere): zzz-orphan-probe" in e
            for e in errs
        )
        # cleanup is automatic via tmp_path, but be explicit so the copy is tidy.
        import shutil
        shutil.rmtree(probe, ignore_errors=True)


class TestExpectedSnippets:
    def test_readme_missing_count_fails(self, scratch):
        sj = _load_sj(scratch)
        fs_count = sj["total_skills"]  # derived, never hardcoded
        rm = scratch / "README.md"
        _patch(rm, f"{fs_count} skills", "0 skills", count=0)
        errs = vc.validate(scratch)
        assert any(f"README.md missing expected text: {fs_count} skills" in e
                   for e in errs)


class TestCatalogSummaryCounts:
    """SKILL-CATALOG.md Summary table must match folder-derived counts (F-02/F-09).

    Expected counts are DERIVED from skills.json so the test never rots when
    the catalog grows/shrinks -- no hardcoded totals.
    """

    def test_custom_summary_drift_fails(self, scratch):
        sj = _load_sj(scratch)
        custom_count = sj["custom_skills"]
        wrong = custom_count - 2  # any wrong value triggers the drift check
        cat = scratch / "SKILL-CATALOG.md"
        _patch(cat, f"| Custom skills | {custom_count} |",
               f"| Custom skills | {wrong} |")
        errs = vc.validate(scratch)
        assert any(
            f"SKILL-CATALOG.md Summary 'Custom skills'={wrong} but expected {custom_count}" in e
            for e in errs
        )

    def test_total_summary_drift_fails(self, scratch):
        sj = _load_sj(scratch)
        fs_count = sj["total_skills"]
        wrong = fs_count - 2
        cat = scratch / "SKILL-CATALOG.md"
        _patch(cat, f"| **Total** | **{fs_count}** |",
               f"| **Total** | **{wrong}** |")
        errs = vc.validate(scratch)
        assert any(
            f"SKILL-CATALOG.md Summary '**Total**'={wrong} but expected {fs_count}" in e
            for e in errs
        )
