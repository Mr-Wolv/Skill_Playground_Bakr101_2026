#!/usr/bin/env python3
"""Functional integrity gate for the skill store (hardened, v2).

Resolves every internal file reference in each skill's SKILL.md against the
filesystem and reports missing files. This is the real bar for "a skill is
complete" -- a skill that links a file that does not exist is broken, even if
its frontmatter parses.

Reference forms handled (with false-positive filtering):
  * markdown links:        ](target)
  * backtick path tokens:  `references/x.md`, `/details.md`, `skills/foo/SKILL.md`
  * leading-slash refs are STORE-ROOT-relative in this catalog's convention:
        /details.md                  -> <skill>/references/details.md  (and other bases)
        /core-web-vitals/SKILL.md    -> <store>/core-web-vitals/SKILL.md
        /docs/index.md               -> <repo>/docs/index.md
  * backtick path preceded by a capitalized foreign brand (e.g. Allium
    `references/...`) is an EXTERNAL tool's doc, not ours -> skipped.
  * cross-skill pointers `skills/<name>/SKILL.md` resolve within the SAME store.
  * literal placeholders (`<name>`) and glob patterns (`*.md`) are skipped.
  * runtime-generated artifacts (plan.md/todo.md/ideas/.../agents/issue-tracker)
    and external-tool paths (.claude/, copilot-instructions, github.com) are
    intentionally not catalog files -> skipped, not flagged.

This version CLOSES the previous blind spot: v1 only resolved `references/...`
and relative links, silently ignoring ~292 leading-slash store-root refs, so it
could never catch a real break there. Now those are validated too.

Usage:
    python scripts/verify_skill_references.py <store_dir> [--repo-docs <dir>]
Exits non-zero if any REAL missing reference is found (suitable for CI / gates).
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

# Strip fenced code blocks before link/ref extraction (code is not doc prose).
FENCE = re.compile(r"```.*?```", re.S)
# markdown links: ](target)
LINK_RE = re.compile(r"\]\(s*([^)\s]+?)s*\)")
# backtick path token, optionally preceded by a capitalized foreign-brand word.
TICK_RE = re.compile(
    r"(?:(?P<brand>[A-Z][A-Za-z]+)\s+)?"
    r"`(?P<tok>"
    r"(?:references|templates|scripts|assets|reference)/[^\s`]+"
    r"|skills/[^\s`]+\.md"
    r"|/[^\s`]+\.md"
    r"|/[^\s`]+/SKILL\.md"
    r")`"
)
# tokens that are intentionally NOT catalog files (external tool / runtime artifact)
SKIP_EXTERNAL = (
    ".claude/", "copilot-instructions", "github.com", "githubusercontent",
    "anthropics", "localhost", "example.com",
)
SKIP_RUNTIME = (
    "/agents/issue-tracker.md", "/plan.md", "/todo.md", "/qa-project-context.md",
    "/ideas/", "/intent/", "/learning-records/", "/resources/", "/rules/",
    "/workflows", "/templates", "/MISSION-FORMAT", "/RESOURCES-FORMAT",
    "/LEARNING-RECORD-FORMAT",
)
IGNORE_PREFIX = ("http://", "https://", "mailto:")


def skill_dirs(base: Path):
    if not base.exists():
        return []
    return [p for p in base.iterdir() if p.is_dir() and (p / "SKILL.md").exists()]


def resolve(d: Path, tok: str, brand: str, store: Path, repo_docs: Path | None):
    """Return a Path if the token resolves, else None. None => skip (not a gap)."""
    tok = tok.split("#", 1)[0].strip().strip("`*").strip()
    if not tok or tok.startswith(IGNORE_PREFIX):
        return None
    # explicit external-tool / runtime-artifact skips
    if any(seg in tok for seg in SKIP_EXTERNAL):
        return None
    if any(seg in tok for seg in SKIP_RUNTIME):
        return None
    if "<" in tok or ">" in tok or "*" in tok or "?" in tok:
        return None  # placeholder / glob
    brand = brand or ""
    if brand and tok.startswith(("references/", "reference/", "assets/", "templates/", "scripts/")):
        # e.g. Allium `references/test-generation` -- external tool doc
        return None

    lead = tok.lstrip("/")
    # cross-skill pointer: skills/<name>/SKILL.md or /<name>/SKILL.md
    m = re.match(r"(?:skills/|^)([^/]+)/SKILL\.md$", lead)
    if m:
        return (store / m.group(1) / "SKILL.md") if (store / m.group(1) / "SKILL.md").exists() else None

    # repo-doc link: /docs/X.md
    if lead.startswith("docs/") and repo_docs is not None:
        cand = repo_docs / lead[len("docs/"):]
        if cand.exists():
            return cand

    # candidate bases for store-root-relative + skill-local refs
    bases = [store, d, d / "references", d / "resources", d / "rules", d / "reference"]
    for base in bases:
        cand = base / lead
        if cand.exists():
            return cand
    return None  # genuinely missing


def main() -> int:
    ap = argparse.ArgumentParser(description="Functional reference-integrity gate for a skill store.")
    ap.add_argument("store", type=Path, help="Skill store root (each subdir is a skill with SKILL.md).")
    ap.add_argument("--repo-docs", type=Path, default=None,
                    help="Repo docs/ dir, for resolving /docs/*.md links (optional).")
    args = ap.parse_args()
    store = args.store.resolve()
    repo_docs = args.repo_docs.resolve() if args.repo_docs else None

    dirs = skill_dirs(store)
    parse_fail = 0
    missing_keys = 0
    name_mismatch = 0
    candidates = 0
    present = 0
    missing = []  # (skill, raw, resolved_path_str)
    seen = set()

    for d in dirs:
        smd = d / "SKILL.md"
        try:
            text = smd.read_text(encoding="utf-8")
        except Exception:
            parse_fail += 1
            continue
        body = FENCE.sub("", text)
        # minimal frontmatter presence check (name/description)
        fm = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
        if fm:
            fm_text = fm.group(1)
            if "name:" not in fm_text or "description:" not in fm_text:
                missing_keys += 1
            nm = re.search(r"^name:\s*(.+)$", fm_text, re.M)
            if nm and nm.group(1).strip().strip('"\'') != d.name:
                name_mismatch += 1
        else:
            missing_keys += 1

        exts = []
        for m in LINK_RE.finditer(body):
            exts.append(m.group(1))
        for m in TICK_RE.finditer(body):
            exts.append(m.group("tok"))

        for raw in exts:
            if raw in seen:
                continue
            # brand capture for TICK only
            bm = TICK_RE.search("`" + raw + "`")
            brand = bm.group("brand") if bm else ""
            p = resolve(d, raw, brand, store, repo_docs)
            if p is None:
                continue
            seen.add(raw)
            candidates += 1
            if p.exists():
                present += 1
            else:
                missing.append((d.name, raw, str(p)))

    print(f"source         : {store}")
    print(f"skills         : {len(dirs)}")
    print(f"parse fail     : {parse_fail}")
    print(f"missing keys   : {missing_keys}")
    print(f"name!=folder   : {name_mismatch}")
    print(f"candidates chk : {candidates}")
    print(f"present refs   : {present}")
    print(f"MISSING refs   : {len(missing)}")
    if missing:
        print("--- MISSING (real gaps) ---")
        for s, raw, p in missing:
            print(f"  {s}: `{raw}`  ->  {p}")
        print("GATE: FAIL")
        return 1
    print("GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
