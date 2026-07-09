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


def _run(label: str, cmd: list[str]) -> int:
    print(f"\n=== GATE: {label} ===")
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    print(f"--- {label}: {'PASS' if rc == 0 else 'FAIL (rc=%d)' % rc} ---")
    return rc


def main() -> int:
    steps = [
        ("pytest regression", ["uv", "run", "--with", "pytest", "pytest", "-q"]),
        ("catalog coherence", [sys.executable, str(SCRIPTS / "validate_catalog.py")]),
        ("mirror parity", [sys.executable, str(SCRIPTS / "check_skill_mirror_parity.py")]),
        ("compositional climb --strict",
         [sys.executable, str(SCRIPTS / "deep_audit.py"), "climb", "--strict"]),
    ]
    failed = 0
    for label, cmd in steps:
        if _run(label, cmd) != 0:
            failed += 1
            break  # stop at first failure; report which gate
    if failed:
        print("\nGATE FAILED — commit blocked. Fix the failing gate above.")
        return 1
    print("\nALL GATES PASS — coherence, persistence and completeness enforced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
