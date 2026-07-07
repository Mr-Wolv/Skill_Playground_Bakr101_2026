---
name: catalog-consistency-auditor
description: Audit skill catalogs and repository documentation for drift against the actual skill set. Use when counts look stale, indexes disagree, mirrored stores may be out of sync, or catalog artifacts need one-pass reconciliation.
---

# Catalog Consistency Auditor

Audit a skill repository for structural drift between the actual skill folders and the documents that describe them.

This skill is for **catalog integrity**, not general code quality. Use it when the problem is that repository artifacts, counts, indexes, or mirrored skill stores may no longer agree.

## When to use

- A README, catalog, or manifest mentions counts that may be stale
- The workspace `skills/` directory and a mirrored global skill store may have diverged
- A skill was added, removed, renamed, merged, or split and the surrounding docs may be inconsistent
- You want a one-pass reconciliation of catalog artifacts after changing the skill set
- You suspect documentation drift across skill indexes, manifests, and navigation docs

## What this skill owns

This skill focuses on:

- structural source of truth discovery
- count verification
- mirror parity checks
- documentation drift detection
- index and manifest reconciliation
- explicit reporting of unresolved ambiguities

This skill does **not** decide whether a new capability should exist. Use capability-architecture or planning skills for that question.

## Workflow

### 1. Establish the source of truth

Treat the actual skill folders as the structural source of truth.

At minimum, verify:

- repository skill directory set
- mirrored/global skill directory set, if applicable

If documentation disagrees with the folder set, the folder set wins.

### 2. Compute the verified state

Record the facts before editing docs:

- total skill directory count
- repo-only entries
- global-only entries
- exact parity status
- any renamed/suspicious near-duplicates discovered during review

Do not copy prior totals from docs.

### 3. Audit catalog-bearing artifacts

Check all repository artifacts that can drift from the source of truth, including:

- `README.md`
- root `SKILL.md`
- `SKILL-CATALOG.md`
- `SKILL-CATALOG-DOMAIN.md`
- `SDLC-PHRASE-CHEATSHEET.md`
- `skills.json`
- `docs/index.md`
- governance or maintenance docs
- `AGENTS.md` if it references catalog behavior or sync rules

Look for:

- stale counts
- conflicting totals
- outdated category claims
- references to missing skills
- missing references to newly added skills
- inaccurate sync statements
- obsolete maintenance instructions

### 4. Reconcile in one pass

When you fix drift, update all affected artifacts in the same change.

Prefer:

- verified counts over inherited counts
- operational language over marketing language
- explicit uncertainty where classification is ambiguous
- narrow factual claims that are easy to keep true

If an exact breakdown cannot be verified confidently, avoid inventing one. State the verified fact and note what remains unclassified.

### 5. Report unresolved issues explicitly

If you encounter ambiguity, record it clearly instead of guessing. Examples:

- a skill appears workflow-oriented and category placement is unclear
- the repo and global stores differ and intentionality is unknown
- legacy docs use a classification scheme that no longer maps cleanly to the current catalog

## Output expectations

Produce a concise reconciliation summary with:

- verified total skill count
- mirror parity result
- artifacts updated
- remaining ambiguities, if any

## Anti-patterns

- trusting stale document counts over actual directories
- updating one index while leaving adjacent indexes stale
- inventing precise category breakdowns without verification
- silently ignoring repo/global divergence
- treating mirrored stores as synced without checking
