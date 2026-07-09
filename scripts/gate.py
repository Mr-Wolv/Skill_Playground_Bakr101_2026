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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


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
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    print(f"--- {label}: {'PASS' if rc == 0 else 'FAIL (rc=%d)' % rc} ---")
    if not required and rc != 0:
        print(f"    (non-blocking in this environment: {label} skipped/optional)")
    return rc if required else 0


def main() -> int:
    steps = [
        ("pytest regression", ["uv", "run", "--offline", "--no-sync", "--with", "pytest", "pytest", "-q"],
         True),  # always required (pure repo-internal)
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
