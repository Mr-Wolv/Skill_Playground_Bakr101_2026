# Performance Optimization — Checklist

A practitioner's checklist for **measuring and fixing** performance problems. Core rule from `SKILL.md`: **profile first, optimize only what evidence proves matters.** Use the measure → identify → fix → verify → guard workflow. Items here are the levers, ordered by where to pull them.

Severity legend: **[Critical]** = do before shipping a perf-sensitive change; **[High]** = usually worth it; **[Med]** = situational; **[Low]** = micro-optimization (only after measurement).

---

## 1. Profile First (the non-negotiable)

- [ ] **[Critical] Establish a real baseline before changing anything** — synthetic (Lighthouse, DevTools Performance, `k6`) *and* RUM (web-vitals/CrUX) for frontend; APM/query logs/timing for backend. No numbers → no optimization.
- [ ] **[Critical] Identify the actual bottleneck, not the assumed one.** Symptom → measurement: slow LCP (images/network), high INP (main-thread JS), slow API (N+1/missing index), memory growth (leak/unbounded cache).
- [ ] **[High] Use the right tool per layer** — `EXPLAIN`/query plan for DB, heap snapshot for memory, CPU profiler for compute, Performance trace for long tasks.
- [ ] **[High] Measure on representative hardware/network** — not your dev machine. Profile on mid-tier mobile + throttled 4G for frontend.
- [ ] **[Med] Capture a trace/recording you can attach to the PR** so the improvement is reproducible and reviewable.

## 2. Hot Paths

- [ ] **[Critical] Optimize the hot path only** — the per-request, per-render, or per-item code that runs constantly. Cold admin scripts don't need micro-optimization.
- [ ] **[High] Move constant work out of the loop** — regex compile, date format, config parse, repeated `new` objects hoisted above the loop.
- [ ] **[High] Replace O(N²) with O(N)** — inner `find`/`includes`/linear scan becomes a `Map`/`Set`/`index` lookup; sort/filter in the DB.
- [ ] **[High] Avoid allocating large objects/arrays per request** in hot paths — reuse buffers/pools where the language/runtime supports it.
- [ ] **[Med] Avoid ReDoS-prone regex on untrusted/long input** — catastrophic backtracking is a hidden hot path.
- [ ] **[Low] Inline trivial getters / avoid needless abstraction layers** only when the profiler shows call overhead matters.

## 3. Database

- [ ] **[Critical] Eliminate N+1 queries** — collapse per-row loops into a single join / `include` / `WHERE id IN (...)`.
- [ ] **[Critical] Paginate list endpoints** — `take`/`limit` + `skip`/`offset` with a hard cap; keyset/cursor pagination for deep, large lists (offset degrades as page grows).
- [ ] **[Critical] Index the columns you filter/join/sort on** — verify with `EXPLAIN` that the planner uses the index; composite indexes ordered for the access pattern (equality first, then range/sort).
- [ ] **[High] Select only needed columns** — no `SELECT *` on wide tables; use DTOs/projections.
- [ ] **[High] Keep transactions short** — no network calls, sleeps, or user waits inside a DB transaction (holds locks, kills throughput).
- [ ] **[High] Batch writes** — bulk insert/update instead of row-by-row in a loop.
- [ ] **[Med] Add connection-pool limits + timeouts** — sized to DB capacity; acquire inside `try/finally` (or `await using`) so connections are always released.
- [ ] **[Med] Consider read replicas / read-through caching** for read-heavy workloads; archive/partition old data on huge tables.
- [ ] **[Low] Use covering indexes** where a query can be served from the index alone.

## 4. Caching Strategy

- [ ] **[Critical] Cache expensive, frequently-read, rarely-changed data** — config, feature flags, reference/lookup data, rendered fragments. TTL + explicit invalidation.
- [ ] **[High] Choose the right tier** — in-process (per-instance) for tiny hot data; shared (Redis) for data that must be consistent across instances.
- [ ] **[High] Correct, specific cache keys** — include inputs that change the output (locale, version, params). Wrong keys → stale or wrong data.
- [ ] **[High] Bounded cache size** — LRU/size/TTL cap; an ever-growing in-memory cache is a memory leak.
- [ ] **[Med] Decide invalidation up front** — TTL-only vs write-through vs write-invalidate; confirm staleness is acceptable.
- [ ] **[Med] HTTP caching for static/immutable assets** — `Cache-Control: public, max-age=..., immutable` with content-hashed filenames.
- [ ] **[Low] Use CDN edge caching** for public, cacheable responses and assets.

