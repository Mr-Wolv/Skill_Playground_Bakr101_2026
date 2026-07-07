---
name: failure-analysis
description: Comprehensive failure analysis — timeline, causal network, defense-in-depth, action scoring
---

# Failure Analysis

Performs structured analysis of incidents and outages using aerospace/nuclear-inspired methodology.

## When to use

- A production incident has occurred
- A postmortem needs deeper analysis beyond basic RCA
- You need to identify systemic issues, not just surface causes

## Instructions

1. **Construct the timeline** — list all events in chronological order with timestamps and sources
2. **Build the causal network** — map cause-effect relationships. A single root cause is rarely the whole story — look for contributing factors, preconditions, and latent conditions
3. **Evaluate defense-in-depth** — for each failure point, identify:
   - What defenses existed
   - Why they failed or were bypassed
   - What defenses should have been in place
4. **Score each action** — for each proposed fix, score on:
   - **Impact** (1-5): how much it reduces risk
   - **Effort** (1-5): how hard it is to implement
   - **Priority**: impact/effort ratio
5. **Generate the report** with the highest-priority actions first

## Analysis structure

```markdown
## Timeline
- 14:02: Deploy v2.3.1 to production
- 14:05: Error rate spikes (500 errors)
- 14:06: Alert triggered
- 14:12: Engineer on-call acknowledges
- 14:18: Root cause identified
- 14:25: Rollback to v2.3.0
- 14:28: Error rate returns to baseline

## Causal Network
Deploy v2.3.1 → Missing env var → DB connection fails → 500 errors

## Defense-in-Depth Gaps
1. No canary deployment (would have caught before full rollout)
2. No config validation at startup (missing env var not detected)
3. Alert threshold too high (15 min delay before notification)

## Prioritized Actions
1. Add config validation at startup (impact: 5, effort: 1)
2. Implement canary deploys (impact: 4, effort: 3)
3. Lower alert threshold (impact: 3, effort: 1)
```
