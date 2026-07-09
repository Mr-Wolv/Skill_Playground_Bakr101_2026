# Skill Merge and Boundary Proposal
# Skill Merge and Boundary Decisions

> Last updated: 2026-07-09

## Purpose

This document records the merge and boundary **decisions** already taken for overlapping skill clusters.

It reflects completed boundary work only.

## Executed boundary cleanups

- `documentation-and-adrs` reduced ADR-specific duplication and now points formal ADR work to `architecture-decision-records`
- `code-review-excellence` reduced operational review duplication and now focuses more clearly on review practice and team culture
- core overlapping clusters were further clarified through explicit boundary sections in the relevant skill bodies

## Current decisions by cluster

| Cluster | Decision | Status |
|---|---|---|
| `code-review`, `code-review-and-quality`, `code-review-excellence` | Keep all three with current clarified boundary | Resolved |
| `documentation-and-adrs`, `architecture-decision-records` | Keep both with current generalist/specialist split | Resolved |
| `research-note`, `research-methodology` | Keep both | Resolved |
| `incident-response`, `postmortem` | Keep both; handoff boundary already clarified in skill bodies | Decision: no merge |
| `incident-runbook-templates`, incident workflow skills | Keep; wording already tightened in skill bodies | Decision: no merge |
| `planning-and-task-breakdown`, `request-refactor-plan` | Keep both | Resolved split |

## Incident workflow boundary (decided)

#### Skills
- `incident-response`
- `postmortem`
- `incident-runbook-templates`

#### Decision
Do not merge.
- keep `incident-response` focused on active incident handling
- keep `postmortem` as the durable post-incident analysis artifact/workflow
- keep `incident-runbook-templates` as a runbook authoring/template skill

#### Why
The capabilities are related but not identical. The issue is not duplication of purpose so much as some overlapping phrasing and ownership hints.

## Planning cluster (decided)

#### Skills
- `planning-and-task-breakdown`
- `request-refactor-plan`

#### Decision
Keep both.

#### Why
The current split is workable:
- general planning vs refactor-specific planning
- generic task decomposition vs interview-driven issue-oriented refactor scoping

No simplification is worth the risk.

## Rename decision

No rename is recommended. The current names are accepted.

## Conclusion

Consolidation is complete for the current catalog state. The next improvements come from:
- documentation freshness
- wording cleanup
- selective tightening of descriptions
- trigger and discoverability improvements
- careful enhancement of existing high-value workflow skills

rather than from additional merges.
rather than from additional merges.
