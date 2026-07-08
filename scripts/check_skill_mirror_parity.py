import hashlib
import sys
from pathlib import Path

from skill_paths import global_skills_dir

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "skills"
GLOBAL = global_skills_dir()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def list_files(root: Path):
    return sorted(
        p.relative_to(root).as_posix() for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    )


def check_parity(repo_root: Path, global_root: Path):
    """Compare two skill trees; return (missing_in_global, extra_in_global, diffs).

    missing_in_global : skill dirs present in repo but absent from global
    extra_in_global   : skill dirs present in global but absent from repo
    diffs             : per-skill (name, kind, ...) where kind is
                        "file-set-mismatch" or "content-mismatch"
    Pure (no printing) so it is unit-testable against synthetic trees.
    """
    repo_dirs = {p.name for p in repo_root.iterdir() if p.is_dir()}
    global_dirs = {p.name for p in global_root.iterdir() if p.is_dir()}

    missing_in_global = sorted(repo_dirs - global_dirs)
    extra_in_global = sorted(global_dirs - repo_dirs)
    diffs = []

    for name in sorted(repo_dirs & global_dirs):
        rdir = repo_root / name
        gdir = global_root / name
        rfiles = list_files(rdir)
        gfiles = list_files(gdir)
        if rfiles != gfiles:
            diffs.append((name, "file-set-mismatch", rfiles, gfiles))
            continue
        for rel in rfiles:
            if sha256(rdir / rel) != sha256(gdir / rel):
                diffs.append((name, "content-mismatch", rel))
                break

    return missing_in_global, extra_in_global, diffs


def main() -> int:
    if not REPO.exists():
        print(f"Repository skills directory does not exist: {REPO}")
        return 1
    if not GLOBAL.exists():
        print(f"Global skills directory does not exist: {GLOBAL}")
        return 1

    missing_in_global, extra_in_global, diffs = check_parity(REPO, GLOBAL)

    print(f"repo_root {REPO}")
    print(f"global_root {GLOBAL}")
    print(f"repo_dirs {len({p.name for p in REPO.iterdir() if p.is_dir()})}")
    print(f"global_dirs {len({p.name for p in GLOBAL.iterdir() if p.is_dir()})}")
    print(f"missing_in_global {len(missing_in_global)}")
    if missing_in_global:
        print(missing_in_global)
    print(f"extra_in_global {len(extra_in_global)}")
    if extra_in_global:
        print(extra_in_global)
    print(f"diff_count {len(diffs)}")
    for item in diffs[:100]:
        print(item)

    if missing_in_global or extra_in_global or diffs:
        return 1

    print("FULL_MIRROR_PARITY_CONFIRMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