## 5. Async & Concurrency

- [ ] **[Critical] Offload blocking work from the request thread / event loop** — `fs.readFileSync`, huge `JSON.parse`, CPU-heavy compute → worker thread, async API, or background job.
- [ ] **[Critical] Run independent I/O concurrently** (`Promise.all`) but cap concurrency to avoid thundering-herd on a dependency.
- [ ] **[High] Set timeouts on every external call** — DB, HTTP, queue; propagate cancellation so a hung dependency can't hang the request forever.
- [ ] **[High] Bounded, jittered retries with backoff** — naive retries cause retry storms during incidents; idempotency keys for non-GET retries.
- [ ] **[Med] Stream large payloads** — files/exports streamed to client or object store rather than fully buffered in memory.
- [ ] **[Med] Avoid lock contention** — guard shared mutable state (counters, caches, flags) with atomic ops or locks; watch for GC pauses and pool exhaustion under load.
- [ ] **[Low] Consider hedged requests** for high-latency tail reduction on critical paths (only when idempotent).

## 6. Resource Limits

- [ ] **[Critical] Cap request/response body size** — prevents memory exhaustion and large-payload DoS.
- [ ] **[Critical] Cap input/collection sizes at boundaries** — pagination limits, max array length, max upload size; reject oversized up front.
- [ ] **[High] Set CPU/memory limits on containers/pods** — and load-test to confirm the service stays healthy under the limit (no OOM-kill loops).
- [ ] **[High] Rate limiting** — per-client and global; protects the system and downstream dependencies.
- [ ] **[Med] Bounded queues / backpressure** — background workers reject or delay when saturated instead of OOM-ing; expose queue depth as a metric.
- [ ] **[Med] Circuit breakers around flaky dependencies** — fail fast and shed load instead of piling up waiting requests.

## 7. Frontend / Core Web Vitals

- [ ] **[Critical] LCP ≤ 2.5s** — hero image optimized (AVIF/WebP, `srcset`, `fetchpriority="high"`, explicit dimensions), no render-blocking CSS/JS, fast TTFB.
- [ ] **[Critical] INP ≤ 200ms** — break up long tasks (>50ms), avoid forced reflow/layout thrash, defer non-urgent work (`requestIdleCallback`/scheduler).
- [ ] **[Critical] CLS ≤ 0.1** — reserve space for images/ads/embeds (dimensions or `aspect-ratio`), avoid late-inserted content shifting layout, use `font-display: optional/swap` with size-adjusted fallback.
- [ ] **[High] Code-split & lazy-load** — route-level splitting, `lazy()` for heavy/rare components; keep initial JS < 200KB gzipped.
- [ ] **[High] No unnecessary re-renders** — `React.memo`, stable `useMemo`/`useCallback`, stable object/array props; don't memoize everything (that's its own cost).
- [ ] **[High] Compress assets** — brotli/gzip for text; modern image formats; preconnect/`dns-prefetch` for critical third-party origins.
- [ ] **[Med] Avoid layout thrash** — batch DOM reads then writes; cache layout reads.
- [ ] **[Low] Use `will-change`/`transform` sparingly** for animations; prefer compositor-only properties.

## 8. Verify & Guard

- [ ] **[Critical] Measure again after the fix** — before/after numbers in the PR; confirm the specific bottleneck improved.
- [ ] **[Critical] Behavior unchanged** — optimization didn't break correctness; existing tests pass.
- [ ] **[High] Enforce a performance budget in CI** — `bundlesize`, Lighthouse CI (`lhci`), p95 latency assertion; fail the build on regression.
- [ ] **[Med] Add a monitoring/guard** so the regression is caught next time (metric alert, perf test in CI).
- [ ] **[Low] Document the finding** — what the bottleneck was and why this fix works, for the next reviewer.

---

### How to use this list
- Never start at section 2 — section 1 (profile) is mandatory. Guessing without measurement is premature optimization.
- Match the symptom to the section: slow first load → 7 + network; slow API → 3; memory growth → 2/4; jank → 7.
- After fixing, you must verify (section 8) or you haven't optimized — you've just changed code.
- Do not modify `SKILL.md`. This file is the supporting reference for `performance-optimization`.
