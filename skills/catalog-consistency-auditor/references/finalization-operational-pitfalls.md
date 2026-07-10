# Finalization Operational Pitfalls — ADDITIVE detail

Companion to `convergence-audit-recipe.md` and the SKILL.md "Operational pitfalls"
section. Holds ONLY the detail NOT already in SKILL.md: the `*.backup-*` junk the
convergence syncs leave, and the background-commit + CI-watch tail of the
finalization sequence. The `--force` silent-no-op, parity-as-separate-gate,
test-corruption hazard, and reload no-op all live in SKILL.md — do not duplicate.

## A. `*.backup-*` junk from the convergence syncs (cleanup + commit hygiene)
- `sync_global_to_repo.py --apply` and `sync_runtime_to_mirror.py --apply` write
  `skills.backup-<ts>/` (repo root) and `skills/.../*.backup/` dirs as a safety net.
- `.gitignore` has `*.backup-*/`, so they are NEVER committed. But they clutter the
  tree. **Never `git add -A`** during finalization — stage explicit paths so a stray
  backup dir (or an unwanted report `.md`) can't slip in.
- To delete leftover temp dirs (e.g. pytest `tmp_path` copies that include read-only
  `.venv`): `rm -rf` hits "Permission denied" on Windows read-only files. Use Python:
  `shutil.rmtree(p, onerror=lambda f,path,err: (os.chmod(path, stat.S_IWRITE), f(path)))`,
  run it in the BACKGROUND (it can take minutes over old `.venv` copies).

## B. Background-commit + CI-watch tail (the part of the sequence SKILL.md omits)
The pre-commit hook re-runs `gate.py` (~35–120s on the full tree). A foreground
`git commit` inside a 60s terminal times out and aborts — changes stay staged but
uncommitted. So:
1. Stage explicit paths (see A).
2. Commit in the BACKGROUND with `notify_on_complete=true`; poll until it prints the
   new SHA. The hook's `ALL GATES PASS` in the commit output IS the success signal.
3. `git push origin main`.
4. Monitor CI — this repo has THREE workflows on push:
   - `Validate Catalog` (`validate.yml`)
   - `Regression Suite` (`tests.yml`)
   - `Mirror Parity Guidance` (`mirror-parity.yml`)
   Get run IDs: `gh run list --limit 5 --json databaseId,workflowName,status,conclusion`.
   Watch each: `gh run watch <id> --exit-status` (returns non-zero if the run failed).
   Only declare "completely finished" when ALL THREE show `success`.
