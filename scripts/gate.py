#!/usr/bin/env python3
"""gate.py — single mechanical entrypoint enforcing repo coherence.

Runs every standing QC gate in order and exits non-zero on the first failure.
Used by CI (tests.yml) and the local pre-commit hook so the SAME gate runs in
both places — coherence, persistence and completeness are enforced by the
toolchain, not by a human re-checking.

Gates:
  1. pytest regression suite (catalog + sync/parity + QC dives)
  2. validate_catalog.py        (structural coherence)
  3. check_skill_mirror_parity.py (repo <-> B mirror integrity)
  4. deep_audit.py climb --strict (0 CRITICAL, 0 new/un-reviewed WARN)
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

# Hard ceiling so a flaky package-manager network call (uv trying to reach
# the index) can NEVER hang a commit indefinitely. The gate is repo-internal
# and hermetic; if a tool can't run offline within this window the step is
# reported as a failure rather than blocking the commit forever.
STEP_TIMEOUT = int(__import__("os").environ.get("GATE_STEP_TIMEOUT", "600"))


def _store_present() -> bool:
    # Mirror parity compares the repo against the LOCAL catalog B
    # (~/.agents/skills), which only exists on the curator's machine — NOT in
    # CI or a fresh checkout. Surface that honestly instead of failing CI.
    try:
        import skill_paths  # local import; keeps gate importable anywhere
        return skill_paths.global_skills_dir().exists()
    except Exception:
        return False


def _run(label: str, cmd: list[str], required: bool = True) -> int:
    print(f"\n=== GATE: {label} ===")
    try:
        proc = subprocess.run(cmd, cwd=ROOT, timeout=STEP_TIMEOUT)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT after {STEP_TIMEOUT}s — gate step could not complete")
        rc = 1
    print(f"--- {label}: {'PASS' if rc == 0 else 'FAIL (rc=%d)' % rc} ---")
    if not required and rc != 0:
        print(f"    (non-blocking in this environment: {label} skipped/optional)")
    return rc if required else 0


def _pytest_cmd() -> list[str]:
    """pytest invocation, hermetic either way.

    pytest is a locked dev dependency (dependency-groups.dev in pyproject.toml,
    pinned in uv.lock). We run it via `uv run [--offline] pytest` — NEVER
    `uv run --with pytest`, which re-resolves the wheel from the network on
    every call and hangs on flaky connections. The dev group is installed once
    via `uv sync --dev`; after that offline is hermetic and instant.

    On GitHub Actions the runner is fresh (no uv cache yet) but HAS network,
    so we allow online resolution there; locally we go offline to avoid the hang.
    """
    offline = not __import__("os").environ.get("GITHUB_ACTIONS")
    cmd = ["uv", "run"]
    if offline:
        cmd += ["--offline", "--no-sync"]
    cmd += ["pytest", "-q"]
    return cmd


def _merged_store_guard() -> int:
    """Belt-and-suspenders: assert the merged-store invariant at commit time.

    Calls scripts/check_merged_topology.py, which only FAILS loudly where the
    merged invariant is SUPPOSED to hold (HERMES_SKILLS_HOME set — i.e. this
    machine). On CI / a fresh checkout HERMES_SKILLS_HOME is unset so it is a
    no-op (CI stays the independent auditor). This is the local-commit layer that
    makes a B<->C split structurally impossible to commit silently.
    """
    return _run(
        "merged-store guard (B == C)",
        [sys.executable, str(SCRIPTS / "check_merged_topology.py")],
        True,
    )


def main() -> int:
    # Merged-store (oscillation-nuke) guard first. Self-skips in CI / when
    # HERMES_SKILLS_HOME is unset; fails loud where the invariant must hold.
    if _merged_store_guard() != 0:
        print("\nGATE FAILED — commit blocked (merged-store guard).")
        return 1
    steps = [
        ("pytest regression", _pytest_cmd(), True),  # always required (pure repo-internal)
        ("catalog coherence", [sys.executable, str(SCRIPTS / "validate_catalog.py")],
         True),  # always required (pure repo-internal)
        ("mirror parity", [sys.executable, str(SCRIPTS / "check_skill_mirror_parity.py")],
         _store_present()),  # only meaningful where local catalog B exists
        ("compositional climb --strict",
         [sys.executable, str(SCRIPTS / "deep_audit.py"), "climb", "--strict"],
         True),  # repo-internal coherence (topology self-skips when B absent)
    ]
    failed = 0
    for label, cmd, required in steps:
        if required or _store_present():
            if _run(label, cmd, required) != 0:
                failed += 1
                break  # stop at first failure; report which gate
        else:
            print(f"\n=== GATE: {label} ===\n    SKIPPED — local catalog B absent "
                  f"(~/.agents/skills); repo<->catalog parity is a local-machine "
                  f"concern and is not validated in CI/a fresh checkout.\n")
    if failed:
        print("\nGATE FAILED — commit blocked. Fix the failing gate above.")
        return 1
    print("\nALL GATES PASS — coherence, persistence and completeness enforced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
