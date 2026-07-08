---
name: capability-router
description: >-
  Map an engineering request to the right capability or capabilities by detecting
  the active SDLC phase and routing to the matching skills. Use when you know the
  phase (or can infer it) and need the correct skill name(s) without building a
  full execution plan. The lightweight sibling of capability-orchestrator.
category: engineering-mindset
source: custom
tags: [routing, discovery, selection, sdlc, phase-mapping]
version: 1.0
---

# Capability Router

A lookup-and-route layer for engineering capabilities. Given a request and (if
known) its SDLC phase, it returns the capability name(s) to invoke, plus the
phase it inferred. It does not sequence or compose — for that use
`capability-orchestrator`. It is the "which skill should I call?" answer.

## When to use

- You have a request and need the correct skill name(s).
- You want phase-aware routing rather than guessing by keyword.
- You are building a dispatcher, an agent front-end, or a menu of capabilities.

## Routing table (phase -> capabilities)

These are representative entries from the Skill Playground library; extend per
your own catalog.

- **Ideation & Concept**: `idea-refine`, `research`, `product-discovery`
- **Requirements & Specification**: `interview-me`, `grill-me`,
  `spec-driven-development`, `to-prd`, `domain-modeling`, `ubiquitous-language`
- **Architecture & Design**: `architecture-patterns`, `architecture-review`,
  `design-review`, `api-and-interface-design`, `codebase-design`,
  `architecture-decision-records`, `backward-compatibility-and-change-management`
- **Implementation**: `incremental-implementation`, `tdd`, `test-driven-development`,
  `typed-holes-refactor`, `request-refactor-plan`, `planning-and-task-breakdown`
- **Testing & Quality**: `code-review`, `code-review-and-quality`,
  `code-review-excellence`, `unit-test-writer`, `integration-test-writer`,
  `web-quality-audit`, `visual-regression-testing`
- **Operations & Readiness**: `operational-readiness-review`,
  `change-risk-assessment`, `slo-implementation`, `shipping-and-launch`,
  `service-ownership-and-lifecycle-management`, `incident-runbook-templates`
- **Security**: `security-pen-testing`, `threat-mitigation-mapping`,
  `attack-tree-construction`, `security-requirement-extraction`
- **Incident & Learning**: `incident-response`, `postmortem`, `root-cause-analysis`,
  `five-whys-analysis`, `failure-analysis`
- **Documentation & ADRs**: `documentation-and-adrs`, `readme-writer`,
  `code-documenter`, `api-documenter`, `document-reviewer`
- **Governance & Convergence**: `catalog-consistency-auditor`,
  `codeowners-and-review-routing`, `dependency-graph`, `repository-archaeology`,
  `triage`, `wayfinder`

## Routing rules

1. Infer phase from the request verbs and artifacts (writes spec -> Requirements;
   reviews architecture -> Architecture; ships -> Operations).
2. Return the most specific capability first, broader ones as alternates.
3. If the request spans phases, return the entry points for each and suggest
   `capability-orchestrator` to sequence them.
4. If no capability fits, say so and route to the nearest analysis skill
   (`research-methodology`, `gap-analysis`).

## Output shape

    request: "review this API design before we build it"
    phase:   Architecture & Design
    route:   design-review (primary)
             architecture-review (alternate)
             api-and-interface-design (if design not started)
    next:    hand result to code-review after implementation
