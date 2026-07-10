# AGENTS.md

## Mission

Treat this repository as a **living skill architecture** rather than a loose collection of prompts.

The goal is to improve the long-term engineering capability of the ecosystem, not to maximize the number of skills.

When working in this repo:

- optimize for **high cohesion** and **low coupling**
- avoid duplication, fragmentation, and capability inflation
- prefer reusable engineering concepts over narrow technology-specific skills
- treat `skills/` and `~/.agents/skills` as mirrored skill stores
- keep all repository documents consistent with the current catalog state

## Default Working Rules

Before creating or modifying a skill:

1. inspect existing skills for overlap
2. decide whether the need is best solved by:
   - enhancing an existing skill
   - splitting an overloaded skill
   - merging overlapping skills
   - adding a new skill only if it provides clear incremental value
3. update all affected documentation and indexes in the same change

## Skill Design Principles

Prefer skills that are:

- reusable
- composable
- narrowly focused
- discoverable
- maintainable
- well-scoped
- grounded in engineering workflows

Avoid:

- duplicate capabilities
- names that differ without meaningful scope differences
- technology-specific skills unless the domain knowledge is genuinely specialized
- creating new skills when a catalog/documentation change is the correct fix

## Repository Consistency Requirements

Whenever the skill catalog changes, keep these artifacts aligned:

- `skills/`
- `README.md`
- `SKILL.md`
- `SKILL-CATALOG.md`
- `SKILL-CATALOG-DOMAIN.md`
- `SDLC-PHRASE-CHEATSHEET.md` when triggers change
- `skills.json`
- `docs/index.md`
- `docs/catalog-governance.md`

If exact counts are mentioned anywhere, verify them from the actual directory contents instead of copying old numbers.

## Sync Model

This repo treats the following directories as a mirrored pair:

- workspace: `skills/` (this repo) — a downstream export of the global store
- global: the SHARED CATALOG — the single source of truth

**Topology (post-oscillation-fix, 2026-07):** on this machine the global
catalog is the SAME physical directory as Hermes's runtime load path. The
pointer `$HERMES_SKILLS_HOME` (set persistently in the Windows user environment,
inherited by the Hermes launcher) makes `global_skills_dir()` resolve to
`<LOCALAPPDATA>/hermes/skills` — i.e. B and C are one store. This is the core
fix for the B<->C oscillation: there is no second place for the truth to
diverge into. In CI / a fresh checkout `HERMES_SKILLS_HOME` is unset, so B
falls back to `~/.agents/skills` and CI remains an independent auditor against
the default global store (see `assert_merged_topology()` in `scripts/skill_paths.py`).

Parity means full folder contents, not only matching folder names.
The shared catalog is authoritative; `skills/` is derived from it.
Changes should preserve parity unless a task explicitly says otherwise.

After catalog-affecting work, run:

1. `python scripts/sync_global_to_repo.py`   # export global -> this repo (community copy)
2. `python scripts/validate_catalog.py`
3. `python scripts/check_skill_mirror_parity.py`

Or use the shortcut:

- `python scripts/sync_and_validate.py`

For the full mechanical QC gate (pytest + coherence + parity + strict
compositional climb), run `python scripts/gate.py` (also wired into CI and the
local pre-commit hook via `make install-hook`). The WARN tier is a hard 0/0
contract enforced by `scripts/warn_allowlist.json`; regenerate it with
`python scripts/deep_audit.py allowlist --write` after a human review of any
new finding.

## Skill Store Ownership & Boundaries

There are THREE skill stores that matter. Ownership and the load/sync rules for
each are fixed to remove ambiguity:

- **Shared catalog = runtime (ONE store).** Resolved by `global_skills_dir()` /
  `runtime_skills_dir()` in `scripts/skill_paths.py`. On this machine both
  resolve to `<LOCALAPPDATA>/hermes/skills` (via `$HERMES_SKILLS_HOME`), so the
  source of truth and Hermes's live load path are the SAME directory. Skills
  created via the agent's own tooling (`skill_manage`) land here too — which is
  correct, because here IS the truth. The merged invariant is enforced by
  `assert_merged_topology()`; the pre-commit gate fails loudly if B and C ever
  point at different directories again.
- **Public repo** `skills/` in this repo — a downstream export of the shared
  catalog. Never authoritative; never pushed back into the catalog.
- **Human private** `~/skills` — the human's own experiments, deliberately
  ASIDE from every agent: NOT in any agent load path, NOT synced, NOT read or
  written by Hermes or any other agent. Not part of the catalog.

The documented DEFAULT global (`~/.agents/skills`) is used only where
`$HERMES_SKILLS_HOME` is unset (CI, other machines). The repo's own QC is
portable and username-free.

Routing rule (no ambiguity):

- shared/curated skill -> the shared catalog, which IS the runtime on this
  machine. Write into it directly (file tools on the resolved dir, or
  `skill_manage` — both land in the same truth here).
- human private skill -> `~/skills` (never in any agent load path).
- The runtime is NOT a separate write target anymore; it is the truth itself.
- sync is additive, hash-detect-don't-overwrite, backup-before-write, private
  stores excluded.

The human owns the catalog; agents read and write into the single merged store.

## Documentation Style

- prefer clear operational language over marketing language
- be explicit about scope, source of truth, and maintenance rules
- do not leave stale counts or unsupported claims in docs
- when uncertain, state the current verified fact and note what still needs verification

## Capability Architecture Guidance

Catalog evolution should be driven by demonstrated capability gaps, architectural coherence, and long-term maintainability rather than expansion for its own sake.

