---
name: regex-builder
description: Build, explain, and test regular expressions interactively
---

# Regex Builder

Builds, explains, and tests regular expressions interactively.

## When to use

- You need to match, extract, or validate text patterns
- You have a regex you don't understand
- You want to test a regex against sample inputs

## Instructions

1. **Understand the requirement** — what text needs to match? What should be captured?
2. **Build the regex step by step**:
   - Start with the literal characters
   - Add character classes (`[a-z]`, `\d`, `\w`, `.`)
   - Add quantifiers (`*`, `+`, `?`, `{n,m}`)
   - Add anchors (`^`, `$`, `\b`)
   - Add groups and captures (`(...)`, `(?:...)`)
3. **Test against inputs** — run the regex against positive and negative cases
4. **Explain existing regex** — break it down token by token in plain English
5. **Optimize** — avoid catastrophic backtracking (nested quantifiers)

## Common patterns

```regex
# Email (simple)
^[\w.+-]+@[\w-]+\.[\w]{2,}$

# URL
https?://[\w.-]+(?:/[\w./%-]*)?(?:\\?[\w&=]+)?

# Date (YYYY-MM-DD)
^\d{4}-\d{2}-\d{2}$

# Phone (US)
^\+?1?\d{10}$

# Hex color
^#?([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$
```

## Anti-patterns

- Using regex to parse HTML/XML (use a proper parser)
- Overly complex regex that's unreadable (add comments with `/x` flag or use named groups)
- Greedy matching when lazy would be correct (`.*` vs `.*?`)
- Catastrophic backtracking with nested quantifiers (like `(a+)+b`)
- Not anchoring patterns (can match unintended substrings)
