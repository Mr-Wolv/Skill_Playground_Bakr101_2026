---
name: spring-data-jpa-patterns
description: N+1 detection, JOIN FETCH, EntityGraphs, batch fetching, pagination optimization
---

# Spring Data JPA Patterns

Optimization patterns for JPA and Hibernate in Spring Boot applications.

## When to use

- Queries are slow due to lazy loading (N+1 problem)
- You need to optimize database access patterns
- Reviewing data access code for performance issues

## Instructions

1. **Detect the N+1 problem** — check if a query triggers N additional queries for related entities
2. **Fix with JOIN FETCH** — use `JOIN FETCH` in JPQL to eagerly load associations in a single query
3. **Fix with EntityGraphs** — use `@EntityGraph(attributePaths = {...})` for dynamic fetch plans
4. **Use batch fetching** — configure `@BatchSize` for collections that can't be eagerly fetched
5. **Optimize pagination** — use `Pageable` with count queries for large datasets
6. **Consider DTO projections** — use `SELECT new com.example.UserDto(e.id, e.name)` instead of loading full entities

## Example

```java
// ❌ N+1: Each user triggers a query for their orders
List<User> users = userRepository.findAll();

// ✅ Fix: JOIN FETCH
@Query("SELECT u FROM User u JOIN FETCH u.orders")
List<User> findAllWithOrders();

// ✅ Fix: EntityGraph
@EntityGraph(attributePaths = {"orders", "profile"})
@Query("SELECT u FROM User u")
List<User> findAllWithRelations();
```

## Edge cases

- Multiple bag fetches (can cause Cartesian products — use Set instead of List)
- Pagination with JOIN FETCH (Hibernate warns — use DTO projection instead)
- Large collections (batch fetching is safer than eager fetching everything)
