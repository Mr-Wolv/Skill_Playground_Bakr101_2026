---
name: assumption-and-bias-check
description: >-
  Surface hidden assumptions, cognitive biases, blind spots, and overconfidence
  before a decision or output stands. Use when stakes are high, when a confident
  answer would be expensive to undo, when a plan rests on unstated premises, or
  when you want a second-pass integrity check on reasoning. Pairs with
  doubt-driven-development and analytical-thinking-patterns.
category: engineering-mindset
source: custom
tags: [assumption, bias, blind-spot, confidence, metacognition, critique]
version: 1.0
---

# Assumption & Bias Check

Engineering failures rarely come from bad math; they come from an assumption
nobody stated, a bias nobody noticed, or a confidence nobody earned. This skill
is a structured adversarial pass over a decision, plan, or analysis to surface
those gaps. It is technology-independent and composes with any engineering
capability.

## When to use

- Before a high-stakes decision (production change, architecture choice, security
  logic, irreversible operation).
- When a plan's premises were never written down.
- When you (or the user) feel unusually sure.
- After a first draft of analysis, as a validation gate.

## Check protocol

### 1. Extract explicit claims
List every factual claim and decision in the artifact. Separate stated from
implied.

### 2. Surface hidden assumptions
For each claim, ask: "What must be true for this to hold that we have not said?"
Common engineering traps:

- "The dependency is stable." (version/compatibility risk)
- "Traffic will be like last quarter." (no load change)
- "They will use it as documented." (abuse/edge cases)
- "This fixes the root cause." (correlation vs causation)
- "We can roll back." (rollback untested)

### 3. Flag bias patterns
- **Confirmation bias** — only evidence that supports the chosen approach sought.
- **Availability bias** — recent similar incident over-weighted.
- **Sunk-cost** — keeping a direction because effort is spent.
- **Anchoring** — first number/estimate unduly fixes the range.
- **Optimism bias** — timelines/risks underestimated.
- **Status-quo** — defaulting to the existing design without reason.

### 4. Estimate confidence honestly
Assign a confidence level per claim with a reason:

- High — verified, reproducible, owned.
- Medium — plausible, partially checked.
- Low — assumed, unverified, or contradicted by one signal.

Report where confidence is low but the decision treats it as high.

### 5. Emit the findings
    ASSUMPTIONS (unstated):
    - "caching layer never misses" — unverified under load
    BIAS FLAGS:
    - confirmation: only success paths tested
    CONFIDENCE:
    - rollback works: Low (never rehearsed)
    ACTION: do not ship until Low items are verified or mitigated

## Relationship to sibling skills

- `doubt-driven-development` — the in-flight adversarial posture; this skill is
  the explicit assumption/bias/confidence inventory it can delegate to.
- `analytical-thinking-patterns` — supplies the reasoning frameworks (first-
  principles, systems) used to challenge assumptions.
- `thought-patterns` — route to the metacognitive/creative resources here.
- `postmortem` / `failure-analysis` — use this skill during the analysis to stop
  repeating the same blind spots.

## Quality bar

A check is useful only if it names specifics. "Consider your biases" is noise.
"Confirmation bias: only the happy path was load-tested; the failure path is
unverified" is actionable.
