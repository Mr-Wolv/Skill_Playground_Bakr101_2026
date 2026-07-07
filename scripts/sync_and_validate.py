import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script_name: str) -> int:
    script_path = ROOT / "scripts" / script_name
    print(f"RUNNING {script_path}")
    result = subprocess.run([sys.executable, str(script_path)], cwd=ROOT)
    return result.returncode


def main() -> int:
    for script_name in (
        "sync_skills_to_global.py",
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
