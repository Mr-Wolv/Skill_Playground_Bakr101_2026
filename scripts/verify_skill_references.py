#!/usr/bin/env python3
"""Functional integrity gate for the skill store.

Resolves every internal file reference in each skill's SKILL.md against the
filesystem and reports missing files. Catches references in BOTH markdown
links ](target) AND backtick code-span path tokens (references/, templates/,
scripts/, assets/, reference/, cross-skill skills/<name>/SKILL.md, and
leading-slash /OtherSkill/SKILL.md). Fenced code blocks are stripped first so
embedded code identifiers (e.g. `operand`) are not mistaken for paths.

Discriminator for external-tool docs: a backtick token like
`references/foo` is treated as THIS skill's own file UNLESS the word
immediately before the backtick is a capitalized foreign brand (e.g.
"the Allium `references/test-generation`" — Allium is an external tool whose
own docs live outside this store). assets/scripts/templates are always ours,
so they are never excluded by this rule.

This is the "skills are usable, not just coherent" gate. Run it on the source
of truth, the runtime store, and the repo copy; all three must read clean.

Usage:
    python scripts/verify_skill_references.py [STORE_ROOT]
    (default STORE_ROOT = ~/.agents/skills)

Exit code 0 = no missing references; 1 = gaps found.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except Exception:
    yaml = None

FENCE   = re.compile(r"```.*?```", re.S)
LINK_RE = re.compile(r"\]\(\s*([^)\s]+?)\s*\)")
# backtick path token, optionally preceded by a capitalized foreign-brand word.
# Named groups: 'brand' (optional) and 'tok' (the path).
TICK_RE = re.compile(
    r"(?:(?P<brand>[A-Z][A-Za-z]+)\s+)?"             # optional brand word
    r"`"
    r"(?P<tok>"
    r"(?:references|templates|scripts|assets|reference)/[^\s`]+"
    r"|skills/[^\s`]+\.md"
    r"|/[^\s`]+\.md"
    r")"
    r"`"
)
IGNORE_PREFIX = ("google/", "github.com/", "http", "mailto:")


def resolve(d: Path, tgt: str, brand: str):
    tgt = tgt.split("#", 1)[0].strip().strip("`*").strip()
    if not tgt or tgt.startswith(IGNORE_PREFIX):
        return None
    # Literal placeholders in docs (e.g. `skills/<name>/SKILL.md`) are not real paths.
    if "<" in tgt or ">" in tgt:
        return None
    # External-tool docs: `references/...` owned by a foreign brand (not this skill).
    if brand and tgt.startswith("references/") and brand != d.name.replace("-", " ").title().replace(" ", ""):
        return None
    if tgt.startswith(("http://", "https://", "mailto:")):
        return None
    if tgt.startswith("/"):
        return (SRC / tgt.lstrip("/")).resolve()
    # Cross-skill pointers like `skills/<name>/SKILL.md` resolve against the store root.
    if tgt.startswith("skills/"):
        return (SRC / tgt[len("skills/"):]).resolve()
    return (d / tgt).resolve()


def main():
    global SRC
    root = sys.argv[1] if len(sys.argv) > 1 else None
    SRC = Path(root) if root else (Path.home() / ".agents" / "skills")

    total = parse_fail = missing_keys = name_mm = 0
    candidates = []
    seen = set()
    for d in sorted(SRC.iterdir()):
        if not d.is_dir():
            continue
        sk = d / "SKILL.md"
        if not sk.exists():
            print(f"  NO SKILL.md: {d.name}"); continue
        total += 1
        text = sk.read_text(encoding="utf-8", errors="replace")
        text = FENCE.sub("", text)
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
        if not m:
            print(f"  NO FRONTMATTER: {d.name}"); parse_fail += 1; continue
        fm, body = m.group(1), m.group(2)
        data = {}
        if yaml:
            try:
                data = yaml.safe_load(fm) or {}
            except Exception:
                print(f"  YAML FAIL: {d.name}"); parse_fail += 1; continue
        else:
            for ln in fm.splitlines():
                if ":" in ln:
                    k, v = ln.split(":", 1); data[k.strip()] = v.strip().strip('"')
        if [k for k in ("name", "description") if not data.get(k)]:
            print(f"  MISSING KEYS: {d.name}"); missing_keys += 1
        if data.get("name") and data.get("name") != d.name:
            print(f"  NAME!=FOLDER: {d.name}"); name_mm += 1
        for raw in LINK_RE.findall(text):
            p = resolve(d, raw, "")
            if p is not None and (d.name, p) not in seen:
                seen.add((d.name, p)); candidates.append((d.name, raw, p))
        for m2 in TICK_RE.finditer(text):
            brand, tok = m2.group("brand"), m2.group("tok")
            p = resolve(d, tok, brand or "")
            if p is not None and (d.name, p) not in seen:
                seen.add((d.name, p)); candidates.append((d.name, tok, p))

    missing = [(s, raw, p) for (s, raw, p) in candidates
               if p is not None and not p.exists()]
    present = sum(1 for (_, _, p) in candidates if p is not None and p.exists())

    print(f"source         : {SRC}")
    print(f"skills         : {total}")
    print(f"parse fail     : {parse_fail}")
    print(f"missing keys   : {missing_keys}")
    print(f"name!=folder   : {name_mm}")
    print(f"candidates chk : {len(candidates)}")
    print(f"present refs   : {present}")
    print(f"MISSING refs   : {len(missing)}")
    for s, raw, p in missing:
        print(f"  MISSING {s}: {raw}  ->  {p}")
    if missing or parse_fail or missing_keys or name_mm:
        print("GATE: FAIL")
        raise SystemExit(1)
    print("GATE: PASS")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
