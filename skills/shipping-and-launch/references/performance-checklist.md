# Launch Performance Checklist

Run this checklist as part of the pre-launch gate. It is the performance subsection of the launch
Definition of Done, expanded with concrete, measurable items. Performance regressions are the
silent killers of launches — they rarely error, they just make users leave. Verify with real load,
not intuition.

## Core Web Vitals (field + lab)

- [ ] **LCP < 2.5s** (Largest Contentful Paint) on mobile, p75 — Good threshold.
- [ ] **INP < 200ms** (Interaction to Next Paint) — replaces FID; measure real interactions.
- [ ] **CLS < 0.1** (Cumulative Layout Shift) — reserve space for images/ads/embeds to avoid jumps.
- [ ] **FCP < 1.8s** (First Contentful Paint) where tracked.
- [ ] **TTFB < 800ms** (Time To First Byte) at the edge for the landing path.
- [ ] **Lab matches field** — Lighthouse/WebPageTest numbers corroborated by RUM (Real User Monitoring) p75.

## Backend / API

- [ ] **No N+1 queries** — critical paths fetch related data in bulk (joins / `selectinload` / dataloader), not per-row.
- [ ] **Database indexes on hot paths** — query plans (`EXPLAIN`) show index scans, not sequential scans, for filtered/sorted columns.
- [ ] **P95 latency budget met** — API p95 under the agreed SLO (e.g. < 500ms for read, < 1s for writes).
- [ ] **P99 bounded** — tail latency capped by timeouts; no unbounded waits to slow clients.
- [ ] **Timeouts & deadlines propagated** — every downstream call has a deadline; the request fails fast instead of hanging.
- [ ] **Connection pooling tuned** — pool size matches concurrency; no per-request connect storms.
- [ ] **Caching for repeated reads** — hot, stable data cached (Redis/CDN/HTTP cache) with correct invalidation.
- [ ] **Pagination on list endpoints** — no unbounded result sets returned to clients.
- [ ] **No synchronous heavy work in request path** — email, image processing, analytics offloaded to a queue/worker.

## Frontend / Asset Delivery

- [ ] **Bundle size within budget** — total JS under the agreed limit (e.g. < 200KB gzipped for the initial route); tracked in CI.
- [ ] **Code splitting** — routes/lazy features split so initial load is minimal.
- [ ] **Tree shaking / dead code eliminated** — production build excludes unused exports.
- [ ] **Images optimized** — modern formats (WebP/AVIF), responsive `srcset`, lazy-loaded off-screen images.
- [ ] **Fonts optimized** — `font-display: swap`, subsetted, no render-blocking requests where avoidable.
- [ ] **Static assets cached** — immutable hashing + long `Cache-Control` for JS/CSS/images via CDN.
- [ ] **CDN in front of static + edge** — assets served close to users; compression (Brotli/gzip) enabled.
- [ ] **No layout-shift on load** — dimensions set on media; skeletons/placeholders prevent CLS.

## Infrastructure & Scaling

- [ ] **Load test passed** — the system sustained expected peak traffic (and a 2–3× headroom) without error or degradation.
- [ ] **Autoscaling configured** — horizontal scaling on CPU/request metrics with sane min/max and warm-up.
- [ ] **Resource limits set** — CPU/memory requests & limits prevent noisy-neighbor and OOM cascades.
- [ ] **Database capacity checked** — connection ceiling, disk, and IOPS sufficient for peak + growth.
- [ ] **Graceful degradation** — non-critical features fail soft (e.g. recommendations hide) rather than taking down the page.
- [ ] **Backpressure handled** — queues and rate limits protect dependencies from overload.

## Observability for Performance

- [ ] **Latency dashboards live** — p50/p95/p99 by endpoint visible pre-launch.
- [ ] **Core Web Vitals in RUM** — field metrics flowing from real users.
- [ ] **Trace sampling on** — distributed traces capture the slow path when p95 degrades.
- [ ] **Alerts on regression** — a latency/error alert fires before users complain (see SLO burn-rate alerts).
- [ ] **Baseline captured** — pre-launch p95/latency numbers recorded so rollout can compare canary vs baseline.

## Using the Checklist

Performance is comparative: the question is not "is it fast?" but "is it within budget and not worse
than before?" Capture a baseline before launch, then compare each rollout stage against it. A feature
that passes functional DoD but fails this checklist will still lose users — just quietly.
