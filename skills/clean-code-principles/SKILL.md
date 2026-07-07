---
name: clean-code-principles
description: Teach Clean Code — naming, functions, DRY, KISS, SOLID, code smells
---

# Clean Code Principles

Teaches and applies Clean Code practices for writing readable, maintainable software.

## When to use

- Reviewing code for readability and maintainability
- Writing new code and want to follow best practices
- Refactoring messy or hard-to-understand code

## Instructions

1. **Check naming** — names should reveal intent. Avoid abbreviations, single-letter variables (except loop indices), and misleading names
2. **Check function size** — functions should do ONE thing. If you can't describe it in a short sentence, it's doing too much
3. **Check for duplication (DRY)** — repeated blocks should be extracted into shared functions
4. **Check for simplicity (KISS)** — prefer simple solutions over clever ones
5. **Check SOLID adherence**:
   - **S**ingle Responsibility — each class/function has one reason to change
   - **O**pen/Closed — open for extension, closed for modification
   - **L**iskov Substitution — subtypes are substitutable for their base types
   - **I**nterface Segregation — keep interfaces focused and small
   - **D**ependency Inversion — depend on abstractions, not concretions

## Code smells to flag

- Long methods (> 20 lines)
- Deep nesting (> 3 levels)
- Primitive obsession (using strings/ints instead of value objects)
- Shotgun surgery (one change requires modifying many files)
- Feature envy (a method uses more from another class than its own)
