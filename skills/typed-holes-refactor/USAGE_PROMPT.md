# Typed Holes Refactor — Example Prompts & Troubleshooting

Companion to `README.md`. Copy-paste these prompts to drive a typed-holes
refactor, and use the troubleshooting table when a step stalls.

## Example prompts

### 1. Discover holes in a module

```
Use the typed-holes-refactor skill. Target the `billing/` module.

Context: it processes invoices but has no types distinguishing a Draft from a
Posted invoice. Discover the architectural "holes" — places where the code uses
untyped primitives (dict/Any) that should be domain types — and list them with
their dependency order. Do not change code yet; produce the hole manifest.
```

### 2. Resolve a hole with TDD

```
Continue the typed-holes refactor. Resolve the first hole: introduce a
`PostedInvoice` type. Write characterization tests that capture CURRENT behavior
first, then refactor to the typed hole, and confirm tests stay green. Report the
constraint delta propagated to callers.
```

### 3. Full safe refactor in a branch

```
Refactor `billing/` end-to-end with the typed-holes-refactor skill. Work on a
branch named `refactor/typed-billing`, never touch `main` or `.beads/`. For each
hole: write validation tests, resolve, propagate constraints, validate, repeat.
Emit an old-vs-new report at the end and list any holes you deliberately left
open with rationale.
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| "No holes found" on a messy module | discovery too shallow / wrong entrypoint | point at the directory with the untyped primitives; widen the scan |
| Characterization tests fail immediately | existing behavior already broken | capture current behavior as the oracle anyway; the failure IS the bug to record |
| Constraint propagation loops | two holes depend on each other cyclically | resolve the shared dependency first or introduce an interface to break the cycle |
| Branch changes `main` | agent drifted out of the branch | abort, re-checkout branch; skill must only write to the working branch |
| Report empty | validation step skipped | re-run with explicit "emit old-vs-new report" and confirm tests ran |
| `.beads/` modified | agent treated it as a target | `.beads/` is off-limits; restore from git, re-run excluding it |

## Guardrails (non-negotiable)

- Always work on a branch; `main` is read-only.
- Never write to `.beads/`.
- Tests before code for every hole.
- A hole left open must be named with a reason, not silently dropped.
