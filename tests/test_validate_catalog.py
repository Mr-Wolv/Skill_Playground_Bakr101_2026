"""Tests for scripts/validate_catalog.py.

These are HERMETIC: they mutate the real catalog/doc files to simulate a
regression, assert the validator catches it, then restore the original bytes.
A failure mid-test would leave a file dirty, so we guard the restore with
try/finally. The green-path test asserts the committed tree currently PASSES.
"""

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_catalog as vc  # noqa: E402


@pytest.fixture
def repo():
    """The real repo root, plus a helper to patch files safely."""
    return ROOT


def _patch(path: Path, old: str, new: str, count: int = 1):
    """Rewrite `old` -> `new` in a real file; raises if anchor missing.

    count=0 replaces ALL occurrences (Python's str.replace treats count as a
    limit, so 0 means "replace none" -- we special-case it to mean "replace all"
    for callers that need every copy gone for a substring check to fail).
    """
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"anchor not found in {path.name}:\n{old!r}")
    replaced = text.replace(old, new) if count == 0 else text.replace(old, new, count)
    path.write_text(replaced, encoding="utf-8")


class TestGreenPath:
    def test_green_path_passes(self, repo):
        errs = vc.validate(repo)
        assert errs == [], f"expected no errors on clean tree, got:\n{errs}"


class TestMissingSkillRefs:
    def test_readme_missing_ref_fails(self, repo):
        rm = repo / "README.md"
        orig = rm.read_bytes()
        try:
            _patch(rm, "repository-archaeology", "nonexistent-skill-xyz")
            errs = vc.validate(repo)
            assert any("README.md references missing skill: nonexistent-skill-xyz" in e
                       for e in errs)
        finally:
            rm.write_bytes(orig)

    def test_catalog_missing_ref_fails(self, repo):
        cat = repo / "SKILL-CATALOG.md"
        orig = cat.read_bytes()
        try:
            _patch(cat, "repository-archaeology", "nonexistent-skill-xyz")
            errs = vc.validate(repo)
            assert any("SKILL-CATALOG.md references missing skill: nonexistent-skill-xyz" in e
                       for e in errs)
        finally:
            cat.write_bytes(orig)

    def test_domain_missing_ref_fails(self, repo):
        dom = repo / "SKILL-CATALOG-DOMAIN.md"
        orig = dom.read_bytes()
        try:
            _patch(dom, "repository-archaeology", "nonexistent-skill-xyz")
            errs = vc.validate(repo)
            assert any("SKILL-CATALOG-DOMAIN.md references missing skill: nonexistent-skill-xyz" in e
                       for e in errs)
        finally:
            dom.write_bytes(orig)

    def test_skill_md_repr_missing_ref_fails(self, repo):
        sm = repo / "SKILL.md"
        orig = sm.read_bytes()
        try:
            _patch(sm, "unit-test-writer", "nonexistent-skill-xyz")
            errs = vc.validate(repo)
            assert any("SKILL.md references missing skill: nonexistent-skill-xyz" in e
                       for e in errs)
        finally:
            sm.write_bytes(orig)


class TestJsonCountDrift:
    def test_total_mismatch_fails(self, repo):
        sj = repo / "skills.json"
        orig = sj.read_bytes()
        try:
            data = json.loads(orig.decode("utf-8"))
            data["total_skills"] = 999
            sj.write_text(json.dumps(data), encoding="utf-8")
            errs = vc.validate(repo)
            assert any("total_skills=999 but filesystem has" in e for e in errs)
        finally:
            sj.write_bytes(orig)

    def test_custom_mismatch_fails(self, repo):
        sj = repo / "skills.json"
        orig = sj.read_bytes()
        try:
            data = json.loads(orig.decode("utf-8"))
            data["custom_skills"] = 1
            sj.write_text(json.dumps(data), encoding="utf-8")
            errs = vc.validate(repo)
            assert any("custom_skills=1 but expected" in e for e in errs)
        finally:
            sj.write_bytes(orig)


class TestLabelReconciliation:
    def test_relabel_custom_as_community_fails(self, repo):
        cat = repo / "SKILL-CATALOG.md"
        orig = cat.read_bytes()
        try:
            # code-review is in categories (custom); relabel its row as community.
            _patch(cat,
                   "| `code-review` | **custom** |",
                   "| `code-review` | community |")
            errs = vc.validate(repo)
            assert any("missing custom label for `code-review`" in e for e in errs)
        finally:
            cat.write_bytes(orig)


