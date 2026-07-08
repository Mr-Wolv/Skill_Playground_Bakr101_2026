---
name: engineering-phase-detector
description: >-
  Detect which SDLC phase (or phases) a request, artifact, or conversation is
  operating in, so downstream capabilities can be selected and sequenced
  correctly. Use when you need to classify where work stands before routing or
  orchestrating. A focused input to capability-router and capability-orchestrator.
category: engineering-mindset
source: custom
tags: [phase-detection, sdlc, classification, context, routing]
version: 1.0
---

# Engineering Phase Detector

Before selecting capabilities you must know which phase the work is in. This
skill classifies a request, diff, artifact, or conversation into one or more
SDLC phases using signal cues. It is the perception layer for
`capability-router` and `capability-orchestrator`.

## Phases and signal cues

- **Ideation & Concept** — vague idea, "should we...", opportunity, no spec yet.
- **Requirements & Specification** — PRD, spec, user story, interview, ADR draft,
  "what should it do".
- **Architecture & Design** — module/API/interface design, boundaries, tradeoffs,
  "how should we structure".
- **Implementation** — code being written, refactor, branch, "implement", diffs.
- **Testing & Quality** — tests, coverage, review, "why is this failing", lint.
- **Operations & Readiness** — deploy, canary, runbook, SLO, on-call, launch.
- **Incident & Learning** — outage, postmortem, root cause, "what broke".
- **Governance & Convergence** — catalog drift, duplication, ownership, audit,
  "skills out of sync".

## Detection procedure

1. Collect signals: the user's verbs, the artifacts present (spec? code? runbook?),
   and any phase markers in the repo (open PR = Implementation/Testing; ADR dir =
   Architecture; incident channel = Incident).
2. Score each phase by signal strength.
3. Report the top phase, plus any secondary phases the request also touches.
4. If signals conflict (e.g. "review the architecture of this code we just
   shipped"), report both and recommend `capability-orchestrator` to sequence.

## Output shape

    signals: diff in services/, no spec file, "review before merge"
    primary_phase: Implementation
    secondary_phase: Testing & Quality
    confidence: high
    route_to: capability-router (phase=Implementation)

## Notes

- Detection is cheap; do it before any heavy capability runs.
- A request can be multi-phase. Never force a single label when two are real.
- When confidence is low, prefer broader capabilities (`research-methodology`,
  `gap-analysis`) over a wrong specific one.
