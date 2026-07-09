# Cheap stub snapshot + surgical file restore (kill the per-trial copytree)

## Problem
A whole-catalog PROPERTY FUZZ mutated the real repo to prove a validator can't
be silently fooled. The naive version did, per trial:

```python
shutil.copytree(ROOT, dst, ignore=...)   # FULL real 241-skill tree
vc.validate(dst)
```

Cost: ~4.6s per copytree × 53 trials ≈ 411s. The suite became unusable.

## Fix
Snapshot the catalog CHEAPLY once, then reuse ONE materialized copy and only
revert the bytes each operator actually touched.

### 1. Build a tiny template (session fixture)
Only the fields the validator reads:
- `skills.json` (verbatim)
- one STUB `SKILL.md` per skill = FRONTMATTER ONLY (what `validate` parses):
  ```python
  def _frontmatter_only(text):
      m = re.match(r"^---\n.*?\n---\n?", text, re.DOTALL)
      return m.group(0) if m else "---\nname: unknown\ndescription: stub\n---\n"
  ```
- the N docs the validator reads (copied verbatim; small)
- NO full bodies, NO fenced blocks, NO extra files

Template build ~0.5s; one materialized stub copy ~0.9s.

### 2. Surgical restore (reuse one materialized root across all trials)
```python
class _Restore:
    def __init__(self, root): self.root = root; self._saved = {}
    def touch(self, rel):
        p = self.root / rel
        self._saved[str(p)] = p.read_bytes() if p.exists() else None
    def add_dir(self, rel): self._saved["__dir__" + str(self.root / rel)] = True
    def restore(self):
        for key, data in self._saved.items():
            if key.startswith("__dir__"): continue
            p = Path(key)
            if data is None:
                if p.exists(): p.unlink()
            else:
                p.write_bytes(data)
        for key in list(self._saved):
            if key.startswith("__dir__"):
                d = Path(key[len("__dir__"):])
                if not d.exists(): d.mkdir(parents=True, exist_ok=True)
```
Each operator calls `restore.touch(...)` (or `restore.add_dir(...)` for dir
add/delete) BEFORE mutating; after `validate()`, call `restore.restore()`.

### 3. Reuse one root, don't recopy
```python
root = _materialize(template, tmp_path / "cs")   # ONCE
restore = _Restore(root)
for trial in range(40):
    op(root, random.Random(trial), restore)
    result = vc.validate(root)
    restore.restore()
```

## Result
411s → 8s, identical coverage. Full suite 57 passed in ~20s (was ~450s).

## Structural guard so it can't regress
```python
class TestSnapshotIsCheap:
    def test_template_excludes_full_skill_tree(self, template):
        total = sum(p.stat().st_size for p in template.rglob("*") if p.is_file())
        assert total < 5 * 1024 * 1024, "template too big — not the cheap stub form"
    def test_each_skill_is_frontmatter_only(self, template):
        for p in (template / "skills").glob("*/SKILL.md"):
            b = p.read_text()
            assert b.lstrip().startswith("---") and "```" not in b
```

## General rule
If a fixture is large, SNAPSHOT IT CHEAPLY and MUTATE-IN-PLACE with surgical
restore. Never copytree the real tree per trial — it's the silent 400s tax.
