---
name: architecture-review
description: Review an existing or proposed architecture against requirements, boundaries, risks, operability, and tradeoffs. Use when assessing architecture quality, reviewing design proposals, or checking whether a system structure fits its constraints.
---

# Architecture Review

Review an architecture as a system of decisions, boundaries, and tradeoffs.

Use this skill to evaluate whether an existing or proposed architecture is a good fit for the problem it is supposed to solve. The goal is not to redesign everything. The goal is to identify the most important structural strengths, weaknesses, risks, and mismatches.

## When to use

- Reviewing a proposed system design before implementation
- Assessing whether an existing architecture still fits current requirements
- Evaluating module boundaries, dependency direction, and responsibility allocation
- Reviewing a service decomposition, integration model, or deployment shape
- Comparing architecture options against constraints like scale, reliability, cost, security, or team capacity
- Preparing architecture feedback for a document, ADR, proposal, or technical review

## Boundary

Use this skill to evaluate an existing or proposed architecture as a whole-system or multi-boundary structure.

Use `design-review` instead when the artifact under review is a more local solution shape such as a module design, workflow, interface, or feature proposal rather than the architecture of the wider system.

Use synthesis skills such as `architecture-patterns`, `api-and-interface-design`, `design-an-interface`, or `codebase-design` when the primary need is to create or reshape a design rather than to review one.

## When not to use

- Pure code-quality review of a diff; use code review skills instead
- Writing the initial architecture from scratch; use architecture/design skills for synthesis
- Producing a formal ADR only; use ADR-focused skills for decision recording

## Review dimensions

Evaluate the architecture across these dimensions.

### 1. Problem fit

Check whether the structure matches the actual problem.

Questions:

- What requirements is this architecture trying to satisfy?
- Which constraints appear to be primary: scale, latency, reliability, compliance, cost, delivery speed, team familiarity?
- Is the architecture proportionate to the problem, or is it underpowered or overengineered?
- Does it solve today's problem only, or is it making justified bets on future needs?

### 2. Boundaries and cohesion

Check whether responsibilities are placed sensibly.

Questions:

- Are modules/services/components organized around cohesive responsibilities?
- Are boundaries explicit, or are concepts leaking across layers?
- Do modules change for one reason, or many unrelated reasons?
- Is shared logic truly shared, or duplicated with slight drift?

### 3. Dependencies and coupling

Check whether dependency flow supports maintainability.

Questions:

- Do dependencies point in the expected direction?
- Are there circular or backchannel dependencies?
- Are shared modules becoming dumping grounds?
- Does any area create excessive coordination cost because too many parts depend on it?

### 4. Operability

Check whether the system can be run and supported in practice.

Questions:

- Can the architecture be monitored, debugged, and operated by the actual team?
- Are failure modes visible and diagnosable?
- Are deployment, rollback, and recovery paths practical?
- Does the design introduce operational burden disproportionate to its value?

### 5. Reliability and failure handling

Check how the design behaves under stress and failure.

Questions:

- What are the critical dependencies and single points of failure?
- How does the system degrade when dependent components fail?
- Are retry, timeout, idempotency, fallback, or backpressure concerns handled where needed?
- Are consistency expectations explicit and realistic?

### 6. Security and trust boundaries

Check whether trust boundaries are visible and defended.

Questions:

- Where does untrusted input enter the system?
- Are authentication, authorization, and secrets-handling concerns placed in the right layers?
- Are data flows across trust boundaries explicit?
- Does the architecture centralize too much privilege in one place?

### 7. Delivery and evolution

Check whether the architecture can change safely.

Questions:

- Can teams modify one area without destabilizing unrelated areas?
- Does the architecture support incremental delivery?
- Are there clear seams for refactoring or replacement?
- Will future changes require broad cross-cutting edits?

## Review workflow

### Step 1: Establish context

Before judging the architecture, gather the minimum context:

- system purpose
- main requirements and constraints
- scale assumptions
- important integrations
- team or operational constraints
- any existing ADRs or design docs

If context is missing, say so explicitly and review against the constraints you can verify.

### Step 2: Identify the architecture shape

Summarize the architecture in plain language.

Examples:

- layered monolith with shared database
- service-oriented system with synchronous HTTP integration
- event-driven architecture with asynchronous consumers
- modular frontend with shared design system and server-state layer

Do not start with criticism. First state what the architecture is.

### Step 3: Review by dimension

Walk through the review dimensions above and note:

- strengths worth preserving
- weaknesses or mismatches
- open questions
- risks that deserve attention

Prioritize substantive concerns over cosmetic ones.

### Step 4: Distinguish issues by severity

Label findings clearly:

- **Critical** — likely to cause failure, severe coupling, major security/reliability risk, or inability to meet key requirements
- **Important** — meaningful architectural weakness or scaling/evolution risk
- **Consider** — worthwhile refinement, but not urgent
- **Open question** — missing information that could materially change the review

### Step 5: Recommend the next move

End with the most useful next action, such as:

- keep the architecture as-is
- proceed, but record assumptions in an ADR
- simplify an overbuilt design
- split a boundary more cleanly
- introduce observability before scaling further
- defer a major structural change until a measurable trigger appears

## Output format

```markdown
# Architecture Review

## Architecture Summary
[What the current/proposed architecture is]

## Context and Constraints
- [constraint]
- [constraint]

## Strengths
- [strength]
- [strength]

## Findings
### Critical
- [finding]

### Important
- [finding]

### Consider
- [finding]

### Open Questions
- [question]

## Recommendation
[Most useful next move]
```

## Anti-patterns

- reviewing without first stating the requirements or constraints
- prescribing a fashionable architecture without evidence it fits the problem
- treating every imperfection as a justification for a rewrite
- focusing only on ideal structure while ignoring operability and team capacity
- criticizing boundaries without proposing a clearer alternative or question
