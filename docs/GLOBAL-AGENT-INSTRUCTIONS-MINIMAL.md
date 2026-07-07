# Global Agent Instructions — Minimal

Use this when you want better cross-project agent behavior without adding much standing instruction weight.

```md
## Global Working Style

- Prefer relevant existing skills when the request clearly matches a skill's scope.
- Prefer improving or extending existing structures before creating new ones.
- Treat coherence, maintainability, and discoverability as first-class engineering goals.
- Be skeptical of duplication: prefer merge, clarification, or extension before multiplication.

## Expansion Discipline

Do not recommend creating something new by default.
Prefer this order:
1. improve an existing capability
2. improve naming, triggers, examples, or discoverability
3. split only when boundaries are genuinely overloaded
4. merge when overlap is the real problem
5. add something new only when it is clearly distinct and repeatedly valuable
```

## Best for

- low-friction always-on use
- broad applicability across many repositories
- minimizing instruction collisions
