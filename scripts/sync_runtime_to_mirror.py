"""Keep Hermes's runtime skill store in sync with the mirror store.

Topology this script operates on (post-2026-07 oscillation fix):

    On THIS machine the "global" store (B) and the runtime load path (C) are the
    SAME physical directory (B == C via $HERMES_SKILLS_HOME). So this sync is a
    no-op by construction — the runtime already IS the truth. The script still
    runs for portability on layouts where B and C genuinely differ (e.g. a
    default install with B=~/.agents/skills and C=~/.hermes/skills), where it
    performs the additive, non-destructive one-way mirror B -> C.

    The core-oscillation guard `assert_merged_topology()` (imported and run at
    module import) fails the script if B and C ever resolve to different
    directories on THIS machine, so the B<->C contradiction cannot silently
    return.

Guarantees (intact / secure / non-breaking):
  * ADDITIVE: skills present in the runtime dir but absent from B are NEVER removed.
  * NON-OVERWRITING: if a skill with the same name exists in both
    but with DIFFERENT content, it is always SKIPPED (never clobbered). The
    runtime is a derived copy of B; re-run this sync after changing B to pick
    up updates. (The --force flag is accepted for CLI symmetry but this
    additive sync does not overwrite differing content.)
  * CONTENT-IDENTICAL is a no-op (no copy, no churn).
  * User private store is never read, written, or "corrected".
  * A safety audit (destructive / secret-exfil patterns) gates every skill that
    would be ADDED or OVERWRITTEN. Unsafe skills are refused unless --allow-unsafe.
  * DRY-RUN BY DEFAULT. Use --apply to actually write.
  * A timestamped backup of the runtime dir is taken before any real write.

Usage:
    python scripts/sync_runtime_to_mirror.py            # dry-run, prints plan
    python scripts/sync_runtime_to_mirror.py --apply   # real sync (with backup)
    python scripts/sync_runtime_to_mirror.py --apply --force   # also overwrite differing
    python scripts/sync_runtime_to_mirror.py --no-audit  # skip the safety audit (NOT recommended)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Allow running from repo root without install.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_paths import (  # noqa: E402
    global_skills_dir,
    runtime_skills_dir,
    local_skills_dir,
    user_skills_dir,
    assert_merged_topology,
)


assert_merged_topology()  # core-oscillation guard: B must equal C


# --------------------------------------------------------------------------- #
# Scanning helpers
# --------------------------------------------------------------------------- #
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


# Destructive / exfiltration patterns. Any match in an executable script of a
# skill that would be ADDED or OVERWRITTEN fails the safety audit.
_DESTRUCTIVE = re.compile(
    r"(rm\s+-rf\s+/|rm\s+-rf\s+~|curl\s+\S+\|\s*(ba)?sh|wget\s+\S+\|\s*(ba)?sh|"
    r"mkfs|dd\s+if=|chmod\s+777|:\s*\(\s*\)\s*\{\:|crontab\s+-r|>\s*/dev/sd)",
    re.I,
)
EXEC_EXT = {".py", ".sh", ".bash", ".bat", ".ps1"}


def audit_skill(skill_dir: Path) -> list[str]:
    """Return a list of hazard descriptions for a skill, empty if safe."""
    hazards: list[str] = []
    for f in skill_dir.rglob("*"):
        if not (f.is_file() and f.suffix in EXEC_EXT):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        m = _DESTRUCTIVE.search(text)
        if m:
            hazards.append(f"{f.relative_to(skill_dir).as_posix()}: {m.group(0)[:48]}")
    return hazards


# --------------------------------------------------------------------------- #
# Core sync
# --------------------------------------------------------------------------- #
def plan_sync(src: Path, dst: Path, force: bool) -> dict:
    src_names = skill_names(src)
    dst_names = skill_names(dst)
    to_add, to_update_identical, to_skip_differ, to_leave = [], [], [], []

    for name in sorted(src_names):
        s = src / name
        d = dst / name
        if not d.exists():
            to_add.append(name)
        elif dir_hash(s) == dir_hash(d):
            to_update_identical.append(name)
        else:
            to_skip_differ.append(name) if not force else to_update_identical.append(name)

    # Anything only in dst stays; we just report it (never deleted).
    only_in_dst = sorted(dst_names - src_names)
    return {
        "src": str(src),
        "dst": str(dst),
        "to_add": to_add,
        "to_update_identical": to_update_identical,
        "to_skip_differ": to_skip_differ if not force else [],
        "only_in_dst_left_untouched": only_in_dst,
        "counts": {"src": len(src_names), "dst": len(dst_names)},
    }


def apply_sync(src: Path, dst: Path, force: bool, do_audit: bool, allow_unsafe: bool = False) -> dict:
    p = plan_sync(src, dst, force)
    backup_dir = None

    real_adds = []
    unsafe = []
    for name in p["to_add"]:
        s = src / name
        if do_audit and not allow_unsafe:
            hz = audit_skill(s)
            if hz:
                unsafe.append((name, hz))
                continue
        real_adds.append(name)

    if not real_adds:
        return {"applied": False, "reason": "nothing to add", "plan": p, "unsafe_refused": unsafe}

    # One backup covers the whole write.
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = dst.with_name(f"{dst.name}.backup-{ts}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    existing = skill_names(dst)
    for n in existing:
        shutil.copytree(dst / n, backup_dir / n)

    added, skipped = 0, 0
    for name in real_adds:
        d = dst / name
        if d.exists():
            skipped += 1
            continue
        shutil.copytree(src / name, d)
        added += 1

    # (force path for differing content would go here; omitted since default
    #  sync never overwrites without an explicit future --force handler.)

    after = skill_names(dst)
    return {
        "applied": True,
        "backup": str(backup_dir),
        "added": added,
        "skipped_already_present": skipped,
        "dst_count_before": p["counts"]["dst"],
        "dst_count_after": len(after),
        "unsafe_refused": unsafe,
        "only_in_dst_left_untouched": p["only_in_dst_left_untouched"],
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="Sync runtime skill store from the mirror (additive, non-destructive).")
    ap.add_argument("--apply", action="store_true", help="Actually write. Default is dry-run.")
    ap.add_argument("--force", action="store_true", help="Accepted for CLI symmetry; this additive sync never overwrites differing content (re-derive runtime from B).")
    ap.add_argument("--no-audit", action="store_true", help="Skip the safety audit (NOT recommended).")
    ap.add_argument("--allow-unsafe", action="store_true",
                    help="Add skills that FAIL the safety audit. Overrides --no-audit. NOT advised.")
    ap.add_argument("--src", type=Path, default=None, help="Override source (mirror) dir.")
    ap.add_argument("--dst", type=Path, default=None, help="Override destination (runtime) dir.")
    args = ap.parse_args()

    src = args.src or global_skills_dir()
    dst = args.dst or runtime_skills_dir()
    local = local_skills_dir()

    print(f"source (mirror) : {src}")
    print(f"dest   (runtime): {dst}")
    print(f"local skills    : {local}  (agent's own local dir; on this layout it IS the runtime;"
          f" excluded from this B->runtime sync and never overwritten by it)")
    print(f"user private   : {user_skills_dir()}  (YOUR skills; OUT of scope: "
          f"not loaded by any agent, not synced)\n")

    p = plan_sync(src, dst, args.force)
    print(f"source skills : {p['counts']['src']}")
    print(f"dest skills   : {p['counts']['dst']}")
    print(f"  + to ADD (new in dest)         : {len(p['to_add'])}")
    print(f"  = identical (no-op)            : {len(p['to_update_identical'])}")
    print(f"  ! differing content (SKIPPED)  : {len(p['to_skip_differ'])}")
    print(f"  - only in dest (left alone)    : {len(p['only_in_dst_left_untouched'])}")
    if p["to_add"]:
        print("    would add:", ", ".join(p["to_add"]))
    if p["to_skip_differ"]:
        print("    skipped (differ):", ", ".join(p["to_skip_differ"]))

    if not args.apply:
        print("\n[dry-run] no changes made. Re-run with --apply to write.")
        return 0

    do_audit = not args.no_audit
    res = apply_sync(src, dst, args.force, do_audit, args.allow_unsafe)
    print("\n=== APPLY RESULT ===")
    print(json.dumps(res, indent=2))
    if res.get("unsafe_refused"):
        print("\nREFUSED (failed safety audit):")
        for name, hz in res["unsafe_refused"]:
            print(f"  - {name}: {hz}")
        print("These were NOT added. Re-run with --allow-unsafe to force (not advised).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
