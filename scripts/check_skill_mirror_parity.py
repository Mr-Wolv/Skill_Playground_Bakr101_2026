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


def skill_dirs(root: Path):
    """Recursively find skill directories (dirs containing SKILL.md) by basename.

    Layout-agnostic: Hermes runtimes may nest skills under category
    subfolders (e.g. engineering-mindset/compositional-deep-audit),
    while the shared catalog (B) and repo mirror (D) store them flat.
    A skill is identified by its basename so parity holds across both layouts.
    """
    return {p.parent.name for p in root.rglob("SKILL.md") if p.is_file()}


def check_parity(repo_root: Path, global_root: Path):
    """Compare two skill trees; return (missing_in_global, extra_in_global, diffs).

    missing_in_global : skill dirs present in repo but absent from global
    extra_in_global   : skill dirs present in global but absent from repo
    diffs             : per-skill (name, kind, ...) where kind is
                       "file-set-mismatch" or "content-mismatch"

    Pure (no printing) so it is unit-testable against synthetic trees.

    Semantics under the private-by-default union model (post-2026-07):
      * `missing_in_global` and `diffs` are the REAL oscillation signal.
        A repo skill absent from global, or differing in content, means the
        exported copy has diverged from the source of truth -> fail.
      * `extra_in_global` (global-only skills) are PRIVATE by default and are
        expected to be absent from the repo. They must NOT fail parity; the
        repo is a curated export, not a mirror of every private skill. The
        published subset is tracked separately via scripts/import.allow.
    """
    repo_dirs = skill_dirs(repo_root)
    global_dirs = skill_dirs(global_root)

    missing_in_global = sorted(repo_dirs - global_dirs)
    extra_in_global = sorted(global_dirs - repo_dirs)
    diffs = []

    for name in sorted(repo_dirs & global_dirs):
        # resolve the actual (possibly nested) dir for this basename
        rdir = next((p.parent for p in repo_root.rglob(f"{name}/SKILL.md")), repo_root / name)
        gdir = next((p.parent for p in global_root.rglob(f"{name}/SKILL.md")), global_root / name)
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

    if missing_in_global or diffs:
        return 1

    print("FULL_MIRROR_PARITY_CONFIRMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
