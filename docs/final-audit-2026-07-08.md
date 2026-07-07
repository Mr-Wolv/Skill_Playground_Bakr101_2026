# Final Catalog Audit

> Date: 2026-07-08

## Executive Summary

The skill catalog is now materially more coherent than at the start of this session.

### Verified current state

- Repository skills: **233**
- Global mirrored skills: **233**
- Repo/global parity: **exact**

### Major improvements completed

#### New capabilities added
- `catalog-consistency-auditor`
- `architecture-review`
- `repository-archaeology`
- `design-review`
- `codeowners-and-review-routing`
- `change-risk-assessment`
- `toil-analysis-and-automation`
- `backward-compatibility-and-change-management`
- `operational-readiness-review`
- `service-ownership-and-lifecycle-management`

#### Consolidation work completed
- Reduced ADR duplication inside `documentation-and-adrs`
- Reduced operational-review duplication inside `code-review-excellence`
- Clarified boundaries across the review and documentation clusters
- Reduced remaining overlap to a small watchlist of boundary-polish candidates rather than severe duplication

## Architectural Assessment

### Strengths

1. **Improved repository-intelligence coverage**
   - The catalog now covers consistency auditing and repository archaeology explicitly.

2. **Improved architecture, delivery, and governance coverage**
   - The catalog now has distinct skills for:
     - architecture review
     - design review
     - compatibility/change management
     - delivery risk assessment
     - operational readiness review
     - service ownership and lifecycle management

3. **Better separation of workflow vs reference vs culture skills**
   - `research` vs `research-methodology`
   - `code-review` vs `code-review-excellence`
   - `documentation-and-adrs` vs `architecture-decision-records`

4. **Mirror governance is now explicit**
   - repo/global parity expectations are documented and being maintained

### Remaining overlap candidates

These are the best remaining consolidation candidates still worth watching.

#### 1. `incident-response` vs `postmortem`

**Why it remains a candidate**
- `incident-response` currently includes postmortem generation as part of its flow
- `postmortem` is now stronger after absorbing writing/facilitation material

**Current recommendation**
- keep both
- narrow `incident-response` conceptually to incident handling and handoff into postmortem
- avoid duplicating postmortem guidance inside incident-response where possible

**Not an immediate merge candidate** because the phases are still operationally distinct.

#### 2. `incident-runbook-templates` vs incident workflow skills

**Why it remains a candidate**
- it touches active response behavior and documentation
- some "responding to active incidents" phrasing blurs with `incident-response`

**Current recommendation**
- keep it
- consider tightening description later so it is clearly a runbook authoring/template skill, not an incident command skill

#### 3. `request-refactor-plan` vs `planning-and-task-breakdown`

**Why it remains a candidate**
- both break work into ordered steps
- both can produce implementation plans

**Current recommendation**
- keep both
- interpret them as:
  - `planning-and-task-breakdown` = general planning workflow
  - `request-refactor-plan` = refactor-specific, interview-heavy, issue-oriented planning workflow

This is currently acceptable.

#### 4. `architecture-review` vs `improve-codebase-architecture`

**Why it remains a candidate**
- both inspect architecture
- one reviews, one proposes deepening opportunities interactively

**Current recommendation**
- keep both
- the current split is healthy:
  - `architecture-review` = assessment
  - `improve-codebase-architecture` = exploratory improvement workflow

No merge recommended.

## Skills with good boundary health now

These clusters are now in a good enough state that no immediate change is recommended.

### Review cluster
- `code-review`
- `code-review-and-quality`
- `code-review-excellence`

### Documentation cluster
- `documentation-and-adrs`
- `architecture-decision-records`

### Research cluster
- `research`
- `research-methodology`

### Repository intelligence cluster
- `catalog-consistency-auditor`
- `repository-archaeology`
- `tech-debt-tracker`
- `dead-code-remover`
- `dependency-auditor`

### Delivery and operations cluster
- `shipping-and-launch`
- `change-risk-assessment`
- `operational-readiness-review`
- `service-ownership-and-lifecycle-management`
- `toil-analysis-and-automation`

## Documentation Drift Observed During Audit

The major stale count and merge-proposal issues identified during this audit have now been corrected.

Remaining cleanup is now mostly wording polish, trigger quality, and evidence-based refinement rather than structural or count inconsistency.

## Recommended Next Actions

### Highest-value cleanup
1. Continue tightening wording, examples, and trigger clarity in the most-used skills.

### Best next consolidation candidate
2. Keep watching the `incident-response` / `postmortem` boundary so post-incident ownership stays clean.

### Optional future taxonomy work
3. Refine discoverability and grouping further only if actual usage shows confusion.

## Conclusion

The catalog is now significantly stronger in:

- repository intelligence
- architecture/design evaluation
- capability boundary clarity
- sync/governance discipline

The highest-risk overlap problems identified during this session have already been reduced. The remaining issues are now mostly boundary polish, wording freshness, and evidence-driven refinement rather than severe architectural duplication.
