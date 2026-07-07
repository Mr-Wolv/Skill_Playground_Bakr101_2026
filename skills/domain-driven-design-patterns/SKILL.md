---
name: domain-driven-design-patterns
description: DDD tactical patterns — aggregates, value objects, domain events, bounded contexts
---

# Domain-Driven Design Patterns

Domain-Driven Design tactical and strategic patterns for modeling complex business domains.

## When to use

- Business logic is complex with many rules and invariants
- The domain language is well-established but not reflected in code
- Multiple teams work on different parts of the same system

## Instructions

1. **Identify the ubiquitous language** — terms, phrases, and rules the business uses
2. **Distinguish entities from value objects**:
   - **Entities** have identity (User, Order) — equality by ID
   - **Value objects** have no identity (Money, Address) — equality by all fields
3. **Define aggregates**:
   - An aggregate is a cluster of entities/vos treated as a unit
   - One aggregate root per cluster (e.g., Order is root, OrderItems are inside)
   - External references to the aggregate go through the root only
4. **Model domain events** — things that happened that other aggregates care about
5. **Map bounded contexts** — each context has its own ubiquitous language and model

## Example

```typescript
// Value Object
class Money {
  constructor(readonly amount: number, readonly currency: string) {}
  equals(other: Money): boolean {
    return this.amount === other.amount && this.currency === other.currency;
  }
}

// Aggregate Root
class Order {
  constructor(
    readonly id: OrderId,
    readonly items: OrderItem[],
    readonly total: Money,
  ) {}

  // Business rule: orders over $100 get free shipping
  qualifiesForFreeShipping(): boolean {
    return this.total.amount > 100;
  }
}
```

## Anti-patterns

- Making everything an entity (use value objects for immutable concepts)
- Exposing internal aggregate state (only the root should be visible outside)
- Cross-aggregate transactions (use eventual consistency via events)
