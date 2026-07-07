---
name: dead-code-remover
description: Find and remove unused exports, files, dependencies, and unreachable code
---

# Dead Code Remover

Analyzes codebases to identify and safely remove dead code.

## When to use

- Cleaning up a codebase with accumulated unused code
- After a large refactoring that left orphaned modules
- Reducing bundle size for frontend applications

## Instructions

1. **Find unused exports** — check for exported functions/classes/variables that have zero import references
2. **Find orphaned files** — files with zero imports from any other source file
3. **Find unused dependencies** — check `package.json` / `requirements.txt` for packages no longer imported
4. **Find unreachable code** — code after a `return`, inside dead conditional branches, or behind constants that are always false
5. **Verify removal safety** — check that removing the code doesn't break anything (run tests, typecheck)
6. **Remove** — delete the code, run the test suite, verify nothing broke

## Safety checklist

- [ ] Run full test suite before and after
- [ ] Run typecheck (`tsc --noEmit`, `mypy`, etc.)
- [ ] Check for dynamic imports or `require()` that reference removed files
- [ ] Verify no runtime errors in the affected areas
- [ ] For unused dependencies, confirm no transitive dependency requires it

## Anti-patterns

- Removing code without checking for dynamic references (e.g., `require(name)` where name is a variable)
- Removing an exported function without checking external consumers (it might be a public API)
- Deleting a file that's generated or auto-imported by a framework (e.g., Next.js pages)
