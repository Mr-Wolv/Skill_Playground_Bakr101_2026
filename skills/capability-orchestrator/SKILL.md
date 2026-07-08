---
name: capability-orchestrator
description: >-
  Select, sequence, and compose engineering capabilities to solve a problem as a
  coordinated workflow rather than one-off skill calls. Use when a request spans
  multiple engineering phases, when you must decide which capabilities participate
  and in what order, or when you want prerequisite/review/validation capabilities
  wired in automatically. Turns a vague engineering goal into an executable
  capability plan.
category: engineering-mindset
source: custom
tags: [orchestration, workflow, sequencing, composition, routing, coordination]
version: 1.0
---

# Capability Orchestrator

An engineering intelligence does not answer a request by grabbing one skill. It
decides which capabilities are needed, in what order, with which prerequisites
and which review/validation gates, then executes the chain. This skill is that
decision layer. It is technology-independent and works with any catalog of
engineering capabilities, including the Skill Playground library it ships with.

## When to use

- A request clearly spans more than one SDLC phase (ideation, requirements,
  architecture, implementation, testing, operations, governance).
- You must decide which capabilities participate and in what order.
- You want prerequisite, review, and validation capabilities wired in
  automatically rather than recalled ad hoc.
- You are handing a multi-step engineering task to a subagent or a team and need
  an explicit capability plan they can follow.

## When NOT to use

- The task is a single, well-scoped skill call (just invoke that skill).
- Use `capability-router` when you only need to map a request to the right
  skill(s) by phase, without building an execution plan.
- Use `engineering-phase-detector` when you only need to know which phase is
  active.

## Orchestration Protocol

### 1. Classify the request
Identify the engineering intent and the phases it touches. Phases:

- Ideation & Concept
- Requirements & Specification
- Architecture & Design
- Implementation
- Testing & Quality
- Operations & Readiness
- Incident & Learning
- Governance & Convergence

### 2. Enumerate candidate capabilities
For each touched phase, list the capabilities that can participate. Prefer
naming real catalog skills. Examples drawn from the Skill Playground library:

- Requirements: `spec-driven-development`, `to-prd`, `domain-modeling`,
  `ubiquitous-language`, `interview-me`
- Architecture: `architecture-review`, `design-review`, `architecture-decision-records`
- Implementation: `incremental-implementation`, `tdd`, `typed-holes-refactor`
- Testing: `code-review`, `code-review-and-quality`, `visual-regression-testing`
- Operations: `operational-readiness-review`, `change-risk-assessment`, `slo-implementation`
- Learning: `postmortem`, `root-cause-analysis`, `failure-analysis`
- Governance: `catalog-consistency-auditor`, `codeowners-and-review-routing`

### 3. Build the execution graph
For each capability, declare:

- `produces`: the artifact or decision it yields
- `requires`: prerequisite capabilities (must run first)
- `reviewed_by`: validation/review capability that should gate completion
- `optional`: capabilities that add value but are not blocking

A linear request becomes an ordered list; a branching request becomes a DAG.

### 4. Inject review and validation gates
Every producing capability should name a reviewing capability. Defaults:

- Code change -> `code-review` (standards + spec)
- Architecture decision -> `architecture-review`
- Production change -> `change-risk-assessment` + `operational-readiness-review`
- Incident -> `postmortem` after `incident-response`

### 5. Emit the plan
Output a compact plan an agent or team can execute:

    PHASE: Architecture & Design
    STEP 1  architecture-review        (produces: review)
            requires: spec-driven-development
            reviewed_by: design-review
    STEP 2  architecture-decision-records (produces: ADR)
            requires: architecture-review
    ...

### 6. Execute or delegate
Execute the plan in order, respecting `requires`. For subagents, pass the plan
as the brief. After execution, run any `reviewed_by` capability as a gate
before declaring done.

## Composition patterns

- **Sequential**: A -> B because B requires A's output.
- **Gate**: A, then review A before B starts.
- **Parallel**: independent capabilities run concurrently, converge at a join.
- **Loop**: revisit a capability when a review gate fails (e.g. re-run
  `architecture-review` after `design-review` findings).

## Relationship to sibling skills

- `engineering-phase-detector` — feeds the phase classification in step 1.
- `capability-router` — feeds the candidate enumeration in step 2.
- `thought-patterns` / `analytical-thinking-patterns` — apply when a step
  needs reasoning (tradeoff, systems, first-principles).
- `doubt-driven-development` — insert as an adversarial gate before any
  high-stakes decision in the plan.

## Quality bar

A good orchestration plan is executable by someone who has never seen the
request: each step names a capability, its inputs, its outputs, and its gate.
If a step is vague ("do the design"), decompose it further before executing.
