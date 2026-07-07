---
name: distributed-systems-patterns
description: CAP theorem, consistency models, saga patterns, consensus algorithms, data partitioning
---

# Distributed Systems Patterns

Patterns and principles for designing and debugging distributed systems.

## When to use

- Designing a system that runs across multiple nodes
- Understanding tradeoffs between consistency, availability, and partition tolerance
- Implementing distributed transactions or data replication

## Instructions

1. **Identify the system's requirements** — consistency vs. availability tradeoff (CAP theorem)
2. **Choose a consistency model**:
   - **Strong consistency** — all reads see the latest write (use consensus: Raft, Paxos)
   - **Eventual consistency** — reads may see stale data temporarily (use CRDTs, gossip)
   - **Causal consistency** — causally related operations are seen in order
3. **Design data partitioning** — hash-based (consistent hashing) or range-based sharding
4. **Handle distributed transactions**:
   - **Saga pattern** — sequence of local transactions with compensating actions on failure
   - **Two-phase commit** — coordinator ensures all nodes agree (higher latency)
5. **Implement replication** — leader-follower, multi-leader, leaderless

## Key patterns

- **Saga orchestration**: a central coordinator tells each service what to do
- **Saga choreography**: each service emits events that trigger the next step
- **Idempotency keys**: ensure operations can be safely retried
- **Outbox pattern**: write events to a local table first, then reliably publish

## Anti-patterns

- Distributed transactions across many services (use sagas instead)
- Ignoring network partitions (they will happen — design for them)
- Synchronous calls between services in a critical path
