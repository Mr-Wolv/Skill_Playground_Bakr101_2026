"""Standard maintenance shortcut.

Operating model (source of truth = GLOBAL store):
    GLOBAL (~/.agents/skills)  = source of truth (curated across agents)
      |-- sync_runtime_to_mirror.py --> MY RUNTIME (~/.hermes/skills)
      |-- sync_global_to_repo.py    --> REPO (community export, downstream)

This shortcut runs the two downstream syncs (dry-run safe by default for the
push steps unless you pass --apply) then validates the catalog and parity.

It does NOT run the deprecated sync_skills_to_global.py (repo->global), which
runs backwards and clobbers the source.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script_name: str, *extra) -> int:
    script_path = ROOT / "scripts" / script_name
    print(f"RUNNING {script_path}")
    result = subprocess.run([sys.executable, str(script_path), *extra], cwd=ROOT)
    return result.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync downstream from global + validate catalog.")
    ap.add_argument("--apply", action="store_true", help="Actually apply the downstream syncs (else dry-run).")
    args = ap.parse_args()

    flags = ["--apply"] if args.apply else []

    for script_name in (
        "sync_runtime_to_mirror.py",
        "sync_global_to_repo.py",
    ):
        code = run(script_name, *flags)
        if code != 0:
            print(f"FAILED {script_name} ({code})")
            return code

    for script_name in (
        "validate_catalog.py",
        "check_skill_mirror_parity.py",
    ):
        code = run(script_name)
        if code != 0:
            print(f"FAILED {script_name} ({code})")
            return code

    print("SYNC_AND_VALIDATE_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
