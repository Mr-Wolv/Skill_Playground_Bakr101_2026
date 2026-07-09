# Example: synthetic-tree tests for path-parameterized sync/parity scripts

Use this pattern when the script under test exposes a PURE function that takes
two `Path` trees (not a single `root` like a catalog validator). No real files
are touched and no `try/finally` restore is needed — each test builds its own
`tmp_path` trees.

## scripts/sync_global_to_repo.py (core: pure plan())
```python
def plan(global_base, repo_base, global_names, repo_names,
         force, explicit_imports, import_all, allowed):
    to_add, to_update_identical, to_skip_differ = [], [], []
    private_blocked = []
    explicit = (set(explicit_imports)
                | (global_names if import_all else set())
                | set(allowed))
    for name in sorted(global_names):
        g = global_base / name
        r = repo_base / name
        if not r.exists():
            (to_add if name in explicit else private_blocked).append(name)
        elif dir_hash(g) == dir_hash(r):
            to_update_identical.append(name)
        else:
            to_skip_differ.append(name)   # differing: kept in repo, not overwritten
    only_repo = sorted(repo_names - global_names)
    return {"to_add": to_add, "to_update_identical": to_update_identical,
            "to_skip_differ": to_skip_differ, "private_blocked": private_blocked,
            "only_in_repo_left_untouched": only_repo}
```

## scripts/check_skill_mirror_parity.py (core: pure check_parity())
```python
def check_parity(repo_root: Path, global_root: Path):
    repo_dirs = {p.name for p in repo_root.iterdir() if p.is_dir()}
    global_dirs = {p.name for p in global_root.iterdir() if p.is_dir()}
    missing_in_global = sorted(repo_dirs - global_dirs)
    extra_in_global = sorted(global_dirs - repo_dirs)
    diffs = []
    for name in sorted(repo_dirs & global_dirs):
        rfiles = list_files(repo_root / name)
        gfiles = list_files(global_root / name)
        if rfiles != gfiles:
            diffs.append((name, "file-set-mismatch", rfiles, gfiles))
            continue
        for rel in rfiles:
            if sha256(repo_root / name / rel) != sha256(global_root / name / rel):
                diffs.append((name, "content-mismatch", rel))
                break
    return missing_in_global, extra_in_global, diffs
```

## tests/conftest.py
```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
```

## tests/test_sync_and_parity.py
```python
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sync_global_to_repo as sync
import check_skill_mirror_parity as parity


def _make_skill(base: Path, name: str, content: str = "body\n"):
    d = base / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(content, encoding="utf-8")
    return d


class TestSyncPlan:
    def test_identical_shared_is_noop(self, tmp_path):
        _make_skill(tmp_path / "global", "foo", "same")
        _make_skill(tmp_path / "repo", "foo", "same")
        p = sync.plan(tmp_path / "global", tmp_path / "repo",
                      {"foo"}, {"foo"}, force=False, explicit_imports=[],
                      import_all=False, allowed=[])
        assert p["to_update_identical"] == ["foo"]

    def test_global_only_blocked_unless_optin(self, tmp_path):
        _make_skill(tmp_path / "global", "secret")
        p = sync.plan(tmp_path / "global", tmp_path / "repo",
                      {"secret"}, set(), force=False, explicit_imports=[],
                      import_all=False, allowed=[])
        assert p["private_blocked"] == ["secret"]

    def test_optin_via_allow_set(self, tmp_path):
        _make_skill(tmp_path / "global", "secret")
        p = sync.plan(tmp_path / "global", tmp_path / "repo",
                      {"secret"}, set(), force=False, explicit_imports=[],
                      import_all=False, allowed={"secret"})
        assert p["to_add"] == ["secret"]


class TestCheckParity:
    def test_repo_only_dir(self, tmp_path):
        _make_skill(tmp_path / "repo", "a", "x")
        (tmp_path / "global").mkdir(parents=True, exist_ok=True)
        missing, extra, diffs = parity.check_parity(tmp_path / "repo", tmp_path / "global")
        assert missing == ["a"] and extra == [] and diffs == []

    def test_global_only_dir(self, tmp_path):
        (tmp_path / "repo").mkdir(parents=True, exist_ok=True)
        _make_skill(tmp_path / "global", "a", "x")
        missing, extra, diffs = parity.check_parity(tmp_path / "repo", tmp_path / "global")
        assert missing == [] and extra == ["a"] and diffs == []

    def test_content_mismatch(self, tmp_path):
        _make_skill(tmp_path / "global", "a", "global")
        _make_skill(tmp_path / "repo", "a", "repo")
        missing, extra, diffs = parity.check_parity(tmp_path / "repo", tmp_path / "global")
        assert diffs and diffs[0][1] == "content-mismatch"
```

## Run
```
uv run --with pytest pytest
```

## Notes
- Both roots must exist before calling `check_parity` (a missing dir raises
  `FileNotFoundError` on `.iterdir()`). Create an empty root with
  `mkdir(parents=True, exist_ok=True)` even when one side has no skills.
- Pass the opt-in set explicitly as `allowed=` rather than monkeypatching the
  module's `ALLOW_FILE` global — it makes the test assert the real contract.
