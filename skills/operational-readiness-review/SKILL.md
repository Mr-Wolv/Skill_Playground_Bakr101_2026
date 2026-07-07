---
name: operational-readiness-review
description: Review whether a service, feature, or system is truly ready to operate in production by checking observability, runbooks, rollback, ownership, alerts, and supportability.
---

# Operational Readiness Review

Use this skill before launch, handoff, or production ownership transfer to determine whether a system is operationally ready — not just implemented.

This is a cross-cutting review skill. It focuses on whether the system can be run, monitored, supported, recovered, and safely owned in the real world.

## Use when

- preparing a service or feature for production
- checking whether a new system is ready for on-call ownership
- doing a go-live or launch readiness review
- evaluating operational maturity before handoff to another team
- reviewing whether alerts, dashboards, runbooks, and rollback are truly in place

## Do not use when

- you need a deployment plan and staged rollout sequence — use `shipping-and-launch`
- you need incident response during an active outage — use `incident-response`
- you only need observability instrumentation — use `observability-and-instrumentation`

## Review dimensions

1. **Observability**
   - logs, metrics, tracing, dashboards
   - useful health signals
   - alerts that map to actionable conditions

2. **Recoverability**
   - rollback path exists
   - restore or failover path exists where needed
   - restart/recovery procedures are known and tested

3. **Runbooks and supportability**
   - operational procedures exist for common failures
   - escalation path is clear
   - support expectations are explicit

4. **Ownership and response model**
   - clear owning team or maintainer
   - on-call or support coverage defined
   - responsibility boundaries understood

5. **Change safety**
   - deploy procedure is documented
   - risky changes have safeguards
   - schema/config changes have safe sequencing

6. **Failure mode awareness**
   - known failure modes documented
   - external dependencies understood
   - degraded-mode behavior considered

7. **Operational hygiene**
   - access model is sane
   - secrets/config management is documented
   - manual steps are minimized or made explicit

## Recommended outputs

A good readiness review should produce:

- readiness verdict: ready / conditionally ready / not ready
- missing operational prerequisites
- high-risk blind spots
- required follow-up actions before go-live
- ownership and watch-window recommendations

## Red flags

- no clear owner
- no useful dashboards or alerts
- no rollback or recovery procedure
- no runbook for obvious failure cases
- support model depends on tribal knowledge
- production behavior cannot be distinguished from healthy behavior quickly
- launch depends on a person remembering undocumented steps

## Typical trigger phrases

- "are we operationally ready"
- "production readiness review"
- "go-live readiness"
- "is this ready for on-call"
- "service readiness review"
- "what is missing before we can support this in production"