class TestDomainEnumeration:
    def test_missing_custom_skill_fails(self, repo):
        dom = repo / "SKILL-CATALOG-DOMAIN.md"
        orig = dom.read_bytes()
        try:
            _patch(dom,
                   "| `code-review` | Two-axis review (Standards + Spec) |\n",
                   "")
            errs = vc.validate(repo)
            assert any("missing custom skill `code-review`" in e for e in errs)
        finally:
            dom.write_bytes(orig)

    def test_intruding_community_skill_fails(self, repo):
        dom = repo / "SKILL-CATALOG-DOMAIN.md"
        orig = dom.read_bytes()
        try:
            extra = ("| `research-note` | Investigate a question against high-trust primary "
                     "sources and capture findings in the repo |\n")
            _patch(dom,
                   "| `research-methodology` | Source hierarchy, CRAAP test, RFC analysis, "
                   "synthesis |\n",
                   "| `research-methodology` | Source hierarchy, CRAAP test, RFC analysis, "
                   "synthesis |\n" + extra)
            errs = vc.validate(repo)
            assert any("lists `research-note` in domain tables but it is not custom" in e
                       for e in errs)
        finally:
            dom.write_bytes(orig)


class TestCommunitySkillNames:
    """skills.json must enumerate community skills by name, not just count."""

    def _corrupt(self, repo, mutate):
        sj = repo / "skills.json"
        orig = sj.read_bytes()
        data = json.loads(orig.decode("utf-8"))
        mutate(data)
        sj.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return sj, orig

    def test_green_path_passes(self, repo):
        assert vc.validate(repo) == []

    def test_missing_name_fails(self, repo):
        sj, orig = self._corrupt(repo, lambda d: d["community_skill_names"].pop())
        try:
            errs = vc.validate(repo)
            assert any("community_skill_names missing" in e for e in errs)
        finally:
            sj.write_bytes(orig)

    def test_extra_name_fails(self, repo):
        sj, orig = self._corrupt(
            repo, lambda d: d["community_skill_names"].append("does-not-exist-skill")
        )
        try:
            errs = vc.validate(repo)
            assert any("community_skill_names lists non-community" in e for e in errs)
        finally:
            sj.write_bytes(orig)

    def test_overlap_with_custom_fails(self, repo):
        sj, orig = self._corrupt(
            repo, lambda d: d["community_skill_names"].append(d["categories"]["testing"][0])
        )
        try:
            errs = vc.validate(repo)
            assert any("community_skill_names overlaps custom set" in e for e in errs)
        finally:
            sj.write_bytes(orig)

    def test_count_mismatch_fails(self, repo):
        sj, orig = self._corrupt(
            repo, lambda d: (d["community_skill_names"].append("extra-1"),
                             d["community_skill_names"].append("extra-2"))
        )
        try:
            errs = vc.validate(repo)
            assert any("community_skill_names=" in e and "but community_skills=" in e
                       for e in errs)
        finally:
            sj.write_bytes(orig)


class TestOrphanSkills:
    """Every on-disk skill must be documented (in skills.json or a doc)."""

    def test_orphan_skill_fails(self, repo):
        probe = repo / "skills" / "zzz-orphan-probe"
        created = False
        try:
            probe.mkdir(exist_ok=True)
            created = True
            (probe / "SKILL.md").write_text(
                "---\nname: zzz-orphan-probe\ndescription: probe\n---\n\n# probe\n",
                encoding="utf-8",
            )
            errs = vc.validate(repo)
            assert any(
                "orphan skill (on disk, documented nowhere): zzz-orphan-probe" in e
                for e in errs
            )
        finally:
            if created and probe.exists():
                shutil.rmtree(probe)


class TestExpectedSnippets:
    def test_readme_missing_count_fails(self, repo):
        rm = repo / "README.md"
        orig = rm.read_bytes()
        try:
            _patch(rm, "240 skills", "0 skills", count=0)
            errs = vc.validate(repo)
            assert any("README.md missing expected text: 240 skills" in e for e in errs)
        finally:
            rm.write_bytes(orig)
