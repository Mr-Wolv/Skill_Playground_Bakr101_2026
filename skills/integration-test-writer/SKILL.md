---
name: integration-test-writer
description: Write integration tests for API endpoints, database flows, and service interactions
---

# Integration Test Writer

Generates integration tests that exercise real components together — API endpoints talking to databases, services calling other services.

## When to use

- You need to verify an API endpoint works end-to-end
- You want to test database operations with a real or containerized database
- You need to validate service-to-service communication

## Instructions

1. **Identify the surface** — API routes, GraphQL resolvers, message handlers, or database repositories
2. **Check for test infrastructure** — supertest for HTTP, Testcontainers for databases, fixtures for seed data
3. **Set up fixtures** — create test data matching the expected domain models
4. **Test each operation**:
   - Create: POST with valid payload → 201 + correct response body
   - Read: GET existing resource → 200 + correct data
   - Update: PUT/PATCH → 200 + updated fields
   - Delete: DELETE → 204 or 200 (resource removed)
   - Error: invalid payload → 4xx + descriptive error message
5. **Verify side effects** — check the database state after mutations
6. **Clean up** — remove test data after each test (or use transactions)

## Example

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import request from 'supertest';
import { createApp } from '../src/app.js';

describe('POST /shorten', () => {
  it('creates a short URL and persists it', async () => {
    const app = createApp(testStore);
    const res = await request(app)
      .post('/shorten')
      .send({ url: 'https://example.com' });
    expect(res.status).toBe(201);
    expect(res.body.short_code).toHaveLength(7);
  });
});
```

## Edge cases

- Database connection failures (graceful handling)
- Concurrent writes to the same resource
- Large payloads near size limits
- Missing required fields in request bodies
