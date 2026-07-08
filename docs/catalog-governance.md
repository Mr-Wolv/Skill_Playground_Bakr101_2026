# Catalog Governance and Sync Model

> Last verified: 2026-07-08

## Purpose

This document defines the source-of-truth and maintenance rules for the Skill Playground catalog.

## Current Verified State

- Repository skill directories: **238**
- Global skill directories: **238**
- Full recursive parity between repo and global store: **yes**

Verified against:

- `D:\Skill-Playground\skills`
- `~/.agents/skills`

## Source of Truth

The primary structural source of truth is the actual set of folders under:

- `skills/` in this repository

The global directory is treated as a synchronized mirror:

- `~/.agents/skills`

If any document count disagrees with the folder set, the folder set wins and the document must be updated.

## Required Consistency Targets

When skills are added, removed, renamed, merged, or split, review and update as needed:

- `README.md`
- `SKILL.md`
- `SKILL-CATALOG.md`
- `SKILL-CATALOG-DOMAIN.md`
- `SDLC-PHRASE-CHEATSHEET.md`
- `skills.json`
- `docs/index.md`
- `AGENTS.md`

## Minimum Change Checklist

For any catalog-affecting change:

1. update the skill folder(s)
2. export the global source of truth into this repo with `python scripts/sync_global_to_repo.py` (private skills stay out unless opted in)
3. validate repo documentation and manifests with `python scripts/validate_catalog.py`
4. confirm full recursive repo/global parity with `python scripts/check_skill_mirror_parity.py`
5. update counts mentioned in documentation
6. update catalog placement
7. update trigger phrasing if invocation guidance changed
8. update machine-readable manifests
9. note any unresolved classification ambiguity explicitly

## Count Policy

Do not hand-maintain counts by memory.

Before editing docs that mention totals:

1. count actual skill directories
2. compare repo and global stores for full recursive parity, not only folder names
3. update all affected documents in one pass

## Automation

The repository includes:

- `scripts/sync_global_to_repo.py` — export the global source of truth (`~/.agents/skills`) into this repo (community copy); private skills stay out unless opted in
- `scripts/sync_runtime_to_mirror.py` — keep this agent's runtime store in sync with global
- `scripts/check_skill_mirror_parity.py` — full recursive parity verification between repo and global stores
- `scripts/sync_and_validate.py` — convenience wrapper that syncs, validates docs, and checks parity

GitHub Actions validates repository coherence on pushes and pull requests. Full mirror parity is a local concern because the CI runner cannot inspect `~/.agents/skills` on your workstation.

## Naming Policy

- use lowercase kebab-case for skill folder names
- prefer concept-based names over vendor-or-language names unless specialization is justified
- avoid near-duplicates that differ only in phrasing

## Catalog Evolution Policy

Catalog growth is justified only when it improves one or more of:

- capability coverage
- modularity
- discoverability
- maintainability
- reuse
- engineering judgment

Do not create skills merely because a technology exists.

The repository is now in a governed maintenance phase: prefer improving boundaries, discovery, naming, examples, and validation discipline before adding net-new skills.

## Evidence-Driven Refinement Policy

Core boundary cleanup across the most overlapping skill clusters has already been completed.

From this point onward, further boundary refactoring should usually be justified by evidence from real project use rather than speculative cleanup. Examples of useful evidence include:

- repeated confusion about which skill to invoke
- repeated overlap during actual task execution
- prompts or trigger phrases that consistently route to the wrong skill
- user or agent friction caused by unclear skill boundaries
- recurring gaps observed while solving real engineering problems

Prefer this order:

1. use the current catalog in real projects
2. observe confusion, misses, or repeated friction
3. refine the smallest set of skills needed to address the observed problem
4. stop once the practical confusion is reduced

Do not keep harmonizing low-traffic or specialist skills purely for stylistic consistency when no real project usage suggests a problem.

## Expansion Control Policy

The catalog is mature enough that net-new skill creation should now be treated as a high-bar exception rather than the default way to improve the repository.

Before adding a new skill, prefer this order:

1. enhance an existing skill
2. improve descriptions, triggers, examples, or cross-references
3. split an overloaded skill only if boundary clarity materially improves
4. merge overlapping skills when duplication is the real problem
5. add a new skill only when the capability is clearly distinct, reusable, and repeatedly valuable

A proposed new skill should beat the alternatives above on all or most of:

- distinctness
- reuse
- discoverability
- maintainability
- engineering value

If the case is ambiguous, defer creation and gather evidence from real usage.
