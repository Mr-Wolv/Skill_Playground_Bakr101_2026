# 0002: Caching Strategy with Redis

- Status: Accepted
- Date: 2024-01-12

## Context

Read-heavy workloads against PostgreSQL (ADR 0001) are introducing latency and
load. We need a cache to absorb repeated reads.

## Decision

Introduce Redis as a read-through / write-through cache in front of hot
PostgreSQL read paths.

## Consequences

- Positive: lower p95 latency, reduced primary DB load.
- Negative: a new consistency boundary — cache invalidation policy required;
  stale-read risk if invalidation is wrong.
- Follow-up: document TTL and invalidation rules; add a cache-stampede guard.
