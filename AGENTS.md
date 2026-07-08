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

- workspace: `D:\Skill-Playground\skills`
- global: `~/.agents/skills`

Parity means full folder contents, not only matching folder names.

Changes should preserve parity unless a task explicitly says otherwise.

After catalog-affecting work, run:

1. `python scripts/sync_global_to_repo.py`   # export global -> this repo (community copy)
2. `python scripts/validate_catalog.py`
3. `python scripts/check_skill_mirror_parity.py`

Or use the shortcut:

- `python scripts/sync_and_validate.py`

## Skill Store Ownership & Boundaries

There are four skill stores. Ownership and the load/sync rules for each are fixed to remove ambiguity:

- **Shared catalog** `~/.agents/skills` — the single SOURCE OF TRUTH. A neutral directory owned by the human. Every agent reads from it; nobody auto-writes into it. Publishing is opt-in and human-approved.
- **Public repo** `skills/` in this repo — a downstream export of the shared catalog. Never authoritative; never pushed back into the catalog.
- **Runtime** `$HERMES_HOME/skills` (default `~/.hermes/skills`) — Hermes's load path, DERIVED from the shared catalog (via `sync_runtime_to_mirror.py`). Auto-rebuilt; never a write target, never a source of truth. The exact path is resolved by `runtime_skills_dir()` in `scripts/skill_paths.py` through `$HERMES_RUNTIME_SKILLS` → `$HERMES_HOME/skills` → `~/.hermes/skills`, so when `HERMES_HOME` points at `<LOCALAPPDATA>/hermes` the runtime follows it. Other agents have their own equivalent runtime, derived from the shared catalog + their own private store.
- **Hermes private** `<LOCALAPPDATA>/hermes/skills` — Hermes's own experimental/agent-authored skills. Excluded from all sync. Never read by other agents.
- **User private** `~/skills` — the human's own experiments, deliberately ASIDE from every agent. NOT in any agent load path, NOT synced, NOT read or written by Hermes or any other agent.

Hermes is NOT the source of truth. The human owns the catalog; agents are derived from it.

Routing rule (no ambiguity):

- shared/curated skill -> shared catalog (the one truth); derives to runtime + exports to repo
- private/experimental skill -> its owner's private store (yours: `~/skills`; Hermes's: `<LOCALAPPDATA>/hermes/skills`)
- NEVER write into a runtime store as an origin
- NEVER cross into another owner's private store
- sync is additive, hash-detect-don't-overwrite, backup-before-write, private stores excluded

The human manages exactly two things: the shared catalog (what they publish) and their own `~/skills`. Runtimes are auto-derived and never monitored.

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

If the case is ambiguous, do not add the skill yet. Capture the gap, observe real usage, and revisit later.
