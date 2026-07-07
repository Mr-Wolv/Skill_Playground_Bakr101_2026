---
name: unit-test-writer
description: Write unit tests for existing code using the project's test framework
---

# Unit Test Writer

Generates unit tests for existing functions, classes, and modules. Use when you need to add test coverage to existing code.

## When to use

- You have a function or class that needs unit tests
- The project already has a test framework (Vitest, Jest, pytest, JUnit)
- You want to follow existing test patterns in the codebase

## Instructions

1. **Read the target file** — understand its exports, types, and dependencies
2. **Detect the test framework** — check `package.json`, `pyproject.toml`, or `build.gradle` for the test runner
3. **Find existing test patterns** — look at neighboring test files for conventions (describe/it blocks, test functions, assertions)
4. **Identify test obligations** — for each exportable function/class:
   - Happy path (typical inputs → expected outputs)
   - Error cases (invalid inputs → expected errors)
   - Edge cases (empty strings, null values, boundary conditions)
   - Side effects (mutations, I/O, state changes)
5. **Generate tests** following the project's conventions
6. **Run the tests** to verify they pass

## Example

```typescript
// Given a function: export function add(a: number, b: number): number
// Generate:
import { describe, it, expect } from 'vitest';
import { add } from './math';

describe('add', () => {
  it('adds two positive numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  it('handles negative numbers', () => {
    expect(add(-1, 1)).toBe(0);
  });

  it('handles zero', () => {
    expect(add(0, 0)).toBe(0);
  });
});
```

## Edge cases to cover

- Functions with no parameters
- Async functions and promises
- Functions that throw errors
- Functions with side effects (mock/stub as needed)
- Functions with many parameters (test a representative subset)