When evaluating changes, ask:

- does this capability already exist?
- is it partially covered already?
- should the current capability be expanded instead?
- would a separate skill improve modularity or only add noise?
- does the change improve reuse, discoverability, maintainability, or engineering quality?

Only add new skills when the answer is materially yes.

## Evidence-Driven Refinement Policy

The highest-value boundary and coherence refactors have already been completed across the most overlapping skill clusters.

From here, prefer evidence-driven refinement over speculative cleanup. Use real project behavior to guide further changes. Strong evidence includes:

- repeated uncertainty about which skill should be used
- repeated invocation misses caused by naming or trigger ambiguity
- recurring overlap encountered during actual engineering tasks
- repeated user friction from unclear skill boundaries
- demonstrated capability gaps in real project work

Prefer this order:

1. use the catalog in real project work
2. observe where selection, invocation, or boundaries fail
3. refine the smallest set of skills that resolves the observed problem
4. stop when the practical confusion is gone

Do not continue boundary refactoring indefinitely for stylistic consistency alone.

## Expansion Control Policy

The catalog is now mature enough that net-new skill creation is no longer the default optimization path.

From this point onward, prefer the following order of operations:

1. improve an existing skill
2. improve naming, triggers, examples, or discoverability
3. split an overloaded skill if the boundaries are truly unclear
4. merge overlapping skills if duplication is diluting clarity
5. add a new skill only if the capability is both genuinely distinct and repeatedly valuable

A new skill should be added only when it clearly beats the alternatives above on:

- distinctness
- reuse
- discoverability
- maintainability
- engineering value

If the case is ambiguous, do not add the skill. Capture the gap and only act once repeated real usage demonstrates the need.

## Operational Notes (post-Convergence hard rules)

These are the durable, non-obvious lessons from the Convergence Initiative.
Violating any of them reintroduces the exact pain the initiative removed.

### Counts are DERIVED, never hand-edited

Every human-readable skill count (README/SKILL.md/SKILL-CATALOG.md prose,
the SKILL-CATALOG.md Summary row, `skills.json` numeric fields) is regenerated
by `scripts/refresh_derived_catalog.py` from the filesystem + `skills.json`.
The pre-commit hook runs `refresh --check` and SELF-HEALS (regenerates + stages)
if any artifact drifted. **Do not** hand-edit a count literal — it will be
overwritten on next commit, or (worse) if you bypass the hook, flagged by the
validator. To refresh manually: `make refresh`.

### The regression suite MUST stay fast

`tests/test_catalog_fuzz.py` (Dive 6) builds a CHEAP STUB snapshot (frontmatter-
only `SKILL.md` + the 7 docs + `skills.json`) and reuses ONE materialized copy
via surgical file restore. It must NEVER `copytree` the real 241-skill tree per
trial — that cost ~410s and made every verification unusable. `TestSnapshotIsCheap`
guards this structurally. Full suite target: **<60s** (currently ~20s). If it
regresses past ~60s, find the per-trial full-tree copy and kill it.

### Gate timing

`python scripts/gate.py` (the pre-commit gate) is ~35s: pytest ~20s + deep-audit
climb --strict ~13s + validate/parity ~2s. Not the old ~6 min. The slow part is
the deep-audit climb over all 241 skills, not the tests.

### Reload invariant (after catalog-affecting work)

After any change to `skills/` or the merged store, RELOAD Hermes and confirm the
skills load. The merged-store junction (`~/.agents/skills` -> `<LOCALAPPDATA>/hermes/skills`,
B==C) makes this safe and idempotent. `assert_merged_topology()` (in
`scripts/skill_paths.py`, run by the gate + CI) fails loudly if B and C ever
diverge — that is the core oscillation guard; do not remove it.

### Stale verification false-positives

The editor/system stale-check can report "No module named pytest" or flag
already-committed files as unverified. That snapshot is stale. The trusted
command is `.venv/Scripts/python -m pytest -q -p no:cacheprovider` (or
`python scripts/gate.py`). Trust the real run, not the stale banner.

### `--force` sync converges repo<-store

`scripts/sync_global_to_repo.py --force` overwrites repo skills whose content
differs from the store (backing up first). It only touches `skills/` dirs, not
root docs. Use it only to intentionally converge the repo export to the store;
never as a routine step (it can mask intended repo-only edits).

### `make` is absent on the Windows host

The Makefile targets (`make verify`, `make refresh`, `make check`, `make gate`,
`make install-hook`) are for CI / Linux. On this Windows MSYS box `make` is not
installed, so run the python invocations directly:
- full gate: `python scripts/gate.py`
- refresh counts: `python scripts/refresh_derived_catalog.py --apply`
- check counts: `python scripts/refresh_derived_catalog.py --check`
- install hook: `python -c "import shutil,pathlib;p=pathlib.Path('.git/hooks/pre-commit');shutil.copy('scripts/pre-commit.hook',p);p.chmod(0o755)"`

The Makefile now uses the locked `.venv` pytest path (not `uv run --with pytest`),
matching `gate.py` — so CI and local runs share one flake-free toolchain.

### The count generator CORRECTS drift, it does not just confirm

`refresh_derived_catalog.py` rewrites a drifted count to the derived value
(e.g. a stale `999 skills` -> `241 skills`), not only a no-op when already
correct. If a doc count ever disagrees with the filesystem, `refresh --apply`
fixes it and the pre-commit hook self-heals. `tests/test_refresh_counts.py`
pins this (and the `**Total**` Summary row + catalog title) at the source.
