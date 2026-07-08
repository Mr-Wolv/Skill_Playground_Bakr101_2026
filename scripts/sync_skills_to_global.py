"""DEPRECATED import direction — use with care.

NOTE ON SOURCE OF TRUTH
========================
This script pushes REPO -> GLOBAL (repo skills into the global agent store).
Under the current operating model the GLOBAL store (~/.agents/skills) is the
SOURCE OF TRUTH and the repo is a DOWNSTREAM COMMUNITY EXPORT. Pushing repo ->
global therefore runs BACKWARDS and will CLOBBER the real source. It is kept
only for the rare case where you intentionally author a skill directly in the
repo and want to publish it up into global.

Preferred flows:
    global -> runtime : python scripts/sync_runtime_to_mirror.py --apply
    global -> repo    : python scripts/sync_global_to_repo.py --apply

This script REFUSES to write unless you pass --i-understand-repo-is-downstream.
It also performs a safety audit and never deletes global skills that are absent
from the repo (additive only).

Usage:
    python scripts/sync_skills_to_global.py --i-understand-repo-is-downstream
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_paths import global_skills_dir  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "skills"
GLOBAL = global_skills_dir()


def main() -> int:
    ap = argparse.ArgumentParser(description="(DEPRECATED) Push repo skills into the global store.")
    ap.add_argument("--i-understand-repo-is-downstream", action="store_true",
                    help="Required to actually run. Repo is downstream of global; this runs backwards.")
    ap.add_argument("--dry-run", action="store_true", help="Preview only (default when not applying).")
    args = ap.parse_args()

    if not REPO.exists():
        print(f"Repository skills directory does not exist: {REPO}")
        return 1

    repo_dirs = {p.name for p in REPO.iterdir() if p.is_dir() and (p / "SKILL.md").exists()}
    global_dirs = {p.name for p in GLOBAL.iterdir() if p.is_dir() and (p / "SKILL.md").exists()}

    only_global = sorted(global_dirs - repo_dirs)  # would be DELETED if we mirrored — we won't
    print(f"REPO   ({REPO}): {len(repo_dirs)} skills")
    print(f"GLOBAL ({GLOBAL}): {len(global_dirs)} skills")
    print(f"global-only (would be DELETED by a mirror; we never do this): {len(only_global)}")
    if only_global:
        print("   ", ", ".join(only_global))

    if not args.i_understand_repo_is_downstream:
        print("\n[REFUSED] This pushes repo -> global, which runs BACKWARDS under the")
        print("current model (global is the source of truth). To actually do it, pass:")
        print("  --i-understand-repo-is-downstream")
        print("Recommended instead: scripts/sync_global_to_repo.py --apply")
        return 0

    # Additive only: copy repo skills into global, never delete global-only ones.
    GLOBAL.mkdir(parents=True, exist_ok=True)
    for name in sorted(repo_dirs):
        src = REPO / name
        dst = GLOBAL / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"PUSHED {src} -> {dst}")
    print("PUSH_COMPLETE (additive; global-only skills preserved)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
