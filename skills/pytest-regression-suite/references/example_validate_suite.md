# Example: validate(root) + hermetic pytest

## scripts/validate_catalog.py (core)
```python
import json, re
from pathlib import Path

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def validate(root: Path) -> list[str]:
    """Return validation errors (empty == PASS). All paths derive from `root`."""
    errors: list[str] = []
    skills = root / "skills"
    names = []
    for f in sorted(skills.glob("*/SKILL.md")):
        m = re.search(r"^name:\s*(.+)$", read_text(f), re.M)
        if m:
            names.append(m.group(1).strip())
    fs = sorted(set(names))
    # ... checks append to errors via errors.append(...) ...
    return errors
```

## tests/conftest.py
```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
```

## tests/test_catalog.py (hermetic: mutate real file, assert, restore)
```python
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_catalog as vc

def _patch(path, old, new, count=1):
    t = path.read_text(encoding="utf-8")
    assert old in t, f"anchor missing in {path.name}"
    rep = t.replace(old, new) if count == 0 else t.replace(old, new, count)
    path.write_text(rep, encoding="utf-8")

def test_committed_tree_passes(repo):
    assert vc.validate(repo) == []

def test_label_drift_fails(repo):
    cat = repo / "SKILL-CATALOG.md"
    orig = cat.read_bytes()
    try:
        _patch(cat, "| `x` | **custom** |", "| `x` | community |")
        assert any("missing custom label for `x`" in e for e in vc.validate(repo))
    finally:
        cat.write_bytes(orig)
```

## pyproject.toml
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["scripts"]
addopts = "-q"
```

## Run
```
uv run --with pytest pytest
```
