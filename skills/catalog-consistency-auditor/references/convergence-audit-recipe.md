# Convergence Audit Recipe (scripted checks)

Reusable Python snippets for the convergence-audit pass. Drop into a temp script in the
repo root and run with `python`. All read-only; nothing is modified.

## 0. Ground truth first
Run the repo's own gate; report its result verbatim as evidence the mechanical layer is
green (convergence defects live in prose docs, not the validator):

```bash
uv run --with pytest pytest        # or: python scripts/gate.py
python scripts/validate_catalog.py
python scripts/check_skill_mirror_parity.py
```

## 1. Source-of-truth contradiction check
```python
import re, pathlib
docs = ["docs/catalog-governance.md", "AGENTS.md", "README.md", "docs/index.md"]
for p in docs:
    txt = pathlib.Path(p).read_text(encoding="utf-8")
    hits = re.findall(r"source of truth[^.\n]*", txt, flags=re.I)
    print(p, "->", hits[:3])
```
Flag if the named authoritative directory differs across docs (e.g. `skills/` vs
`~/.agents/skills`).

## 2. Prose-count lint
```python
import json, re, pathlib
folders = [d for d in os.listdir("skills") if os.path.isdir(f"skills/{d}")]
n = len(folders)
print("folder count:", n)
for md in list(pathlib.Path(".").glob("*.md")) + list(pathlib.Path("docs").glob("*.md")):
    for m in re.findall(r"\b(\d{2,3})\s*(?:skills|custom|community)",
                        md.read_text(encoding="utf-8", errors="ignore")):
        if int(m) != n and int(m) not in (64, 176):  # tolerate the legit 64/176 split
            print("DRIFT", md, m)
sj = json.loads(pathlib.Path("skills.json").read_text())
assert sj["total_skills"] == n, (sj["total_skills"], n)
```

## 3. Cross-artifact token cross-reference
```python
import os, re, pathlib
from collections import Counter
folders = set(d for d in os.listdir("skills") if os.path.isdir(f"skills/{d}"))
def tokens(path):
    lines = pathlib.Path(path).read_text(encoding="utf-8").split("\n")
    out, fence = [], False
    for ln in lines:
        if ln.strip().startswith("```"):
            fence = not fence; continue
        if fence: continue
        out += re.findall(r"`([a-z0-9\-]+)`", ln)
    return Counter(out)
cat = tokens(pathlib.Path("SKILL-CATALOG.md"))
print("duplicates:", {k: v for k, v in cat.items() if v > 1})
print("orphans:", [s for s in cat if s not in folders])
print("missing from catalog:", [f for f in folders if f not in cat])
```

## 4. Placeholder-description finder
```python
import re, pathlib
for ln in pathlib.Path("SKILL-CATALOG.md").read_text(encoding="utf-8").split("\n"):
    if re.search(r"^\| `[a-z0-9-]+` \| (?:community|\*\*custom\*\*) \| [>~]", ln):
        print("PLACEHOLDER:", ln.strip())
```

## 5. Coverage gaps (no catalog row AND no cheatsheet trigger)
```python
import os, re, pathlib
folders = set(d for d in os.listdir("skills") if os.path.isdir(f"skills/{d}"))
mentioned = set(re.findall(r"`([a-z0-9\-]+)`",
    pathlib.Path("SKILL-CATALOG.md").read_text() + pathlib.Path("SDLC-PHRASE-CHEATSHEET.md").read_text()))
print("undiscoverable (no catalog row, no cheatsheet):",
      sorted(f for f in folders if f not in mentioned))
```

## Report shape (Version 1.0 Convergence Report)
Each finding: `impact`, `recommended action`, `priority` (P1/P2/P3), `architectural
justification`. End with a go/no-go on the "complete" claim. Findings are almost always
mechanical and low-risk; prefer a one-pass fix sequence ending in a green gate re-run.
