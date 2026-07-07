# AGENTS.md

## Mission

Treat this repository as a **living skill architecture** rather than a loose collection of prompts.

The goal is to improve the long-term engineering capability of the ecosystem, not to maximize the number of skills.

When working in this repo:

- optimize for **high cohesion** and **low coupling**
- avoid duplication, fragmentation, and capability inflation
- prefer reusable engineering concepts over narrow technology-specific skills
- treat `skills/` and `C:\Users\GIGABYTE\.agents\skills` as mirrored skill stores
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
- global: `C:\Users\GIGABYTE\.agents\skills`

Parity means full folder contents, not only matching folder names.

Changes should preserve parity unless a task explicitly says otherwise.

After catalog-affecting work, run:

1. `python scripts/sync_skills_to_global.py`
2. `python scripts/validate_catalog.py`
3. `python scripts/check_skill_mirror_parity.py`

Or use the shortcut:

- `python scripts/sync_and_validate.py`

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
