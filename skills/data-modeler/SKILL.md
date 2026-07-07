---
name: data-modeler
description: Design database schemas, entities, relationships, and data models
---

# Data Modeler

Designs database schemas and data models from functional requirements.

## When to use

- Designing a new database schema from requirements
- Reviewing an existing schema for normalization or performance issues
- Planning a schema migration that affects multiple tables

## Instructions

1. **Gather requirements** — what data needs to be stored, queried, and updated
2. **Identify entities** — nouns in the domain (User, Order, Product)
3. **Define relationships**:
   - 1:1 — User ↔ Profile
   - 1:N — User → Orders
   - M:N — Product ↔ Category (use junction table)
4. **Normalize to 3NF**:
   - 1NF — atomic columns, no repeating groups
   - 2NF — no partial dependencies on composite keys
   - 3NF — no transitive dependencies
5. **Add indexes** — on foreign keys, frequently queried columns, unique constraints
6. **Document** the schema with field types, constraints, and relationships

## Example

```sql
-- E-commerce schema
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE orders (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    total DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
```

## Edge cases

- Soft deletes (add `deleted_at` column instead of removing rows)
- Audit trails (created_at, updated_at on every table)
- Multi-tenant schemas (add tenant_id and partition by tenant)
- Time-series data (consider partitioning by time range)
