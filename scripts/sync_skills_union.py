"""Bidirectional union sync between the local repo skills/ and the global
agent skill store.

Privacy model (important — this repo is public):
  The global store may contain PRIVATE or experimental skills that live only on
  your machine and are NOT meant to be published. Therefore global-only skills
  are treated as PRIVATE BY DEFAULT. Union will never copy a global-only skill
  into this repo unless you explicitly opt in, by one of:
    - listing it in scripts/import.allow (one name per line, # comments ok), or
    - passing --import <name> (repeatable), or
    - --import-all (bulk import everything — use only when you mean to publish).

  On conflicts between repo and global copies, the repo wins by default
  (repo is source of truth); pass --global-wins to prefer the global copy.

Union NEVER deletes anything. It only adds/updates skill directories and (when
importing) records the opt-in name in skills.json under an "imported" bucket so
the validator stays green — but only for skills you explicitly approved.

Run with --dry-run to see exactly what would change without writing.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

from skill_paths import global_skills_dir

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "skills"
GLOBAL = global_skills_dir()
ALLOW_FILE = ROOT / "scripts" / "import.allow"
IMPORTED_BUCKET = "imported"


def skill_hash(dir_: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(dir_.rglob("*")):
        if p.is_file():
            h.update(p.relative_to(dir_).as_posix().encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def skill_dirs(base: Path):
    return {p.name for p in base.iterdir() if p.is_dir() and (p / "SKILL.md").exists()}


def load_allow() -> set:
    if not ALLOW_FILE.exists():
        return set()
    names = set()
    for line in ALLOW_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.add(line)
    return names


def load_manifest():
    if not (ROOT / "skills.json").exists():
        return None
    return json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))


def save_manifest(data):
    (ROOT / "skills.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def extract_name(skill_dir: Path) -> str:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return skill_dir.name


def record_import(manifest, name):
    """Record an explicitly-approved import in skills.json under 'imported'."""
    if manifest is None:
        return False
    categories = manifest.setdefault("categories", {})
    bucket = categories.setdefault(IMPORTED_BUCKET, [])
    if name in bucket:
        return False
    bucket.append(name)
    all_names = {n for arr in categories.values() for n in arr}
    manifest["total_skills"] = len(all_names)
    manifest["custom_skills"] = len(all_names)
    if "community_skills" in manifest:
        manifest["community_skills"] = manifest["total_skills"] - manifest["custom_skills"]
    return True


def copy_dir(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> int:
    ap = argparse.ArgumentParser(description="Bidirectional union sync of skills.")
    ap.add_argument("--global-wins", action="store_true",
                    help="On content conflict, prefer the global copy instead of the repo copy.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report what would change without writing anything.")
    ap.add_argument("--import", dest="import_names", action="append", default=[],
                    help="Explicitly import a global-only skill by name (repeatable). "
                         "Overrides the private-by-default gate.")
    ap.add_argument("--import-all", action="store_true",
                    help="Import ALL global-only skills. Use only when you intend to publish them.")
    args = ap.parse_args()

    if not REPO.exists():
        print(f"Repository skills directory does not exist: {REPO}")
        return 1
    GLOBAL.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest()
    repo_dirs = skill_dirs(REPO)
    global_dirs = skill_dirs(GLOBAL)

    both = sorted(repo_dirs & global_dirs)
    repo_only = sorted(repo_dirs - global_dirs)
    global_only = sorted(global_dirs - repo_dirs)

    allowed = load_allow() | set(args.import_names)
    if args.import_all:
        allowed |= set(global_only)

    pushed = updated = skipped = conflicts = 0
    imported = private_blocked = []
    cataloged = []

    # Common: resolve by content hash
    for name in both:
        rh = skill_hash(REPO / name)
        gh = skill_hash(GLOBAL / name)
        if rh == gh:
            skipped += 1
            continue
        conflicts += 1
        src = (GLOBAL / name) if args.global_wins else (REPO / name)
        dst = (GLOBAL / name) if args.global_wins else (REPO / name)
        if args.dry_run:
            print(f"CONFLICT {name} -> would copy {'global' if args.global_wins else 'repo'} wins")
            continue
        copy_dir(src, dst)
        copy_dir(src, (REPO / name) if args.global_wins else (GLOBAL / name))
        updated += 1
        print(f"MERGED {name} ({'global' if args.global_wins else 'repo'} wins)")

    # Repo-only -> push to global (public repo -> global is fine)
    for name in repo_only:
        if args.dry_run:
            print(f"PUSH {name} -> global")
            pushed += 1
            continue
        copy_dir(REPO / name, GLOBAL / name)
        pushed += 1
        print(f"PUSHED {name} -> global")

    # Global-only -> PRIVATE BY DEFAULT. Import only if explicitly allowed.
    for name in global_only:
        if name in allowed:
            if args.dry_run:
                print(f"IMPORT {name} -> repo (approved)")
                imported.append(name)
                continue
            copy_dir(GLOBAL / name, REPO / name)
            imported.append(name)
            print(f"IMPORTED {name} -> repo (approved)")
            real = extract_name(REPO / name) or name
            if record_import(manifest, real):
                cataloged.append(real)
                print(f"CATALOGED {real} under '{IMPORTED_BUCKET}'")
        else:
            private_blocked.append(name)
            print(f"PRIVATE (skipped) {name} -> not in repo. Opt in via scripts/import.allow or --import {name}")

    if cataloged and not args.dry_run and manifest is not None:
        save_manifest(manifest)
        print(f"MANIFEST updated: total_skills={manifest['total_skills']}, "
              f"custom_skills={manifest['custom_skills']}, imported={len(cataloged)}")

    if private_blocked and not args.dry_run:
        print(f"\nNOTE: {len(private_blocked)} global-only skill(s) left PRIVATE "
              f"(not copied into this public repo):")
        for n in private_blocked:
            print(f"  - {n}")
        print("To import one intentionally: add it to scripts/import.allow, "
              "or run with --import <name>.")

    print("UNION_SYNC_COMPLETE")
    print(f"skipped {skipped}")
    print(f"conflicts_resolved {conflicts}")
    print(f"pushed {pushed}")
    print(f"imported {len(imported)}")
    print(f"private_blocked {len(private_blocked)}")
    print(f"auto_cataloged {len(cataloged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
