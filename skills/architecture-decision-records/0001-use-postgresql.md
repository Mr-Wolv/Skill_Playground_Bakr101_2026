# 0001: Use PostgreSQL as Primary Database

- Status: Accepted
- Date: 2024-01-10

## Context

We need a primary datastore for transactional application data. Requirements:
strong consistency, mature tooling, relational integrity, and operational
familiarity across the team.

## Decision

Use PostgreSQL as the primary relational database for all transactional data.

## Consequences

- Positive: ACID guarantees, rich SQL, extensions (PostGIS, pgvector), large
  operations ecosystem.
- Negative: vertical scaling ceiling; sharding is manual. Not ideal for
  unstructured or high-write-time-series data (see ADR 0002 for caching, ADR
  0020 for the MongoDB deprecation).
- Follow-up: define backup/restore and connection-pool policy before launch.
