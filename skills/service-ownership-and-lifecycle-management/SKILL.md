---
name: service-ownership-and-lifecycle-management
description: Define who owns a service, what responsibilities they carry, how lifecycle states are managed, and when systems should be invested in, handed off, or retired.
---

# Service Ownership and Lifecycle Management

Use this skill when a service or subsystem needs explicit ownership, stewardship expectations, lifecycle policy, and a durable operating model beyond code review routing.

This skill is about sustained accountability for a system across its life: active development, steady-state operation, handoff, and retirement.

## Use when

- ownership of a service or subsystem is unclear
- defining maintainer responsibilities for a new or existing system
- handing a system from one team to another
- classifying lifecycle state such as incubating, active, maintenance-only, or retiring
- deciding whether a system should be maintained, consolidated, or sunset
- clarifying support expectations and stewardship boundaries

## Do not use when

- you only need `CODEOWNERS` and review assignment — use `codeowners-and-review-routing`
- you only need deprecation mechanics — use `deprecation-and-migration`
- you only need on-call shift handoff — use `on-call-handoff-patterns`

## Ownership model

For each service or subsystem, define:

- primary owner
- secondary/backstop owner
- support expectations
- escalation path
- operational responsibilities
- dependency responsibilities
- documentation expectations
- lifecycle state

## Typical lifecycle states

- **Incubating** — early stage, fast change, limited support promises
- **Active** — normal investment, clear ownership, expected reliability
- **Maintenance** — limited feature work, only necessary fixes and upkeep
- **Retiring** — migration underway, no new investment except safe removal work
- **Orphaned** — no acceptable state; must assign owner or plan retirement

## Core questions

1. Who is accountable when this breaks?
2. Who approves major changes to this system?
3. Who maintains docs, alerts, and runbooks?
4. What support level is promised?
5. What is the current lifecycle state?
6. What would justify more investment, transfer, or retirement?
7. Are dependencies and consumers aware of the ownership model?

## Good outputs

A good result includes:

- ownership matrix
- lifecycle classification
- maintainer responsibilities
- support and escalation expectations
- handoff or retirement recommendations where needed
- identified orphan-risk or stewardship gaps

## Red flags

- no clear accountable owner
- multiple teams assuming another team owns it
- active production system in maintenance-by-accident mode
- orphaned docs/runbooks/alerts
- lifecycle state implied but never documented
- no criteria for retirement or transfer

## Typical trigger phrases

- "who owns this service"
- "define service ownership"
- "what are the maintainer responsibilities"
- "set lifecycle policy for this subsystem"
- "is this system active or retiring"
- "clarify stewardship and support expectations"
