---
name: tech-debt-tracker
description: Scan codebase for TODOs, complexity hotspots, code smells, and tech debt indicators
---

# Tech Debt Tracker

Scans codebases for technical debt indicators and generates prioritized remediation plans.

## When to use

- Onboarding to a new codebase and need a quick assessment
- Before a major refactoring effort
- As part of a regular codebase health review

## Instructions

1. **Scan for TODOs/FIXMEs/HACKs** — search across all source files. Group by category (feature gaps, known bugs, performance hacks)
2. **Measure complexity** — check cyclomatic complexity of functions. Flag anything > 10
3. **Detect code smells**:
   - Methods longer than 20 lines
   - Classes with more than 10 methods or 300 lines
   - Deep nesting (> 3 levels)
   - God classes (classes doing too many things)
   - Feature envy
4. **Check for deprecated patterns** — outdated libraries, removed APIs, legacy conventions
5. **Generate a prioritized report** — order by impact and effort

## Report format

```markdown
# Tech Debt Report

### Critical (fix within this sprint)
- [ ] `src/service.ts:45` — TODO: Fix race condition in concurrent writes

### Moderate (schedule for next sprint)
- [ ] `src/app.ts:120` — Function handleRequest() has complexity 23

### Low (add to backlog)
- [ ] `src/utils.ts:3-89` — Deprecated utility functions (migrated to v2)
```

## Anti-patterns

- Reporting every single TODO as critical (use judgment)
- Ignoring the business impact of the debt (prioritize by user-facing impact)
- Creating debt without offering remediation suggestions
