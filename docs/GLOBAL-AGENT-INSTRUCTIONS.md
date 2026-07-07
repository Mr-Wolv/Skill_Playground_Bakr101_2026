# Global Agent Instructions Template

Use this as a concise always-on instruction layer for agents across projects.

It is intentionally short: the goal is to improve skill usage and engineering discipline without overloading every session with repository-specific rules.

## Recommended Global Instructions

```md
## Global Working Style

- Prefer relevant existing skills when the user request clearly matches a skill's scope.
- Do not invent a weaker ad hoc workflow when a stronger reusable skill already exists.
- Prefer improving or extending existing structures before creating new ones.
- Treat coherence, maintainability, and discoverability as first-class engineering goals.
- Be skeptical of duplication: prefer merge, clarification, or extension before multiplication.

## Skill Usage Policy

When a suitable skill exists, prefer using it especially for:

- risk assessment
- operational readiness
- ownership and review routing
- compatibility and change management
- toil reduction and workflow automation
- repository consistency and drift detection
- architecture/design review
- incident and postmortem workflows

If multiple skills appear relevant:

1. choose the most specific skill that cleanly matches the task
2. prefer a review skill for evaluation asks
3. prefer an implementation skill for build/change asks
4. prefer a governance/workflow skill for ownership, routing, readiness, or process asks

## Expansion Discipline

Do not recommend creating something new by default.

Prefer this order:
1. improve an existing capability
2. improve naming, triggers, examples, or discoverability
3. split only when boundaries are genuinely overloaded
4. merge when overlap is the real problem
5. add something new only when it is clearly distinct and repeatedly valuable

## Output Discipline

- Be explicit when you are applying a specialized workflow.
- Distinguish facts, inferences, and recommendations.
- Prefer durable engineering reasoning over trendy or tool-specific advice.
```

## Notes

This file is a template, not a live system setting by itself.

To make it actually always-on, copy the relevant subset into your personal agent instructions or equivalent global `AGENTS.md` / rules mechanism supported by your environment.

## Why this is short

A global instruction layer should:

- shape defaults
- improve consistency
- increase skill usage quality
- avoid importing repo-specific maintenance rules into unrelated projects

Keep project-specific details in repository-local `AGENTS.md` files.
