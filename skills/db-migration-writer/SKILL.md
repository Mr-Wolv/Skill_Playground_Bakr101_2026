---
name: db-migration-writer
description: Write versioned SQL and ORM migration files for database schema changes
---

# DB Migration Writer

Generates versioned database migration files for SQL databases and ORM frameworks.

## When to use

- Adding a new table or column to the database
- Modifying existing schema (renaming, changing types)
- Writing rollback scripts for safe deployments

## Instructions

1. **Understand the migration framework** — Flyway, Liquibase, Prisma, TypeORM, Alembic, or raw SQL
2. **Write the forward migration** — the SQL/ORM commands to apply the change
3. **Write the rollback migration** — the reverse commands to undo the change
4. **Follow naming conventions** — `V{version}__{description}.sql` (Flyway) or `{timestamp}-{description}.ts` (TypeORM)
5. **Add safety checks** — use `IF NOT EXISTS` / `IF EXISTS` where appropriate
6. **Verify** the migration runs and rolls back cleanly

## Example

```sql
-- V1__create_users_table.sql (forward)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- V1__create_users_table.sql (rollback)
DROP TABLE IF EXISTS users;
```

## Edge cases

- Data migrations (backfill existing rows before adding NOT NULL constraints)
- Long-running migrations on large tables (use batching)
- Migrations that depend on other migrations (ensure ordering)
- Zero-downtime migrations (add columns as nullable first, backfill, then add NOT NULL)
