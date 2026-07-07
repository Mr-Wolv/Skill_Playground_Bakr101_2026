---
name: flyway-migration-patterns
description: Versioned DB migrations with Flyway — naming conventions, safety patterns, rollback strategies
---

# Flyway Migration Patterns

Patterns and conventions for managing database schema changes with Flyway.

## When to use

- Using Flyway for database migration management
- Setting up migration naming conventions for a team
- Planning a complex schema migration that needs rollback support

## Instructions

1. **Follow Flyway naming conventions** — `V{version}__{description}.sql` (e.g., `V1__create_users.sql`)
2. **Version strategies**:
   - **Integer versions**: V1, V2, V3 — simple, linear
   - **Timestamp versions**: V20260101__description.sql — avoids merge conflicts
   - **Semantic versions**: V1.0.0, V1.1.0 — maps to application versions
3. **Write idempotent migrations** — use `IF NOT EXISTS`, `IF EXISTS` for safety
4. **Keep migrations small** — one logical change per migration; avoid mixing schema + data changes
5. **Test both forward and rollback** — ensure `flyway undo` works before deploying

## Example

```sql
-- V2__add_email_to_users.sql
ALTER TABLE users ADD COLUMN email VARCHAR(255);
-- V2__add_email_to_users__undo.sql
ALTER TABLE users DROP COLUMN email;
```

## Safety patterns

- Never edit a migration that has been applied to production — create a new one
- Use `flyway check` or `-outOfOrder=true` carefully
- For data migrations, wrap in a transaction and test on a copy of production
