---
name: resilience-patterns
description: Circuit breaker, retry, bulkhead, rate limiter, timeout, graceful degradation
---

# Resilience Patterns

Implementation patterns for building systems that handle failures gracefully.

## When to use

- A service calls external dependencies that can fail or be slow
- You need to prevent cascading failures across services
- You're building a distributed system with multiple downstream dependencies

## Instructions

1. **Identify failure points** — external APIs, databases, message queues
2. **Add timeouts** — set a maximum wait time for every external call. Fail fast instead of hanging
3. **Add retries with backoff** — exponential backoff + jitter prevents thundering herd
4. **Add circuit breaker** — after N consecutive failures, stop calling the failing service for a cooldown period
5. **Add bulkheads** — separate thread pools/connection pools per downstream dependency so one failure doesn't exhaust all resources
6. **Add rate limiting** — protect your own service from being overwhelmed
7. **Implement graceful degradation** — when a dependency is down, return a fallback (cached data, default value) instead of failing the whole request

## Example

```typescript
const circuit = new CircuitBreaker({
  failureThreshold: 5,
  resetTimeout: 30000, // 30 seconds
});

async function fetchWithResilience(url: string): Promise<Response> {
  return circuit.call(async () => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    try {
      const res = await fetch(url, { signal: controller.signal });
      return res;
    } finally {
      clearTimeout(timeout);
    }
  });
}
```

## Anti-patterns

- Infinite retries (exhausts resources, masks problems)
- No jitter in retry backoff (causes thundering herd on recovery)
- Single thread pool for all dependencies (one slow dependency blocks everything)
- No fallback when circuit is open (fail with grace, not with 500)
