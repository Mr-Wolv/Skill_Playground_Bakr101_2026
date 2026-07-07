---
name: toil-analysis-and-automation
description: Identify repetitive low-value manual work, quantify its cost, and design the right automation, guardrails, or workflow simplifications to eliminate toil sustainably.
---

# Toil Analysis and Automation

Use this skill when engineers are repeatedly doing manual, operational, or coordination-heavy work that should be simplified, automated, or removed.

This skill is about identifying toil systematically and deciding what kind of automation or workflow redesign will actually pay off.

## Use when

- a repeated manual workflow keeps consuming engineer time
- operational checklists are being executed by hand too often
- engineers complain that a process takes too many clicks or too many repeated commands
- a recurring support or maintenance task should probably be automated
- you need to prioritize automation work instead of automating everything indiscriminately

## Boundary

Use this skill to decide whether recurring manual work is truly toil, quantify its cost, and choose the right intervention: automation, simplification, standardization, or removal.

Do not use this skill when the real problem is launch planning, operational readiness, or change risk rather than repetitive low-value work.

Do not use this skill when the main problem is ownership, policy, or stewardship ambiguity rather than repetitive effort. For those cases, use the ownership and operations skills.

## Do not use when

- you already know the exact automation to implement and just want to build it
- the work is rare, high-judgment, and not repetitive enough to justify automation
- the problem is actually unclear ownership or policy rather than repetitive work

## What counts as toil

Treat work as toil when most of the following are true:

- manual
- repetitive
- low-leverage
- interrupt-driven
- procedurally understood
- does not create lasting product or platform value each time it is repeated
- expensive relative to its value

Examples:

- repeated service restarts with the same commands
- copy-paste release checklists run every week
- recurring dependency or environment cleanup steps
- repetitive incident triage tasks that could be scripted or standardized
- manual generation of reports that always follow the same structure

## Analysis workflow

1. **Describe the recurring workflow**
   - who does it?
   - how often?
   - what steps are repeated?
   - what dependencies or approvals are involved?

2. **Measure the cost**
   - frequency per week/month
   - average time per execution
   - interruption cost and context switching
   - error rate or inconsistency rate
   - impact on morale, latency, or reliability

3. **Classify the toil**
   - operational toil
   - review/coordination toil
   - data/reporting toil
   - environment/setup toil
   - release/deployment toil
   - documentation drift toil

4. **Find the root cause**
   - missing automation?
   - poor defaults?
   - poor discoverability?
   - missing validation?
   - fragmented ownership?
   - unnecessary policy complexity?

5. **Choose the right intervention**
   Not all toil should be solved with a script. Choose the smallest durable fix:
   - automate the task
   - simplify the workflow
   - remove unnecessary steps
   - add templates/checklists
   - improve self-service tooling
   - move validation earlier
   - improve ownership or routing

6. **Evaluate automation ROI**
   - implementation cost
   - maintenance cost
   - expected time saved
   - reliability improvement
   - reduction in interruptions and human error

7. **Recommend next action**
   - automate now
   - standardize first, then automate
   - document only
   - defer because the toil is too rare or too high-judgment

## Prioritization heuristic

Prioritize toil reduction when the work is:

- frequent
- expensive in aggregate
- error-prone
- latency-sensitive
- demoralizing
- blocking higher-value engineering work

Deprioritize when the work is:

- rare
- highly variable
- dependent on expert judgment each time
- likely to change soon enough that automation would rot immediately

## Good outputs

A good result usually includes:

- a clear description of the toil
- estimated cost per week or month
- root-cause analysis of why it exists
- recommended intervention
- expected payoff
- implementation sketch if automation is justified

## Typical trigger phrases

- "automate this repetitive process"
- "this is too manual"
- "find toil in this workflow"
- "what should we automate first"
- "reduce repetitive ops work"
- "turn this checklist into automation"
- "this process takes too many clicks"
