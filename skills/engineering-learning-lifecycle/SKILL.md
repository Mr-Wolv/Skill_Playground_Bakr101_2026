---
name: engineering-learning-lifecycle
description: >-
  Run the post-task Engineering Learning Lifecycle after any completed
  engineering task. Composes existing capabilities into a deliberate,
  evidence-driven reflection + decision loop: outcome eval, root-cause
  classification, repository-support assessment, convergence/entropy gate,
  and an institutionalization decision that strongly prefers "no change."
  Use when a task finished (or failed), after a bug/fix, after CI catches a
  defect, or when deciding whether a lesson deserves to become permanent
  repository knowledge. Not for the live execution of the task itself.
category: engineering-mindset
source: custom
tags: [learning, reflection, retrospective, institutional-knowledge, convergence, post-task, entropy]
version: 1.0
---

# Engineering Learning Lifecycle

A permanent post-task subsystem. It turns engineering work into institutional
memory *without* inflating the repository. **Most tasks should produce no
repository change.** This skill is the discipline, not a new body of knowledge.

## Why this skill exists (non-duplication note)

The platform already owns the *pieces*: `postmortem`, `quality-postmortem`,
`root-cause-analysis`, `five-whys-analysis`, `assumption-and-bias-check`,
`change-risk-assessment`, `catalog-consistency-auditor`, `long-term-engineering-mindset`,
`autonomous-learner`, `capability-orchestrator`. What was missing is the
**orchestration + decision gate** that runs *after* a task and refuses
unjustified change. This skill adds only that — it delegates analysis to the
existing skills above and never restates their content.

## Core Principle

Never ask "What can I add to the repository?" Ask: "What did engineering teach
us, and does that lesson deserve to become institutional knowledge?"

## Lifecycle Stages

Run in order. Each stage has a decision point. Stop early when the answer is
"No change required."

1. **Engineering Outcome** — Did it succeed? If not: why, and which decisions
   caused it? (Delegate failure analysis to `postmortem` / `quality-postmortem`
   for anything non-trivial.)
2. **Root Cause Classification** — Classify: missing knowledge / weak capability /
   unclear docs / governance gap / missing automation / workflow friction /
   insufficient reasoning / architectural inconsistency / **implementation
   defect**. *Do not assume "missing capability" — most root causes are defects
   or doc gaps.*
3. **Repository Support Assessment** — Did the platform guide this task well?
   Yes → likely no change. No → pinpoint the precise gap.
4. **Existing Capability Analysis** — Can the gap be closed by refining a
   capability, clarifying docs, improving governance/automation/orchestration,
   or strengthening reasoning? **Exhaust these before any new artifact.**
5. **Generalization Test** — Will this lesson help *multiple* future projects?
   No → do not modify the repo. Yes → continue.
6. **Stability Test** — Does the change strengthen long-term architecture, or
   merely patch today's problem? Prefer enduring value.
7. **Convergence Gate** (see below) — The entropy check. Blocks capability
   inflation, duplication, doc divergence, governance inconsistency,
   fragmentation, cognitive overload.
8. **Institutionalization Decision** — Apply the Decision Framework. Default
   outcome is "No change required."

## Decision Framework

Possible outcomes, in preference order:

1. No repository change
2. Refine an existing capability
3. Improve governance
4. Improve documentation
5. Improve automation
6. Improve validation
7. Improve orchestration
8. Improve repository organization
9. Improve metadata
10. Merge capabilities
11. Deprecate an obsolete capability
12. Introduce a new capability (**last resort**)

## Evidence Model

A "lesson" only qualifies for institutionalization with evidence, not anecdote:

- **Hard**: failed CI/gate after a change, reproduced defect, user correction
  with a specific fix, measured regression.
- **Soft**: repeated invocation friction, naming/trigger ambiguity, recurring
  overlap encountered in real work.
- **Rejected**: one-off confusion, hypothetical "what if", activity without
  outcome.

Temporary observations and project-specific lessons NEVER modify the repo.
Only **institutional knowledge** (reusable across projects, stable over time)
may.

## Reflection Model (ask, do not skip)

- Was the outcome successful? What enabled it? What inhibited it?
- Did the repo provide sufficient guidance? Were V1.0 principles followed?
- Did governance help? Was documentation sufficient? Did automation reduce
  effort? Did reasoning quality meet the bar?
- Would future engineering *materially* improve if this became institutional?

## Convergence Controls

Every proposed change must *reduce* entropy: less duplication, less ambiguity,
higher cohesion, better composability/discoverability/consistency/maintainability.
Reject changes that solve an isolated problem while weakening the whole. The
repo should become more elegant, not larger.

## Governance / Documentation / Automation Integration

- **Governance**: respect `AGENTS.md` (mirror parity, single source of truth,
  sync model). Any `skills/` change goes through the same export path.
- **Documentation**: keep `README.md`, `SKILL-CATALOG.md`, `SKILL.md`,
  `skills.json`, `docs/*` aligned — use `catalog-consistency-auditor` after any
  catalog-affecting change.
- **Automation**: the repo's own `gate.py` (incl. `assert_merged_topology()`)
  is the automated guardrail. If a learning implies a durable check, prefer
  adding it to `gate.py`/the tripwire over a doc.

## Repository Evolution Workflow

When a change is justified:
1. Fix in the merged store (B==C); keep scope minimal.
2. Run `python scripts/sync_and_validate.py` (export + validate + parity).
3. Pass `python scripts/gate.py` before commit.
4. Commit with a message stating the evidence and the Lifecycle stage that
   authorized it.

## Risk Analysis

- **Over-learning**: changing the repo after every task → inflation. Mitigated
  by the default "no change" and the generalization/stability gates.
- **Under-learning**: silently repeating mistakes. Mitigated by always running
  stages 1–3, even when the outcome is "no change."
- **Capability inflation**: new skills for one-off needs. Mitigated by
  "introduce new capability = last resort" + convergence gate.
- **Doc divergence**: catalogs drift from reality. Mitigated by
  `catalog-consistency-auditor` + the manifest tripwire in `gate.py`.

## Operational Guidelines

- Keep it cheap: a full lifecycle pass is seconds of thought, not a document.
- For trivial successes: stages 1–3 mentally, stop. No artifact.
- For failures/defects: engage `postmortem` / `root-cause-analysis` /
  `five-whys-analysis` before deciding.
- The highest form of learning is not changing often — it is knowing precisely
  when change is justified.
