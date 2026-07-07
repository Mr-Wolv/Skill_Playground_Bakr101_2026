---
name: code-documenter
description: Add docstrings and code documentation following language conventions
---

# Code Documenter

Adds comprehensive inline documentation to source code following language-specific conventions.

## When to use

- Functions and classes lack documentation
- You need to generate API docs from code
- Improving code readability for maintainers

## Boundary

Use this skill for docstrings, API comments, and code-level documentation that describes the contract of functions, classes, modules, or exports.

Do not use this skill for high-level repository docs, ADRs, or README authoring. Use `documentation-and-adrs`, `architecture-decision-records`, or `readme-writer` for those.

Do not use this skill when the main need is a few targeted inline comments explaining tricky intent inside an implementation body. For that, use `code-commenter`.

## Instructions

1. **Read the target file** — understand each export, its parameters, and return value
2. **Follow language conventions**:
   - TypeScript/JavaScript: JSDoc/TSDoc (`@param`, `@returns`, `@throws`)
   - Python: docstrings (`:param`, `:returns:` or Google/NumPy style)
   - Java: Javadoc (`@param`, `@return`, `@throws`)
   - Rust: doc comments (`///`, `//!`)
3. **Document what, not how** — explain the purpose and contract, not the implementation details
4. **Include examples** for non-obvious usage patterns
5. **Mark incomplete or experimental code** with `@deprecated` or `@beta` tags

## Example (TypeScript)

```typescript
/**
 * Shortens a URL by generating a unique 7-character code.
 *
 * @param url - The URL to shorten. Must start with http:// or https://.
 * @returns The created UrlEntry with the generated short code.
 * @throws {Error} If the URL is empty or doesn't start with http.
 *
 * @example
 * const entry = shortenUrl('https://example.com/long-url');
 * console.log(entry.short_code); // 'aB3xK9m'
 */
export function shortenUrl(url: string): UrlEntry { ... }
```

## Guidelines

- Every public function/class gets a doc comment
- Every parameter is documented with its expected range or format
- Return values describe what they represent, not their type
- Thrown errors are explicitly listed
