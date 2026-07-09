"""Deep catalog-coherence audit (deterministic probe, no mutation).

Run a one-pass cross-file reconciliation of a skill repo:
  - skills.json union == real skill directories (no orphans, no phantoms)
  - custom/community split has no overlap and matches the on-disk set
  - SKILL-CATALOG.md per-row labels == json custom set (both directions)
  - SKILL-CATALOG-DOMAIN.md domain tables == json custom set
  - SKILL.md / README / cheatsheet references all resolve to real skills
  - no orphan skills (every disk skill documented somewhere)

This is the "QA senior engineer deep scan" recipe. It mirrors the checks that
validate_catalog.py enforces, but recomputes them INDEPENDENTLY (not via the
gate) so it can catch a gate that itself drifted. Exit 0 = coherent.

Usage:
    python scripts/catalog_coherence_audit.py [--root DIR]
"""
import json
import re
import sys
from pathlib import Path

SKILL_RE = r"`([a-z][a-z0-9_-]+)`"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def audit(root: Path) -> list[str]:
    errs: list[str] = []
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return [f"no skills/ dir at {skills_dir}"]

    fs = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())
    fs_set = set(fs)

    data = json.loads(_read(root / "skills.json"))
    custom = set(s for arr in data.get("categories", {}).values() for s in arr)
    comm = set(data.get("community_skill_names", []))
    union = custom | comm

    if len(union) != len(fs_set):
        errs.append(f"union size {len(union)} != disk {len(fs_set)}")
    if fs_set - union:
        errs.append(f"on disk but not custom|community: {sorted(fs_set - union)}")
    if union - fs_set:
        errs.append(f"in manifest but not on disk: {sorted(union - fs_set)}")
    if custom & comm:
        errs.append(f"custom/community overlap: {sorted(custom & comm)}")

    # SKILL-CATALOG.md per-row labels
    cat = _read(root / "SKILL-CATALOG.md")
    rows = re.findall(r"^\|\s*`([a-z0-9_-]+)`\s*\|\s*(?:\*\*custom\*\*|custom)\s*\|",
                      cat, re.M)
    cat_custom = set(rows)
    if cat_custom != custom:
        errs.append(f"catalog custom labels != json custom: "
                    f"only-in-catalog={sorted(cat_custom - custom)} "
                    f"only-in-json={sorted(custom - cat_custom)}")
    cat_refs = set(re.findall(SKILL_RE, cat))
    if cat_refs - fs_set:
        errs.append(f"catalog refs missing on disk: {sorted(cat_refs - fs_set)}")

    # SKILL-CATALOG-DOMAIN.md domain tables (exclude the meta-skills prose block)
    dom = _read(root / "SKILL-CATALOG-DOMAIN.md")
    meta_block = dom.split("## 🤖 Meta-Skills", 1)[1] if "## 🤖 Meta-Skills" in dom else ""
    dom_refs = set(re.findall(SKILL_RE, dom))
    dom_tables = dom_refs - set(re.findall(SKILL_RE, meta_block))
    if dom_tables != custom:
        errs.append(f"domain tables != json custom: "
                    f"only-in-domain={sorted(dom_tables - custom)} "
                    f"only-in-json={sorted(custom - dom_tables)}")

    # SKILL.md representative skills are PLAIN-TEXT comma-separated cells
    skill_md = _read(root / "SKILL.md")
    rep = set()
    for ln in skill_md.splitlines():
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0].startswith("Category"):
            continue
        for tok in re.split(r",\s*", cells[1]):
            tok = tok.strip().strip("`")
            if re.fullmatch(r"[a-z][a-z0-9_-]+", tok):
                rep.add(tok)
    if rep - fs_set:
        errs.append(f"SKILL.md rep refs missing on disk: {sorted(rep - fs_set)}")

    # README: only table rows name skills (avoids fence/prose false positives)
    readme = _read(root / "README.md")
    readme_rows = "\n".join(l for l in readme.splitlines() if l.strip().startswith("|"))
    if set(re.findall(SKILL_RE, readme_rows)) - fs_set:
        errs.append(f"README table refs missing on disk: "
                    f"{sorted(set(re.findall(SKILL_RE, readme_rows)) - fs_set)}")

    # cheatsheet
    cheat = _read(root / "SDLC-PHRASE-CHEATSHEET.md")
    if set(re.findall(SKILL_RE, cheat)) - fs_set:
        errs.append(f"cheatsheet refs missing on disk: "
                    f"{sorted(set(re.findall(SKILL_RE, cheat)) - fs_set)}")

    # orphan: every disk skill must appear in json OR a doc backtick ref
    mentioned = union | cat_refs | dom_refs | set(re.findall(SKILL_RE, skill_md)) \
        | set(re.findall(SKILL_RE, readme)) | set(re.findall(SKILL_RE, cheat))
    if fs_set - mentioned:
        errs.append(f"orphan skills (on disk, documented nowhere): "
                    f"{sorted(fs_set - mentioned)}")

    return errs


if __name__ == "__main__":
    root = Path(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else Path.cwd()
    errs = audit(root.resolve())
    if errs:
        print("COHERENCE FAILED")
        for e in errs:
            print(f"- {e}")
        sys.exit(1)
    print("COHERENCE OK — catalog, manifest, and docs are mutually consistent")
