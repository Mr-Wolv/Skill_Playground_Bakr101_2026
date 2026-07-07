---
name: backward-compatibility-and-change-management
description: Review and plan interface, schema, config, and behavior changes to preserve compatibility, minimize consumer breakage, and manage safe evolution over time.
---

# Backward Compatibility and Change Management

Use this skill when evolving APIs, events, schemas, configs, data contracts, or observable behavior that other systems, users, or teams may depend on.

This skill exists to answer a practical question before change ships: **is this breaking, for whom, and how do we evolve it safely?**

## Use when

- changing a public API or SDK
- evolving a database schema used by existing code paths
- changing event payloads, queues, or message contracts
- renaming config keys or altering configuration semantics
- modifying observable behavior that external users or systems may rely on
- deciding whether versioning, adapters, flags, dual-write, or transition windows are needed

## Do not use when

- you only need to write a migration plan after deprecation is already decided — use `deprecation-and-migration`
- you need contract test implementation details — use `api-contract-testing`
- you are assessing general delivery risk — use `change-risk-assessment`

## Core questions

Before approving a change, answer:

1. **Who or what depends on the current behavior?**
   - internal callers
   - external consumers
   - downstream pipelines
   - automation scripts
   - dashboards and alerts
   - undocumented but observable behavior

2. **What kind of compatibility is at stake?**
   - API contract compatibility
   - schema compatibility
   - event compatibility
   - config compatibility
   - behavior compatibility
   - operational compatibility

3. **Is the change additive, substitutive, or destructive?**
   - additive changes are usually safer
   - substitutions need transition handling
   - destructive changes need explicit migration and communication

4. **Can old and new coexist temporarily?**
   - dual read / dual write
   - versioned endpoints
   - adapters
   - aliases
   - compatibility shims
   - phased config support

5. **How will consumers discover and survive the change?**
   - deprecation warnings
   - migration guides
   - compatibility windows
   - feature flags
   - contract tests
   - rollout monitoring

## Safe evolution patterns

Prefer these patterns when possible:

- add new field before removing old field
- support old and new config keys during transition
- version externally visible contracts only when needed
- keep consumers working while migration is in progress
- use adapters where interface preservation is cheaper than mass migration
- remove only after usage has been measured near zero

## Breaking change heuristics

Treat a change as potentially breaking if it:

- removes or renames fields, endpoints, events, or config keys
- changes defaults or behavior in a way callers can observe
- tightens validation or authorization rules
- changes ordering, timing, or retry semantics that clients may rely on
- alters nullability, cardinality, or required fields
- assumes consumers will update in lockstep

## Recommended outputs

A good result includes:

- compatibility assessment
- identified consumers and dependency surface
- breaking vs non-breaking classification
- required transition strategy
- migration and communication requirements
- removal criteria for legacy behavior

## Typical trigger phrases

- "is this a breaking change"
- "maintain backward compatibility"
- "compatibility review"
- "how do we evolve this safely"
- "can we change this without breaking consumers"
- "what transition strategy do we need"
