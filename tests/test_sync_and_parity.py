"""Tests for scripts/sync_global_to_repo.py (plan logic) and
scripts/check_skill_mirror_parity.py (check_parity logic).

These build SYNTHETIC skill trees in a temp dir, so they touch no real files
and need no restore. They assert:

  sync.plan():
    - shared skills with identical content -> to_update_identical (no-op)
    - global-only skill WITHOUT opt-in -> private_blocked (never exported)
    - global-only skill WITH opt-in (--import / --import-all / import.allow)
      -> to_add
    - differing skill (global != repo) -> to_skip_differ (not overwritten
      unless --force)
    - repo-only skill -> only_in_repo_left_untouched (never deleted: additive)

  check_parity():
    - identical trees -> no missing / extra / diffs
    - repo-only dir -> missing_in_global
    - global-only dir -> extra_in_global
    - same dir, differing file content -> content-mismatch
    - same dir, differing file set -> file-set-mismatch
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sync_global_to_repo as sync  # noqa: E402
import check_skill_mirror_parity as parity  # noqa: E402


def _make_skill(base: Path, name: str, content: str = "body\n"):
    d = base / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(content, encoding="utf-8")
    return d


class TestSyncPlan:
    def test_identical_shared_is_noop(self, tmp_path):
        g = _make_skill(tmp_path / "global", "foo", "same")
        r = _make_skill(tmp_path / "repo", "foo", "same")
        p = sync.plan(tmp_path / "global", tmp_path / "repo",
                      {"foo"}, {"foo"}, force=False, explicit_imports=[], import_all=False, allowed=[])
        assert p["to_update_identical"] == ["foo"]
        assert p["to_add"] == []
        assert p["private_blocked"] == []
        assert p["to_skip_differ"] == []

    def test_global_only_blocked_unless_optin(self, tmp_path):
        _make_skill(tmp_path / "global", "secret")
        p = sync.plan(tmp_path / "global", tmp_path / "repo",
                      {"secret"}, set(), force=False, explicit_imports=[], import_all=False, allowed=[])
        assert p["to_add"] == []
        assert p["private_blocked"] == ["secret"]

    def test_optin_via_import_flag(self, tmp_path):
        _make_skill(tmp_path / "global", "secret")
        p = sync.plan(tmp_path / "global", tmp_path / "repo",
                      {"secret"}, set(), force=False, explicit_imports=["secret"], import_all=False, allowed=[])
        assert p["to_add"] == ["secret"]
        assert p["private_blocked"] == []

    def test_optin_via_import_all(self, tmp_path):
        _make_skill(tmp_path / "global", "secret")
        _make_skill(tmp_path / "global", "secret2")
        p = sync.plan(tmp_path / "global", tmp_path / "repo",
                      {"secret", "secret2"}, set(), force=False, explicit_imports=[], import_all=True, allowed=[])
        assert sorted(p["to_add"]) == ["secret", "secret2"]

    def test_optin_via_allow_set(self, tmp_path):
        _make_skill(tmp_path / "global", "secret")
        # import.allow opt-ins arrive as the `allowed` arg to plan() (wired in
        # main() via allowed_imports()). The script never auto-publishes a
        # global-only skill unless it appears in that set.
        p = sync.plan(tmp_path / "global", tmp_path / "repo",
                      {"secret"}, set(), force=False, explicit_imports=[],
                      import_all=False, allowed={"secret"})
        assert p["to_add"] == ["secret"]
        assert p["private_blocked"] == []

    def test_differing_is_skipped_not_overwritten(self, tmp_path):
        _make_skill(tmp_path / "global", "foo", "global-version")
        _make_skill(tmp_path / "repo", "foo", "repo-version")
        p = sync.plan(tmp_path / "global", tmp_path / "repo",
                      {"foo"}, {"foo"}, force=False, explicit_imports=[], import_all=False, allowed=[])
        assert p["to_skip_differ"] == ["foo"]
        assert p["to_add"] == []
        # With --force it is still NOT reclassified into to_add (apply loop
        # handles differing via to_skip_differ), so plan stays additive/safe.
        p2 = sync.plan(tmp_path / "global", tmp_path / "repo",
                       {"foo"}, {"foo"}, force=True, explicit_imports=[], import_all=False, allowed=[])
        assert p2["to_skip_differ"] == ["foo"]

    def test_repo_only_never_deleted(self, tmp_path):
        _make_skill(tmp_path / "repo", "local-extra")
        p = sync.plan(tmp_path / "global", tmp_path / "repo",
                      set(), {"local-extra"}, force=False, explicit_imports=[], import_all=False, allowed=[])
        assert p["only_in_repo_left_untouched"] == ["local-extra"]


class TestCheckParity:
    def test_identical_trees(self, tmp_path):
        _make_skill(tmp_path / "global", "a", "x")
        _make_skill(tmp_path / "repo", "a", "x")
        missing, extra, diffs = parity.check_parity(tmp_path / "repo", tmp_path / "global")
        assert missing == [] and extra == [] and diffs == []

    def test_repo_only_dir(self, tmp_path):
        _make_skill(tmp_path / "repo", "a", "x")
        (tmp_path / "global").mkdir(parents=True, exist_ok=True)
        missing, extra, diffs = parity.check_parity(tmp_path / "repo", tmp_path / "global")
        assert missing == ["a"]
        assert extra == []
        assert diffs == []

    def test_global_only_dir(self, tmp_path):
        (tmp_path / "repo").mkdir(parents=True, exist_ok=True)
        _make_skill(tmp_path / "global", "a", "x")
        missing, extra, diffs = parity.check_parity(tmp_path / "repo", tmp_path / "global")
        assert missing == []
        assert extra == ["a"]
        assert diffs == []

    def test_content_mismatch(self, tmp_path):
        _make_skill(tmp_path / "global", "a", "global")
        _make_skill(tmp_path / "repo", "a", "repo")
        missing, extra, diffs = parity.check_parity(tmp_path / "repo", tmp_path / "global")
        assert missing == [] and extra == []
        assert len(diffs) == 1
        assert diffs[0][0] == "a" and diffs[0][1] == "content-mismatch"

    def test_file_set_mismatch(self, tmp_path):
        d = _make_skill(tmp_path / "global", "a", "x")
        (d / "extra.txt").write_text("more", encoding="utf-8")
        _make_skill(tmp_path / "repo", "a", "x")
        missing, extra, diffs = parity.check_parity(tmp_path / "repo", tmp_path / "global")
        assert len(diffs) == 1
        assert diffs[0][1] == "file-set-mismatch"
