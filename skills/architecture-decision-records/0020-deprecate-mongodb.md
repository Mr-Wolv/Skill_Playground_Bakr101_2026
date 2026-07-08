# 0020: Deprecate MongoDB

- Status: Accepted
- Date: 2024-01-15
- Supersedes: [0003-mongodb-user-profiles.md](0003-mongodb-user-profiles.md)

## Context

The MongoDB user-profile store (ADR 0003) added a second datastore, operational
toil, and dual-write complexity without clear benefit. Team preference is a
single primary store (PostgreSQL, ADR 0001).

## Decision

Deprecate MongoDB. Migrate user profiles to PostgreSQL as JSONB columns (or a
profiles table), then decommission the MongoDB deployment.

## Consequences

- Positive: one datastore, simpler backups, fewer failure modes.
- Negative: migration effort; a dual-write transition window where both stores
  stay in sync.
- Follow-up: define the cutover plan, backfill script, and rollback before
  deleting the MongoDB instance.
