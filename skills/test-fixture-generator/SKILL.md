---
name: test-fixture-generator
description: Generate reusable test factories, seed data, and mock objects
---

# Test Fixture Generator

Creates reusable test data factories, seed data for database-backed tests, and mock objects for external dependencies.

## When to use

- Multiple tests need similar entity instances
- You need to populate a test database with realistic data
- External services need to be mocked/stubbed consistently

## Instructions

1. **Analyze the domain model** — read entity/type definitions to understand field types and constraints
2. **Create factory functions** — one per entity type, with sensible defaults
3. **Support overrides** — allow callers to override specific fields
4. **Support sequences** — auto-increment IDs, unique timestamps
5. **Create relationships** — factory for child entities that can link to parent factories
6. **Add builders** (optional) — fluent builder pattern for complex entities

## Example

```typescript
// Factory pattern
export function createUser(overrides: Partial<User> = {}): User {
  return {
    id: faker.string.uuid(),
    name: 'Test User',
    email: 'test@example.com',
    createdAt: new Date(),
    ...overrides,
  };
}

// Usage in tests
const admin = createUser({ role: 'admin' });
const guest = createUser({ role: 'guest', name: 'Guest User' });
```

## Patterns

- **Object Mother**: single place defining canonical test objects
- **Builder**: fluent API for step-by-step construction
- **Seed Data**: SQL/JSON files for database-backed tests
- **Mock Factories**: create mock service responses

## Edge cases

- Nullable fields (test with and without)
- Required relationships (ensure they're always populated)
- Circular references (use lazy evaluation)
- Date/time fields (use fixed seeds for reproducible tests)
