import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "skills"
GLOBAL = Path(r"C:\Users\GIGABYTE\.agents\skills")


def main() -> int:
    if not REPO.exists():
        print(f"Repository skills directory does not exist: {REPO}")
        return 1
    GLOBAL.mkdir(parents=True, exist_ok=True)
    repo_dirs = {p.name for p in REPO.iterdir() if p.is_dir()}
    global_dirs = {p.name for p in GLOBAL.iterdir() if p.is_dir()}

    removed = sorted(global_dirs - repo_dirs)
    added_or_updated = sorted(repo_dirs)

    for name in removed:
        target = GLOBAL / name
        if target.exists():
            shutil.rmtree(target)
            print(f"REMOVED {target}")

    for name in added_or_updated:
        source = REPO / name
        target = GLOBAL / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        print(f"SYNCED {source} -> {target}")

    print("SYNC_COMPLETE")
    print(f"repo_root {REPO}")
    print(f"global_root {GLOBAL}")
    print(f"removed {len(removed)}")
    print(f"synced {len(added_or_updated)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
