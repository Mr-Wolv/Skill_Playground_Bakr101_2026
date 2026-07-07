# Skill Merge and Boundary Proposal

> Last updated: 2026-07-08

## Purpose

This document records the current merge and boundary recommendations for overlapping skill clusters.

It reflects both:

- work already completed
- remaining consolidation candidates

## Completed consolidations

### Executed merge
- `postmortem-writing` → merged into `postmortem`

### Executed boundary cleanups
- `documentation-and-adrs` reduced ADR-specific duplication and now points formal ADR work to `architecture-decision-records`
- `code-review-excellence` reduced operational review duplication and now focuses more clearly on review practice and team culture

## Current recommendations by cluster

| Cluster | Recommendation | Status |
|---|---|---|
| `code-review`, `code-review-and-quality`, `code-review-excellence` | Keep all three with current clarified boundary | Healthy enough now |
| `documentation-and-adrs`, `architecture-decision-records` | Keep both with current generalist/specialist split | Healthy enough now |
| `research`, `research-methodology` | Keep both | Healthy |
| `incident-response`, `postmortem` | Keep both, but tighten handoff boundary later | Candidate for future cleanup |
| `incident-runbook-templates`, incident workflow skills | Keep, but tighten wording later | Candidate for future cleanup |
| `planning-and-task-breakdown`, `request-refactor-plan` | Keep both | Acceptable split |

## Remaining consolidation candidates

### 1. Incident workflow boundary cleanup

#### Skills
- `incident-response`
- `postmortem`
- `incident-runbook-templates`

#### Recommendation
Do not merge now.

Instead:
- keep `incident-response` focused on active incident handling
- keep `postmortem` as the durable post-incident analysis artifact/workflow
- keep `incident-runbook-templates` as a runbook authoring/template skill

#### Why
The capabilities are related but not identical. The issue is not duplication of purpose so much as some overlapping phrasing and ownership hints.

### 2. Planning cluster watchlist

#### Skills
- `planning-and-task-breakdown`
- `request-refactor-plan`

#### Recommendation
Keep both.

#### Why
The current split is workable:
- general planning vs refactor-specific planning
- generic task decomposition vs interview-driven issue-oriented refactor scoping

No immediate simplification is worth the risk.

## Rename watchlist

No rename is recommended immediately.

If discoverability becomes a bigger concern later, possible candidates remain:
- `code-review-and-quality` → `quality-code-review`
- `documentation-and-adrs` → `engineering-documentation`

These remain optional, not recommended now.

## Recommendation

At this point, further consolidation should be conservative.

The catalog has moved from meaningful overlap to manageable boundary nuance. The next wins are more likely to come from:

- documentation freshness
- wording cleanup
- selective tightening of descriptions
- trigger and discoverability improvements
- careful enhancement of existing high-value workflow skills

rather than from additional merges.
