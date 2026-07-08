# Code Review — Performance Checklist

A focused checklist for reviewing **code changes** for performance regressions and anti-patterns. Use alongside the five-axis review in `SKILL.md` (Axis 5: Performance). Items are things you can catch by reading the diff; confirm suspicious ones with a profiler before blocking.

Severity legend: **[High]** = real regression risk, fix before merge; **[Med]** = fix soon / discuss; **[Low]** = nit.

---

## 1. Algorithmic Complexity

- [ ] **[High] No accidental quadratic behavior.** Nested loops over the same data (`for a in A: for b in B`) — is the inner lookup O(1)? A linear `find`/`includes` inside a loop over N items is O(N²). Use a `Map`/`Set`/index for the inner lookup.
- [ ] **[High] Sorting/filtering done in the database, not in app memory** for large collections. Pulling 50k rows to `Array.sort()` in the handler is a memory and CPU spike.
- [ ] **[Med] Recursion with deep or attacker-influenced depth** — unbounded recursion can stack-overflow; check for a cycle guard and a depth cap.
- [ ] **[Med] Regex complexity (ReDoS) reviewed** — catastrophic-backtracking patterns executed on untrusted/long input (see security checklist too).
- [ ] **[Low] Repeated work hoisted out of loops** — constant computations, regex compilation, and date formatting moved outside the hot loop.

## 2. Database Access (N+1 & Queries)

- [ ] **[High] No N+1 query patterns.** A loop that issues one query per row (`tasks.forEach(t => loadOwner(t.ownerId))`) must be collapsed into a single joined/`include`/`select ... where id in (...)` query.
- [ ] **[High] List endpoints are paginated** — `take`/`limit` + `skip`/`offset`, with a cap on page size so a client can't request 1,000,000 rows.
- [ ] **[High] Only needed columns are selected** (`select`/`projections`), not `SELECT *`, especially for wide tables and large result sets.
- [ ] **[Med] Queries use indexes** — filters, joins, and sorts are on indexed columns. A full table scan on a hot path is a latency bomb. (Verify an `EXPLAIN` shows index usage.)
- [ ] **[Med] No query inside a serializer/renderer** — lazy-loading relationships while building the response defeats eager loading and reintroduces N+1.
- [ ] **[Med] Transactions are as short as possible** — no network calls, sleeps, or user interaction inside a DB transaction (holds locks, kills throughput).
- [ ] **[Low] `COUNT(*)` for "total pages" considered** — a full count on every list page can be expensive; confirm it's needed or use an approximate/keyset count.

## 3. Caching

- [ ] **[High] Expensive, stable computations are cached** — config, feature flags, reference data, rendered fragments fetched far more often than they change. TTL + invalidation strategy present.
- [ ] **[Med] Cache keys are specific and correct** — include the relevant inputs (locale, version, params). A too-broad key serves stale/wrong data; too-narrow defeats the cache.
- [ ] **[Med] Cache invalidation is handled** — TTL-only or explicit purge on write; confirm stale reads are acceptable for the use case.
- [ ] **[Med] No unbounded in-memory cache growth** — an ever-growing `Map`/object leaks memory. Use a size/ TTL-bounded cache (LRU) or external store (Redis).
- [ ] **[Low] HTTP caching headers set for static assets / immutable content** (`Cache-Control: public, max-age=..., immutable` with content-hashed filenames).

## 4. Database Indexing

- [ ] **[High] New queried columns have indexes** — any new `WHERE`, `JOIN ON`, or `ORDER BY` column on a large table gets an index; verify it's a composite index ordered for the access pattern (equality columns first, then range/sort).
- [ ] **[Med] Indexes aren't redundant or contradictory** — don't add a duplicate of an existing index; drop unused ones (they slow writes).
- [ ] **[Med] Partial/expression indexes considered** for large tables filtered by a constant (e.g. `WHERE status = 'active'`).
- [ ] **[Low] Foreign-key columns indexed** — FK columns are frequent join/filter targets and are not auto-indexed in every engine.

## 5. Payload & Response Sizes

- [ ] **[High] Responses aren't bloated** — no dumping entire entity graphs; use DTOs / field selection so the API returns what the UI needs and nothing more.
- [ ] **[High] Request body size is capped** (max JSON/body size in the server) to prevent memory exhaustion and large-payload DoS.
- [ ] **[Med] Large lists use keyset/cursor pagination**, not deep `OFFSET` (offset pagination degrades as the page number grows).
- [ ] **[Med] Binary/large data streamed, not buffered** — files and exports streamed to the client / object store rather than loaded fully into memory.
- [ ] **[Low] Compression enabled** (gzip/brotli) for text responses and assets.

## 6. Concurrency & Async

- [ ] **[High] Blocking/synchronous work off the event loop / request thread** — no `fs.readFileSync`, `JSON.parse` of huge inputs, or CPU-heavy work on the request path without offloading (worker, async, or background job).
- [ ] **[High] Parallel independent I/O, serialize dependent I/O** — independent fetches run concurrently (`Promise.all`), not sequentially, but `Promise.all` over an unbounded set causes thundering-herd; batch with a concurrency cap.
- [ ] **[Med] Connection pool sized correctly** — not exhausted (too small → queuing) and not leaking (acquire without release, missing `finally`/`await using`).
- [ ] **[Med] No race conditions on shared mutable state** — feature flags, caches, counters updated from concurrent requests need atomic ops or locks.
- [ ] **[Med] Timeouts on every external call** — DB, HTTP, queue; a hung dependency must not hang the request forever. Honor downstream deadlines (hedging/cancellation propagated).
- [ ] **[Low] Retries are bounded and use backoff + jitter** — naive retries amplify load during an incident (retry storms). Idempotency keys for non-GET retries.

## 7. Frontend / Rendering

- [ ] **[High] No unnecessary re-renders** — `React.memo`, stable `useCallback`/`useMemo`, stable object/array props; new object literals in render passed to memoized children cause wasted renders.
- [ ] **[High] Images sized, lazy, and responsive** — explicit `width`/`height` (no CLS), `loading="lazy"` for below-fold, `srcset`/AVIF/WebP for the LCP image, `fetchpriority="high"` on the hero.
- [ ] **[Med] Bundle size reviewed** — heavy, rarely-used code is dynamically imported (`lazy()` / route splitting); no giant dependency pulled into the initial bundle.
- [ ] **[Med] No layout thrash / forced reflow** — interleaved read-then-write of DOM styles in loops; batch reads and writes.
- [ ] **[Low] Long tasks (>50ms) on the main thread avoided** — heavy work chunked or moved off-thread (web worker) to keep INP healthy.

## 8. Review Habits

- [ ] **[High] Suspect claims are backed by a measurement** — don't block on "this might be slow" without a profile or numbers. Quantify the cost when you can.
- [ ] **[Med] Performance budget considered** — does the change push bundle size, payload, or p95 latency past the agreed budget? If a budget exists in CI, it should pass.
- [ ] **[Low] Hot path kept allocation-light** — no large arrays/objects/closures created per request where a pooled/reused structure fits.

---

### How to use this list
- Read the diff with the five axes in mind; this list is Axis 5.
- Profile before declaring a "bottleneck" — see `performance-optimization` for the measure→identify→fix→verify→guard workflow.
- Don't over-optimize cold paths; fix what evidence shows matters.
- Do not modify `SKILL.md`. This file supports Axis 5 (Performance) and the `performance-optimization` skill.
