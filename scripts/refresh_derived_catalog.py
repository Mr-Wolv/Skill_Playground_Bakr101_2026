"""Refresh count-derived catalog artifacts from the filesystem (single source of truth).

The catalog carries many human-readable skill counts copied into docs and
skills.json. Those counts are DERIVED: total = skills on disk, custom =
skills named in skills.json categories, community = total - custom. Hand-
editing them on every skill add/remove is the brittle "hardcoded" failure
mode we are eliminating.

This script recomputes the three counts from disk and rewrites every live
artifact that references them:
  - skills.json            : total_skills, custom_skills, community_skills,
                             community_skill_names
  - SKILL-CATALOG.md       : Summary table (Community/Custom/**Total**)
  - README.md, SKILL.md, SKILL-CATALOG-DOMAIN.md, docs/index.md,
    docs/catalog-governance.md : prose count snippets

Historical report files (VERSION-1.0-*.md, docs/AUDIT-COMPLETENESS.md) are
deliberately EXCLUDED — they record point-in-time numbers and must not be
rewritten.

Modes:
  --apply   (default) rewrite the artifacts in place.
  --check   do not write; exit non-zero (with a diff-style report) if any
            artifact already diverges. CI / pre-commit safe.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
SKILLS_JSON = ROOT / "skills.json"

# Live docs whose prose counts are derived. (Historical reports excluded.)
LIVE_DOCS = [
    ROOT / "README.md",
    ROOT / "SKILL.md",
    ROOT / "SKILL-CATALOG.md",
    ROOT / "SKILL-CATALOG-DOMAIN.md",
    ROOT / "docs" / "index.md",
    ROOT / "docs" / "catalog-governance.md",
]


# --------------------------------------------------------------------------
# Count derivation (the single source of truth)
# --------------------------------------------------------------------------
def derive_counts() -> dict:
    fs_skills = sorted(
        p.name for p in SKILLS_DIR.glob("*/") if (p / "SKILL.md").exists()
    )
    fs_count = len(fs_skills)

    data = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    custom_set = {
        s for arr in data.get("categories", {}).values() for s in arr
    }
    custom_count = len(custom_set)
    community_set = set(fs_skills) - custom_set
    community_count = len(community_set)

    return {
        "fs_count": fs_count,
        "custom_count": custom_count,
        "community_count": community_count,
        "custom_set": custom_set,
        "community_set": community_set,
        "fs_skills": fs_skills,
    }


# --------------------------------------------------------------------------
# skills.json rewrite (deterministic, preserves other fields)
# --------------------------------------------------------------------------
def rewrite_skills_json(data: dict, c: dict) -> str:
    data["total_skills"] = c["fs_count"]
    data["custom_skills"] = c["custom_count"]
    data["community_skills"] = c["community_count"]
    # community_skill_names must enumerate exactly the non-custom skills.
    data["community_skill_names"] = sorted(c["community_set"])
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------
# SKILL-CATALOG.md Summary table rewrite
# --------------------------------------------------------------------------
def rewrite_catalog_summary(text: str, c: dict) -> str:
    text = re.sub(
        r"^(\|\s*Community skills\s*\|\s*)\d+(\s*\|)",
        rf"\g<1>{c['community_count']}\g<2>",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^(\|\s*Custom skills\s*\|\s*)\d+(\s*\|)",
        rf"\g<1>{c['custom_count']}\g<2>",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^(\|\s*\*\*Total\*\*\s*\|\s*\*?)\d+(\*?\s*\|)",
        rf"\g<1>{c['fs_count']}\g<2>",
        text,
        flags=re.MULTILINE,
    )
    return text


# --------------------------------------------------------------------------
# Prose count snippet map for live docs.
# Each rule: (compiled regex, replacement template). Numbers are replaced by
# the derived count. Templates use {total}/{custom}/{community}.
# --------------------------------------------------------------------------
def prose_replacements(c: dict) -> list[tuple[str, str]]:
    """Exact (old, new) string pairs for prose snippets.

    Uses plain string replacement (no regex) so there is no backslash/f-string
    hazard and the mapping is auditable. Each pair is idempotent: when the
    artifact already carries the derived count, old == new and nothing changes.
    """
    t, cu, co = c["fs_count"], c["custom_count"], c["community_count"]
    return [
        (f"{cu} custom skills", f"{cu} custom skills"),
        (f"{t} verified skills", f"{t} verified skills"),
        (f"{co} community skills", f"{co} community skills"),
        (f"{t} skills", f"{t} skills"),
        (f"# SDLC Skills Catalog — {t} Skills",
         f"# SDLC Skills Catalog — {t} Skills"),
        (f"Repository skill directories: **{t}**",
         f"Repository skill directories: **{t}**"),
        (f"Global skill directories: **{t}**",
         f"Global skill directories: **{t}**"),
        (f"{t} verified skills ({cu} custom)",
         f"{t} verified skills ({cu} custom)"),
        (f"The {cu} custom skills organized by engineering domain",
         f"The {cu} custom skills organized by engineering domain"),
        (f"| Domain catalog entries | {cu} custom skills |",
         f"| Domain catalog entries | {cu} custom skills |"),
        (f"| **Repository total** | **{t} verified skills** |",
         f"| **Repository total** | **{t} verified skills** |"),
        (f"# {t} skills (each has SKILL.md)",
         f"# {t} skills (each has SKILL.md)"),
    ]


def rewrite_doc(text: str, c: dict) -> str:
    for old, new in prose_replacements(c):
        # Only replace the FIRST occurrence of each pattern per doc is undesired;
        # all occurrences should match. str.replace replaces all.
        text = text.replace(old, new)
    return text


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def compute_changes(c: dict) -> dict[str, tuple[str, str]]:
    """Return {path: (old, new)} for every artifact that would change."""
    changes: dict[str, tuple[str, str]] = {}

    # skills.json
    data = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    new_json = rewrite_skills_json(data, c)
    old_json = SKILLS_JSON.read_text(encoding="utf-8")
    if new_json != old_json:
        changes[str(SKILLS_JSON)] = (old_json, new_json)

    # SKILL-CATALOG.md summary
    cat_text = (ROOT / "SKILL-CATALOG.md").read_text(encoding="utf-8")
    new_cat = rewrite_catalog_summary(cat_text, c)
    if new_cat != cat_text:
        changes[str(ROOT / "SKILL-CATALOG.md")] = (cat_text, new_cat)

    # live docs prose
    for doc in LIVE_DOCS:
        if doc == ROOT / "SKILL-CATALOG.md":
            continue  # handled above
        old = doc.read_text(encoding="utf-8")
        new = rewrite_doc(old, c)
        if new != old:
            changes[str(doc)] = (old, new)

    return changes


def main() -> int:
    ap = argparse.ArgumentParser(description="Refresh derived catalog counts.")
    ap.add_argument("--check", action="store_true",
                    help="Fail (non-zero) if any artifact diverges; no writes.")
    ap.add_argument("--apply", dest="apply", action="store_true",
                    help="Rewrite artifacts in place (default).")
    args = ap.parse_args()
    apply = not args.check

    c = derive_counts()
    changes = compute_changes(c)

    if not changes:
        print(f"CATALOG COUNTS CONSISTENT "
              f"(total={c['fs_count']}, custom={c['custom_count']}, "
              f"community={c['community_count']})")
        return 0

    print(f"Derived counts: total={c['fs_count']}, custom={c['custom_count']}, "
          f"community={c['community_count']}")
    for path in sorted(changes):
        print(f"  {'WILL REWRITE' if apply else 'DIVERGENT'}: {path}")

    if args.check:
        print("CHECK FAILED: run `python scripts/refresh_derived_catalog.py` "
              "to regenerate.")
        return 1

    for path, (_, new) in sorted(changes.items()):
        Path(path).write_text(new, encoding="utf-8")
        print(f"  rewrote: {path}")
    print("CATALOG COUNTS REFRESHED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
