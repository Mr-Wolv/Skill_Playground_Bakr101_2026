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

## Boundary

Use this skill for repository catalog coherence: source-of-truth discovery, count verification, mirror parity checks, and reconciliation of catalog-bearing documents and manifests.

Do not use this skill for historical reconstruction of why a repository evolved the way it did. For that, use `repository-archaeology`.

Do not use this skill for general codebase health, tech debt, dead code, or dependency audits. Use the repository-intelligence specialist skill that matches that problem.

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

## Convergence audit (the "many truths → one truth" pass)

When the task is not a one-off reconciliation but a *convergence audit* — declare a
catalog "complete", "coherent", or "Version 1.0" — produce a **report**, not just a
fix-list. The deliverable is a findings table where every finding carries
**impact / recommended action / priority / architectural justification**, plus a
go/no-go verdict on the completion claim. Framing: the goal is to find *inconsistencies,
ambiguity, duplication, drift, architectural debt, simplification opportunities* — not
to add capabilities.

Run the repo's own QC gate first and report its result as ground truth. A green
`gate.py` / `make verify` is strong evidence the *mechanical* foundation is converged
even when prose docs contradict each other. Convergence findings are almost always in
the *documents*, not the validator.

Reusable techniques that caught real drift (cheap to re-run; see
`references/convergence-audit-recipe.md` for the scripted versions):

1. **Source-of-truth contradiction check.** Grep every governance/doc for "source of
   truth" and confirm they agree on WHICH directory is authoritative. This session found
   `docs/catalog-governance.md` calling `skills/` the source of truth while
   `AGENTS.md`/`README.md`/`docs/index.md` called `~/.agents/skills` the source of truth
   — a direct "many similar truths" violation and the single highest-value finding. Check
   it first.
2. **Prose-count lint.** Docs hard-code totals that drift from the folder set (a catalog
   summary said "62 custom / 176 community = 238" while the validator confirmed 240/64/176).
   Cross-reference every literal count in markdown against `len(os.listdir('skills'))` and
   the json `total_skills`.
3. **Cross-artifact token cross-reference.** Parse every backtick-coded skill token out of
   each catalog/doc (skipping fenced code blocks), then diff against the folder set:
   orphans (token with no folder), missing (folder never mentioned), duplicates (token
   listed >1×). Diff `skills.json` `community_skill_names` vs folders to derive the implied
   custom set; compare to any `custom` markers in the catalogs.
4. **Placeholder-description finder.** Regex the catalog table for empty/truncated cells
   (`| > |`, `| >- |`, `| ~ |`) — unfinished entries in a "complete" deliverable.
5. **Coverage gaps.** List folders in NO catalog row and NO cheatsheet trigger phrase;
   prioritize surfacing high-value meta/orchestration skills that are undiscoverable.

## Output expectations

For a reconciliation pass, produce a concise summary with:

- verified total skill count
- mirror parity result
- artifacts updated
- remaining ambiguities, if any

For a convergence audit, produce the report described in the section above.

## Anti-patterns

- trusting stale document counts over actual directories
- updating one index while leaving adjacent indexes stale
- inventing precise category breakdowns without verification
- silently ignoring repo/global divergence
- treating mirrored stores as synced without checking
- declaring a catalog "complete" from a green gate alone — prose-doc contradictions are
  the convergence defects a passing validator does not see
