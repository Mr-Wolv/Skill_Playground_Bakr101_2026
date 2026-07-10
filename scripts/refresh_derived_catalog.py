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
    # The free-text description also carries a count; keep it derived so a
    # hand-edited "240 verified skills" can't silently contradict the folder set.
    desc = data.get("description", "")
    data["description"] = re.sub(
        r"\b\d+ verified skills\b", f"{c['fs_count']} verified skills", desc
    )
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
        r"^(\|\s*\*\*Total\*\*\s*\|\s*\*{0,2})\d+(\*{0,2}\s*\|)",
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
def prose_patterns(c: dict) -> list[tuple[re.Pattern, str]]:
    """(regex, replacement) pairs that CORRECT any count to the derived value.

    Unlike exact-match no-op pairs, these replace the NUMBER wherever it
    appears in a known count phrase, so a drifted count (e.g. '999 skills')
    is actually corrected to the derived one -- not merely confirmed. Specific
    phrases are listed before the generic bare 'N skills' so qualifiers
    ('verified'/'custom'/'community') are consumed by their own rule and the
    generic pass only touches remaining bare totals.
    """
    t, cu, co = c["fs_count"], c["custom_count"], c["community_count"]
    return [
        (re.compile(r"(\d+) custom skills"), f"{cu} custom skills"),
        (re.compile(r"(\d+) verified skills \(\d+ custom\)"),
         f"{t} verified skills ({cu} custom)"),
        (re.compile(r"(\d+) verified skills"), f"{t} verified skills"),
        (re.compile(r"(\d+) community skills"), f"{co} community skills"),
        (re.compile(r"# SDLC Skills Catalog.*?(\d+) Skills", re.IGNORECASE),
         f"# SDLC Skills Catalog — {t} Skills"),
        (re.compile(r"Repository skill directories: \*\*(\d+)\*\*"),
         f"Repository skill directories: **{t}**"),
        (re.compile(r"Global skill directories: \*\*(\d+)\*\*"),
         f"Global skill directories: **{t}**"),
        (re.compile(r"The (\d+) custom skills organized by engineering domain"),
         f"The {cu} custom skills organized by engineering domain"),
        # domain-catalog scope variants ("64 curated custom skills") and the
        # "complete 240-skill listing" phrasing (hyphenated, not caught by the
        # bare 'N skills' rule) — both must track the derived counts.
        (re.compile(r"(\d+) curated custom skills"), f"{cu} curated custom skills"),
        (re.compile(r"complete (\d+)-skill listing"), f"complete {t}-skill listing"),
        (re.compile(r"\| Domain catalog entries \| (\d+) custom skills \|"),
         f"| Domain catalog entries | {cu} custom skills |"),
        (re.compile(r"\|\s*\*\*Repository total\*\*\s*\| \*\*(\d+) verified skills\*\*\s*\|"),
         f"| **Repository total** | **{t} verified skills** |"),
        (re.compile(r"# (\d+) skills \(each has SKILL.md\)"),
         f"# {t} skills (each has SKILL.md)"),
        # generic bare 'N skills' LAST: every remaining bare count is the total
        (re.compile(r"(\d+) skills"), f"{t} skills"),
    ]


def rewrite_doc(text: str, c: dict) -> str:
    for pat, repl in prose_patterns(c):
        text = pat.sub(repl, text)
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

    # SKILL-CATALOG.md summary table + any count prose in the body (e.g. the
    # "# SDLC Skills Catalog — N Skills" title). rewrite_doc is safe on the
    # summary rows (no "digit skills" adjacency there) and corrects the title.
    cat_text = (ROOT / "SKILL-CATALOG.md").read_text(encoding="utf-8")
    new_cat = rewrite_doc(rewrite_catalog_summary(cat_text, c), c)
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
