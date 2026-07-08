"""Tests for scripts/validate_catalog.py.

These are HERMETIC: they mutate the real catalog/doc files to simulate a
regression, assert the validator catches it, then restore the original bytes.
A failure mid-test would leave a file dirty, so we guard the restore with
try/finally. The green-path test asserts the committed tree currently PASSES.
"""

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
    limit, so 0 means "replace none" — we special-case it to mean "replace all"
    for callers that need every copy gone for a substring check to fail).
    """
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"anchor not found in {path.name}:\n{old!r}")
    replaced = text.replace(old, new) if count == 0 else text.replace(old, new, count)
    path.write_text(replaced, encoding="utf-8")


class TestGreenPath:
    def test_committed_tree_passes(self, repo):
        assert vc.validate(repo) == [], "committed catalog should validate clean"


class TestReferenceIntegrity:
    def test_missing_skill_in_catalog_fails(self, repo):
        cat = repo / "SKILL-CATALOG.md"
        orig = cat.read_bytes()
        try:
            _patch(cat, "| `architecture-review` |", "| `definitely-not-a-skill` |")
            errs = vc.validate(repo)
            assert any("SKILL-CATALOG.md references missing skill: definitely-not-a-skill" in e
                       for e in errs)
        finally:
            cat.write_bytes(orig)

    def test_missing_skill_in_domain_fails(self, repo):
        dom = repo / "SKILL-CATALOG-DOMAIN.md"
        orig = dom.read_bytes()
        try:
            _patch(dom, "| `research-methodology` |",
                   "| `definitely-not-a-skill` |")
            errs = vc.validate(repo)
            assert any("SKILL-CATALOG-DOMAIN.md references missing skill: definitely-not-a-skill" in e
                       for e in errs)
        finally:
            dom.write_bytes(orig)


class TestManifestConsistency:
    def test_total_skills_mismatch_fails(self, repo):
        sj = repo / "skills.json"
        data = sj.read_text(encoding="utf-8")
        try:
            sj.write_text(data.replace('"total_skills": 238', '"total_skills": 999'),
                          encoding="utf-8")
            errs = vc.validate(repo)
            assert any("total_skills=999 but filesystem" in e for e in errs)
        finally:
            sj.write_text(data, encoding="utf-8")

    def test_custom_skills_mismatch_fails(self, repo):
        sj = repo / "skills.json"
        data = sj.read_text(encoding="utf-8")
        try:
            sj.write_text(data.replace('"custom_skills": 62', '"custom_skills": 99'),
                          encoding="utf-8")
            errs = vc.validate(repo)
            assert any("custom_skills=99 but expected" in e for e in errs)
        finally:
            sj.write_text(data, encoding="utf-8")


class TestPerRowLabelReconciliation:
    def test_custom_mislabeled_community_fails(self, repo):
        cat = repo / "SKILL-CATALOG.md"
        orig = cat.read_bytes()
        try:
            _patch(cat,
                   "| `architecture-review` | **custom** |",
                   "| `architecture-review` | community |")
            errs = vc.validate(repo)
            assert any("missing custom label for `architecture-review`" in e for e in errs)
        finally:
            cat.write_bytes(orig)

    def test_community_mislabeled_custom_fails(self, repo):
        cat = repo / "SKILL-CATALOG.md"
        orig = cat.read_bytes()
        try:
            _patch(cat,
                   "| `architecture-patterns` | community |",
                   "| `architecture-patterns` | **custom** |")
            errs = vc.validate(repo)
            assert any("labels `architecture-patterns` custom but it is not" in e for e in errs)
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


class TestExpectedSnippets:
    def test_readme_missing_count_fails(self, repo):
        rm = repo / "README.md"
        orig = rm.read_bytes()
        try:
            _patch(rm, "238 skills", "0 skills", count=0)
            errs = vc.validate(repo)
            assert any("README.md missing expected text: 238 skills" in e for e in errs)
        finally:
            rm.write_bytes(orig)
