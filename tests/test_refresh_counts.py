"""Unit tests for scripts/refresh_derived_catalog.py (the count source of truth).

These pin the generator's DERIVATION + REWRITE at the source, so a regression
in derive_counts / rewrite_doc / rewrite_skills_json is caught directly — not
only via the downstream validator. The original motivation: a generator bug
that emitted a wrong count (e.g. "0 skills") would otherwise slip through until
a later catalog check failed opaquely.

The generator's module globals (ROOT, SKILLS_DIR, SKILLS_JSON, LIVE_DOCS) point
at the real repo; we monkeypatch them onto a synthetic tmp repo so the test is
hermetic and fast (no 241-skill tree).
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_derived_catalog as r  # noqa: E402


SAMPLE_FM = """---
name: {n}
description: {d}
---

# {n}

Body text (ignored by the count derivation).
"""


@pytest.fixture
def fake_repo(tmp_path, monkeypatch):
    """A minimal 2-skill repo: 1 custom, 1 community."""
    skills = tmp_path / "skills"
    skills.mkdir()
    for n, d in (("alpha", "custom one"), ("beta", "community one")):
        (skills / n).mkdir()
        (skills / n / "SKILL.md").write_text(
            SAMPLE_FM.format(n=n, d=d), encoding="utf-8")

    data = {
        "total_skills": 99,          # intentionally wrong -> must be overwritten
        "custom_skills": 99,
        "community_skills": 99,
        "categories": {"engineering-mindset": ["alpha"]},
        "community_skill_names": ["WRONG"],
        "domains": ["engineering-mindset"],
    }
    (tmp_path / "skills.json").write_text(json.dumps(data, indent=2))

    # docs with deliberately WRONG placeholder counts -> must be corrected
    (tmp_path / "README.md").write_text(
        "# README\n\n999 skills\n999 custom skills\n999 verified skills\n",
        encoding="utf-8")
    (tmp_path / "SKILL.md").write_text(
        "# SKILL\n\n999 skills\n999 verified skills (999 custom)\n", encoding="utf-8")
    (tmp_path / "SKILL-CATALOG.md").write_text(
        "# SDLC Skills Catalog — 999 Skills\n\n"
        "| Community skills | 999 |\n| Custom skills | 999 |\n"
        "| **Total** | **999** |\n", encoding="utf-8")
    (tmp_path / "SKILL-CATALOG-DOMAIN.md").write_text(
        "# Domain\n\nThe 999 custom skills organized by engineering domain\n",
        encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text(
        "# I\n\n999 verified skills\n999 custom skills\n", encoding="utf-8")
    (docs / "catalog-governance.md").write_text(
        "Repository skill directories: **999**\n"
        "Global skill directories: **999**\n", encoding="utf-8")

    # repoint the generator at the synthetic repo
    monkeypatch.setattr(r, "ROOT", tmp_path)
    monkeypatch.setattr(r, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr(r, "SKILLS_JSON", tmp_path / "skills.json")
    monkeypatch.setattr(r, "LIVE_DOCS", [
        tmp_path / "README.md", tmp_path / "SKILL.md",
        tmp_path / "SKILL-CATALOG.md", tmp_path / "SKILL-CATALOG-DOMAIN.md",
        docs / "index.md", docs / "catalog-governance.md",
    ])
    return tmp_path


def test_derive_counts(fake_repo):
    c = r.derive_counts()
    assert c["fs_count"] == 2
    assert c["custom_count"] == 1
    assert c["community_count"] == 1
    assert c["custom_set"] == {"alpha"}
    assert c["community_set"] == {"beta"}


def test_rewrite_corrects_wrong_counts(fake_repo):
    c = r.derive_counts()
    changes = r.compute_changes(c)
    # every artifact with a wrong placeholder must appear in changes
    assert str(fake_repo / "skills.json") in changes
    assert str(fake_repo / "SKILL-CATALOG.md") in changes
    assert str(fake_repo / "README.md") in changes

    # apply and assert the derived numbers landed everywhere
    for path, (_, new) in changes.items():
        Path(path).write_text(new, encoding="utf-8")

    assert (fake_repo / "README.md").read_text().count("2 skills") == 1
    assert (fake_repo / "README.md").read_text().count("1 custom skills") == 1
    assert (fake_repo / "SKILL.md").read_text().count("2 verified skills (1 custom)") == 1
    cat = (fake_repo / "SKILL-CATALOG.md").read_text()
    assert "| Custom skills | 1 |" in cat
    assert "| **Total** | **2** |" in cat
    assert "# SDLC Skills Catalog — 2 Skills" in cat
    js = json.loads((fake_repo / "skills.json").read_text())
    assert js["total_skills"] == 2
    assert js["custom_skills"] == 1
    assert js["community_skills"] == 1
    assert js["community_skill_names"] == ["beta"]


def test_generator_never_emits_wrong_count(fake_repo):
    """Hard guard against the '0 skills' / arbitrary-number class of bug."""
    c = r.derive_counts()
    changes = r.compute_changes(c)
    blob = "\n".join(new for _, new in changes.values())
    # the only bare count tokens present must equal the derived ones
    for tok in ("0 skills", "0 custom skills", "999 skills", "999 custom skills"):
        assert tok not in blob, f"generator emitted stray count token: {tok!r}"
    assert f"{c['fs_count']} skills" in blob
    assert f"{c['custom_count']} custom skills" in blob


def test_rewrite_is_idempotent(fake_repo):
    c = r.derive_counts()
    # apply once
    for path, (_, new) in r.compute_changes(c).items():
        Path(path).write_text(new, encoding="utf-8")
    # a second pass must produce NO further changes
    changes2 = r.compute_changes(r.derive_counts())
    assert changes2 == {}, f"generator not idempotent: {list(changes2)}"
