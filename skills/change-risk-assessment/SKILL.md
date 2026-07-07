---
name: change-risk-assessment
description: Assess the delivery risk of a code, config, schema, or infrastructure change and recommend safeguards such as canaries, approvals, rollback plans, and preflight checks.
---

# Change Risk Assessment

Use this skill before shipping a meaningful change when you need to understand blast radius, failure modes, and what safeguards should be in place.

This skill is about deciding how risky a change is and what protections it needs before rollout. It is not just deployment planning; it is preflight judgment.

## Use when

- evaluating whether a change is safe to ship
- deciding whether a rollout needs canarying, feature flags, or approvals
- assessing config, migration, infra, auth, or data changes before release
- preparing a preflight checklist for a risky deploy
- comparing rollout options based on risk

## Boundary

Use this skill before rollout when the key question is risk: blast radius, reversibility, detectability, failure modes, and which safeguards are justified.

Use `shipping-and-launch` instead when you already intend to ship and need the practical rollout checklist, staged rollout sequence, monitoring plan, and rollback preparation.

Use `operational-readiness-review` instead when the question is whether the service or feature is supportable and operable in production as a system, not just whether one change is risky.

## Do not use when

- you are already actively responding to a failure — use `incident-response`
- you need a broad launch checklist and staged rollout plan — use `shipping-and-launch`
- you need a post-incident analysis — use `postmortem` or `failure-analysis`

## Risk dimensions

Assess the change across these dimensions:

1. **Blast radius**
   - how many users, systems, or teams are affected if this goes wrong?
   - is this localized, regional, tenant-specific, or platform-wide?

2. **Reversibility**
   - can the change be rolled back quickly?
   - does rollback restore the previous state cleanly?
   - are there irreversible data mutations or contract changes?

3. **Change surface area**
   - how many components are changing?
   - does the change cross boundaries like app + DB + infra + clients?
   - are multiple systems being coordinated at once?

4. **Operational novelty**
   - is this a known, repeated workflow or a first-time maneuver?
   - are operators familiar with the procedure?
   - are tools, scripts, and dashboards already prepared?

5. **Failure detectability**
   - would failure be visible quickly?
   - are metrics, logs, alerts, and health checks in place?
   - could the failure be silent or delayed?

6. **Data and security sensitivity**
   - does it affect auth, permissions, secrets, money, or regulated data?
   - could failure cause corruption, leakage, or privilege escalation?

7. **Dependency and coordination risk**
   - does success depend on external services, ordering, timing, or team coordination?
   - are there hidden preconditions?

## Risk rating model

Use a simple working model:

- **Low risk** — small blast radius, easy rollback, strong observability, familiar procedure
- **Medium risk** — some cross-system effects or rollback caveats, but manageable safeguards exist
- **High risk** — broad blast radius, difficult rollback, novel procedure, weak detectability, or sensitive data/security implications

## Recommended outputs

For each assessed change, produce:

- risk summary
- top failure modes
- likely blast radius
- rollback confidence
- required safeguards
- go / hold / redesign recommendation

## Safeguards to recommend

Depending on risk, recommend some combination of:

- feature flags
- canary rollout
- staged rollout
- manual approval gate
- extra reviewer signoff
- schema expand/contract sequencing
- backup or snapshot before change
- preflight verification checklist
- post-deploy watch window
- rollback rehearsal
- freeze window or off-peak timing

## Preflight checklist structure

1. What is changing?
2. What can fail?
3. Who/what would be affected?
4. How would we know quickly?
5. How do we stop or roll back safely?
6. What safeguards are mandatory before shipping?
7. Who must approve or be on standby?

## Warning signs

Escalate risk if you see:

- irreversible migrations
- auth or permissions changes
- coordinated deploys across multiple systems
- unknown dependency behavior
- poor monitoring coverage
- incomplete rollback path
- changes landing before weekends, holidays, or low staffing windows
- "we'll just fix it in prod if needed"

## Typical trigger phrases

- "how risky is this deploy"
- "what could break if we ship this"
- "do a preflight risk review"
- "what safeguards should we add before rollout"
- "classify the risk of this change"
- "is this safe to deploy"
