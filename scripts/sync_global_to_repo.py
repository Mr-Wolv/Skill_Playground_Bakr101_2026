"""Export the global skill store into this repository (global -> repo).

Source-of-truth model (per repo owner):
    GLOBAL (~/.agents/skills)  = source of truth, curated across multiple agents.
      |
      |  sync_global_to_repo.py   (this script — the EXPORT direction)
      v
    REPO   (D:/Skill-Playground/skills)  = community/localized export; downstream.

This is the OPPOSITE direction of the older `sync_skills_to_global.py`, which
pushed repo -> global. Under the current model that older script is unsafe
(clobbers the real source) and must only run when explicitly intended.

Guarantees (intact / secure / non-breaking):
  * ADDITIVE: skills present in the repo but ABSENT from global are NEVER
    removed from the repo (the community copy keeps its extras).
  * NON-OVERWRITING BY DEFAULT: if a skill exists in both but content DIFFERS,
    the repo copy is SKIPPED (repo keeps its version). Pass --force to overwrite
    the repo copy from global (backs up first).
  * PRIVATE BY DEFAULT: global-only skills (in global but not in repo) are
    NEVER copied into the repo unless opted in via scripts/import.allow,
    --import <name>, or --import-all. This prevents leaking private/experimental
    skills into a public repo.
  * Content-identical = no-op.
  * Dry-run by default. --apply to write. --apply takes a timestamped backup of
    any repo skill it would overwrite.
  * Portable paths (no hardcoded username) via scripts/skill_paths.py.

Usage:
    python scripts/sync_global_to_repo.py            # dry-run, shows plan
    python scripts/sync_global_to_repo.py --apply   # real export (with backup)
    python scripts/sync_global_to_repo.py --apply --force   # also overwrite differing
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_paths import global_skills_dir  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "skills"
GLOBAL = global_skills_dir()
ALLOW_FILE = ROOT / "scripts" / "import.allow"


def skill_names(base: Path) -> set[str]:
    if not base.exists():
        return set()
    return {p.name for p in base.iterdir() if p.is_dir() and (p / "SKILL.md").exists()}


def dir_hash(d: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(d.rglob("*")):
        if f.is_file():
            h.update(f.relative_to(d).as_posix().encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def allowed_imports() -> set[str]:
    if not ALLOW_FILE.exists():
        return set()
    out = set()
    for line in ALLOW_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(line)
    return out


def plan(global_base, repo_base, global_names, repo_names, force, explicit_imports, import_all):
    to_add, to_update_identical, to_skip_differ, to_leave_in_repo = [], [], [], []
    private_blocked = []  # global-only, not opted-in -> never exported
    explicit = set(explicit_imports) | (global_names if import_all else set())

    for name in sorted(global_names):
        g = global_base / name
        r = repo_base / name
        if not r.exists():
            if name in explicit:
                to_add.append(name)
            else:
                private_blocked.append(name)
        elif dir_hash(g) == dir_hash(r):
            to_update_identical.append(name)
        else:
            # Differing: keep listed as skipped (or overwritten under --force).
            # NOTE: do NOT reclassify into to_update_identical under --force,
            # or the apply loop (which only copies to_add and to_skip_differ)
            # would never actually export the new files.
            to_skip_differ.append(name)

    only_repo = sorted(repo_names - global_names)
    return {
        "to_add": to_add,
        "to_update_identical": to_update_identical,
        "to_skip_differ": to_skip_differ,
        "private_blocked": private_blocked,
        "only_in_repo_left_untouched": only_repo,
        "counts": {"global": len(global_names), "repo": len(repo_names)},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Export global skill store into this repo (global -> repo).")
    ap.add_argument("--apply", action="store_true", help="Actually write. Default is dry-run.")
    ap.add_argument("--force", action="store_true", help="Overwrite repo skills whose content differs (backs up first).")
    ap.add_argument("--import-all", action="store_true", help="Export ALL global-only skills (publish everything).")
    ap.add_argument("--import", dest="imports", action="append", default=[], help="Export a specific global-only skill (repeatable).")
    ap.add_argument("--src", type=Path, default=None, help="Override global dir.")
    ap.add_argument("--dst", type=Path, default=None, help="Override repo skills dir.")
    ap.add_argument("--check-completeness", action="store_true",
                    help="In dry-run, exit non-zero (2) if global has public skills not exported to repo.")
    args = ap.parse_args()

    global_base = args.src or GLOBAL
    repo_base = args.dst or REPO

    print(f"source (global): {global_base}")
    print(f"dest   (repo)  : {repo_base}")
    print("flow: GLOBAL -> REPO (export). Private global-only skills stay private unless opted in.\n")

    g_names, r_names = skill_names(global_base), skill_names(repo_base)
    p = plan(global_base, repo_base, g_names, r_names, args.force, args.imports, args.import_all)

    print(f"global skills : {p['counts']['global']}")
    print(f"repo skills   : {p['counts']['repo']}")
    print(f"  + to ADD into repo (opted-in)         : {len(p['to_add'])}")
    print(f"  = identical (no-op)                   : {len(p['to_update_identical'])}")
    print(f"  ! differing (SKIPPED unless --force)  : {len(p['to_skip_differ'])}")
    print(f"  * private global-only (NOT exported)  : {len(p['private_blocked'])}")
    print(f"  - only in repo (left alone)           : {len(p['only_in_repo_left_untouched'])}")
    if p["to_add"]:
        print("    would add:", ", ".join(p["to_add"]))
    if p["private_blocked"]:
        print("    private (blocked):", ", ".join(p["private_blocked"]))
    if p["to_skip_differ"]:
        print("    skipped (differ):", ", ".join(p["to_skip_differ"]))

    # Completeness signal: global has skills that are NOT in the repo AND NOT
    # opted in. Under the source-of-truth model these are public-but-unexported
    # skills — the repo is silently drifting out of completeness. Surface it.
    unexported = p["private_blocked"]  # global-only skills not opted in
    if unexported:
        print("\n!!! COMPLETENESS WARNING !!!")
        print(f"  {len(unexported)} global skill(s) are NOT in the repo and NOT opted in:")
        print("    " + ", ".join(unexported))
        print("  The repo is a point-in-time export; it will NOT contain these until you")
        print("  opt them in via scripts/import.allow (or --import/--import-all) and re-run --apply.")
        if args.check_completeness:
            print("  [--check-completeness] failing because the repo is incomplete vs global.")
            return 2

    if not args.apply:
        print("\n[dry-run] no changes made. Re-run with --apply to write.")
        return 0

    # Apply: copy opt-in adds + (if --force) differing overwrites with backup.
    added = skipped = 0
    backup_root = None
    if p["to_add"] or p["to_skip_differ"]:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_root = repo_base.with_name(f"{repo_base.name}.backup-{ts}")
        backup_root.mkdir(parents=True, exist_ok=True)
        for n in r_names:
            shutil.copytree(repo_base / n, backup_root / n)

    for name in p["to_add"]:
        src = global_base / name
        dst = repo_base / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        added += 1

    if args.force:
        for name in p["to_skip_differ"]:
            src = global_base / name
            dst = repo_base / name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            skipped += 1

    print("\n=== APPLY RESULT ===")
    print(json.dumps({
        "added_to_repo": added,
        "overwritten_with_force": skipped,
        "backup": str(backup_root) if backup_root else None,
        "private_blocked": len(p["private_blocked"]),
        "repo_extras_left_untouched": len(p["only_in_repo_left_untouched"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
