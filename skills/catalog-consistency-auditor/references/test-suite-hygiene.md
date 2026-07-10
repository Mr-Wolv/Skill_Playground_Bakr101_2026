# Test-suite hygiene — make corruption structurally impossible

A convergence pass triggers the QC suite, which historically mutated shared root
files IN PLACE (`skills.json`, `SKILL-CATALOG.md`) to exercise drift checks. If a
test failed mid-run, its restore was skipped and the tree stayed dirty — cascading
false failures into sibling tests. That is a HAZARD: a "green" gate depended on
cleanup that might never run.

User mandate that governs this: **hazards > anything; be fool-proof; do not sleep on
a hazard.** So the durable fix is to ELIMINATE the hazard, not to recover from it.

## The fix (fool-proof by construction)

Tests run against a THROWAWAY COPY of the repo, never the real tree. The committed
tree is then physically impossible to corrupt — a timeout, Ctrl-C, or teardown error
cannot leave a dirty file. This is the pattern now in `tests/test_validate_catalog.py`:

```python
import json, sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_catalog as vc

# Dirs never copied into a scratch repo (disk-exhaustion hazard on a 240-skill tree).
_EXCLUDE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".venv-cache"}

def _copytree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for child in src.iterdir():
        name = child.name
        if child.is_dir():
            if name in _EXCLUDE_DIRS or name.endswith(".backup"):
                continue
            _copytree(child, dst / name)
        else:
            if name.endswith(".backup"):
                continue
            (dst / name).write_bytes(child.read_bytes())

@pytest.fixture
def scratch(tmp_path):
    """Validate() runs against a throwaway COPY; the real tree is never touched."""
    dst = tmp_path / "repo"
    _copytree(ROOT, dst)
    vc.ROOT = dst          # keep error-message relative paths coherent
    yield dst
    vc.ROOT = ROOT

def _load_sj(scratch): return json.loads((scratch/"skills.json").read_text())
def _write_sj(scratch, data):
    # preserve canonical formatting — never collapse json.dumps(data) with no indent
    (scratch/"skills.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
```

Properties that make it safe:
- **No shared-file mutation.** Every `_patch` / `_write_sj` targets `scratch/...`, not `ROOT/...`.
- **No `try/finally` restore of shared files** — there is nothing to restore.
- **Format-preserving writes** (`indent=2`), so even a scratch copy stays valid JSON.
- **Excludes disk-hogs** (`.venv`/`.git`/`*.backup-*`). Copying the whole repo incl.
  `.venv` causes `OSError: [Errno 28] No space left on device` — skip those dirs.
- **Immune to validator file-list drift** — copies the whole repo (minus exclusions),
  so adding a doc the validator reads won't silently break the test.

## If you inherit the OLD design (recovery path)

Only relevant if a test still mutates the real tree. Symptom: a failure like
`anchor not found in SKILL-CATALOG.md: '| Custom skills | 1 |'`, or `skills.json`
reads `"custom_skills": 1` while the catalog says 65, or `git diff skills.json` shows
the whole file collapsed to one line. This is corruption from a PRIOR run, not your code.

Recovery (canonical, idempotent — do NOT hand-edit literals):
1. `python scripts/refresh_derived_catalog.py --apply`  # rebuilds skills.json + prose from disk
2. `python scripts/refresh_derived_catalog.py --check`  # -> CONSISTENT
3. Re-run the FULL suite on the healed tree; if it passes, the earlier failures were corruption.

## Proof the hazard is gone

After rewriting the suite, run it and hash the real root files before/after:
```python
import hashlib, pathlib, subprocess
files = ["skills.json","SKILL-CATALOG.md","README.md","SKILL.md","SKILL-CATALOG-DOMAIN.md"]
before = {f: hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest() for f in files}
subprocess.run([".venv/Scripts/python","-m","pytest","-q","-p","no:cacheprovider",
                "tests/test_validate_catalog.py"], capture_output=True, text=True, timeout=300)
after = {f: hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest() for f in files}
assert all(before[f]==after[f] for f in files), "REAL TREE CORRUPTED"
```
All five must be byte-identical. If they are, the suite is fool-proof.

## Rule of thumb

After ANY change, before trusting a test failure as "your bug", run `git diff --stat`
for UNEXPECTED root-doc / skills.json edits. If found and you didn't make them, heal
with `refresh --apply` first, then re-test. But the real goal is to never be in that
state: make the bad state impossible, don't recover from it.
