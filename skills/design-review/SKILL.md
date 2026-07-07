---
name: design-review
description: Review a proposed design against requirements, complexity, alternatives, usability, operability, and maintainability. Use when evaluating module designs, API/interface designs, UX flows, or technical proposals before implementation.
---

# Design Review

Review a design before it hardens into implementation.

This skill evaluates whether a proposed design is clear, proportionate, and fit for purpose. It is broader than visual design and narrower than full architecture review: use it for the shape of a solution, not the entire system structure.

## When to use

- Reviewing a module, component, API, workflow, or feature design before implementation
- Evaluating whether a design is too complex, too vague, or missing important cases
- Comparing design options against requirements and constraints
- Reviewing internal interfaces, user flows, or technical proposals
- Giving structured feedback on a design doc, PRD, proposal, or implementation plan

## When not to use

- Reviewing the architecture of a whole system; use `architecture-review`
- Reviewing code diffs; use code review skills
- Creating the first design from scratch; use design/synthesis skills for generation

## Review dimensions

### 1. Requirement fit

- Does the design address the actual problem?
- Are the success criteria explicit?
- Are important constraints represented in the design?

### 2. Simplicity and proportionality

- Is the design simpler than the problem requires, or more complex?
- Does it introduce abstractions that have not yet earned their cost?
- Can the same result be achieved with fewer moving parts?

### 3. Interface clarity

- Are inputs, outputs, and responsibilities explicit?
- Is the API or module surface understandable?
- Are naming and concepts aligned with the domain?

### 4. Edge cases and failure paths

- What happens on invalid input, missing state, timeouts, partial failure, or conflicting actions?
- Are fallback and error states explicit where needed?
- Does the design assume ideal conditions too heavily?

### 5. Maintainability and evolution

- Will this design be easy to modify safely?
- Are extension seams clear?
- Does it create duplication or future coordination cost?

### 6. Human and operational usability

- If user-facing, is the flow understandable and recoverable?
- If engineer-facing, is the design easy to reason about and support?
- Are observability, debugging, and support implications considered when relevant?

### 7. Alternatives and tradeoffs

- Were plausible alternatives considered?
- Is the chosen design justified, or merely one possible shape?
- What costs is the design accepting in exchange for its benefits?

## Review workflow

### Step 1: State the design under review

Summarize what is being proposed before criticizing it.

### Step 2: State the constraints

Identify the requirements, non-goals, and constraints that should govern the review.

### Step 3: Review by dimension

Capture:

- strengths worth preserving
- important weaknesses
- unanswered questions
- alternative shapes worth considering

### Step 4: Label findings

Use:

- **Critical**
- **Important**
- **Consider**
- **Open question**

### Step 5: Recommend the next move

Examples:

- proceed as designed
- simplify before implementation
- clarify interface contracts first
- document assumptions in an ADR or spec
- prototype one uncertain part before full build

## Output format

```markdown
# Design Review

## Design Summary
[What is being proposed]

## Constraints
- [constraint]
- [constraint]

## Strengths
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
[next move]
```

## Anti-patterns

- reviewing a design without stating the requirements first
- rejecting a design for not matching personal preference
- recommending architecture-scale changes for a local design problem
- ignoring edge cases because the happy path is elegant
- praising abstraction without checking whether it earned its cost
