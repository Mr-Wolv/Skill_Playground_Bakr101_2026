---
name: code-commenter
description: Add inline explanatory comments to clarify complex or non-obvious code
---

# Code Commenter

Adds inline comments to explain complex logic, business rules, and non-obvious code patterns.

## When to use

- Code contains complex algorithms or business logic
- A workaround or hack needs explanation
- The intent behind code is not obvious from reading it

## Instructions

1. **Read the code** to understand what it does and why
2. **Add comments for the "why"** — explain the reasoning behind decisions, not what the code does (the code already says what)
3. **Reference external context** — link to issue numbers, spec documents, or RFCs
4. **Mark workarounds** — annotate with `// HACK:` or `// TODO: refactor when...`
5. **Respect existing style** — match the project's commenting conventions

## Examples

```typescript
// Good: explains WHY
// Retry up to 5 times because nanoid(7) collisions are astronomically rare,
// but a bug or seed issue could cause repeated collisions.
for (let attempt = 0; attempt < 5; attempt++) { ... }

// Bad: explains WHAT (redundant)
// Increment the counter by 1
counter += 1;
```

## Guidelines

- Don't comment self-documenting code (`const name = user.name;` needs no comment)
- Do comment when the code contradicts the obvious (e.g., inverted logic, performance tricks)
- Keep comments up to date when the code changes (stale comments are worse than none)
