---
name: clean-architecture-principles
description: Teach Clean Architecture layers, dependency rule, and architectural boundaries
---

# Clean Architecture Principles

Teaches and applies Clean Architecture principles for structuring maintainable, testable applications.

## When to use

- Designing a new application's architecture
- Refactoring a monolithic codebase into layers
- Reviewing architecture for dependency rule violations

## Instructions

1. **Identify the layers** in the codebase:
   - **Entities** — enterprise-wide business rules (POJOs, records)
   - **Use Cases** — application-specific business rules (services, interactors)
   - **Interface Adapters** — controllers, presenters, gateways
   - **Frameworks** — Express, Spring, React, database drivers
2. **Verify the dependency rule** — dependencies point INWARD (Frameworks → Adapters → Use Cases → Entities). Outer layers depend on inner layers, never the reverse.
3. **Check boundary isolation** — inner layers (Entities, Use Cases) must not import framework code or annotations
4. **Look for violations** — are any use-case classes importing HTTP request objects? Are entities annotated with JPA?

## Key patterns

- **Dependency Injection** — outer layers create and inject dependencies into inner layers
- **Repository interfaces** — define in Use Case layer, implement in Adapter layer
- **DTOs** — never pass framework-specific request objects into use cases

## Anti-patterns

- Adding `@Entity` or `@Table` annotations to domain entities (couples them to JPA)
- Services directly calling HTTP or database code (should go through interfaces)
- Business logic in controller methods (belongs in use cases)
