---
name: api-documenter
description: Generate API documentation from code, specifications, and endpoint definitions
---

# API Documenter

Generates comprehensive API documentation from code analysis and endpoint definitions.

## When to use

- An API exists but lacks documentation
- You need to generate OpenAPI/Swagger specs from code
- Onboarding integrators to use your API

## Instructions

1. **Analyze the codebase** — find route definitions, controllers, handlers, and request/response types
2. **Extract endpoint metadata** — method, path, parameters, request body, response shape
3. **Generate OpenAPI spec** (`openapi.json` or `openapi.yaml`) with:
   - Paths and operations
   - Request/response schemas
   - Authentication requirements
   - Example requests and responses
4. **Generate user-facing docs** — markdown or HTML rendered from the spec
5. **Verify accuracy** — ensure documented endpoints match actual routes

## Documentation structure

```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
paths:
  /users/{id}:
    get:
      summary: Get a user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
```

## Edge cases

- Versioned APIs (document multiple versions separately)
- Deprecated endpoints (mark with `deprecated: true`)
- WebSocket endpoints (document event names and payload shapes)
- Error responses (document all possible error codes and their meanings)
