"""CI / pre-commit belt-and-suspenders check for the merged store topology.

On THIS machine the shared catalog (B = global_skills_dir) and Hermes's
runtime load path (C = runtime_skills_dir) MUST be the SAME physical
directory. The oscillation was structurally nuked by junctioning
~/.agents/skills -> <LOCALAPPDATA>/hermes/skills, so B resolves into C at the
filesystem level — independent of any env var, surviving reboot.

This script is the independent second layer:
  - It asserts B == C (resolved) whenever we are NOT in CI / a fresh checkout.
  - In CI (GITHUB_ACTIONS/CI set) it is a no-op, because CI runs on a
    different OS where the Windows junction does not exist and the merged
    invariant is NOT expected — CI's validate.yml / mirror-parity.yml remain
    the independent auditor there.

If a future change ever splits B and C again (e.g. the junction is removed),
this fails LOUD so the regression cannot be committed or merged silently.

Exit codes: 0 = merged & verified (or intentionally skipped in CI), 1 = split.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
import skill_paths as sp  # noqa: E402

# Only meaningful locally. In CI the junction does not exist and the merged
# invariant is not expected; skip so CI stays the independent auditor.
if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
    print("[SKIP] CI / GitHub Actions -> merged-store invariant not expected "
          "here. No-op.")
    sys.exit(0)

if not sp.global_skills_dir().exists():
    # Local machine but no local catalog B present (fresh checkout on a dev
    # box) -> nothing to assert against. Not a split; skip.
    print("[SKIP] local catalog B absent -> merged-store invariant not "
          "applicable here. No-op.")
    sys.exit(0)

try:
    sp.assert_merged_topology()
except AssertionError as e:
    print("[FAIL] MERGED-STORE INVARIANT BROKEN:", e, file=sys.stderr)
    sys.exit(1)

b, c = sp.global_skills_dir(), sp.runtime_skills_dir()
print("[OK] merged-store invariant holds:")
print("  B =", b)
print("  C =", c)
print("  resolved-identical:", b.resolve() == c.resolve())
