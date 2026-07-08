# Observability & Instrumentation — Checklist

A checklist for **instrumenting features so production behavior is visible and diagnosable**. From `SKILL.md`: instrument alongside the feature, the way you write tests. Telemetry without a question is noise — define "working" first. Use this as the at-a-glance gate (the fuller process is in `SKILL.md`).

Severity legend: **[Critical]** = required for any production feature; **[High]** = strongly expected; **[Med]** = recommended; **[Low]** = maturity/nice-to-have.

---

## 1. Define Questions Before Signals

- [ ] **[Critical] Write 2–4 on-call questions per feature** before adding telemetry ("what fraction succeed? when it fails, why? is the dependency slower than usual?"). Every signal must map to a question.
- [ ] **[Critical] Pick the right signal per question** — structured log = "what happened in this case"; metric = "how often/how fast in aggregate"; trace = "where did time go across services."
- [ ] **[High] Rule of thumb applied** — metrics tell you *that* something is wrong, traces tell you *where*, logs tell you *why*. No signal without a corresponding question.

## 2. Structured Logging

- [ ] **[Critical] All logs are structured JSON** with a stable `event` name and machine-readable fields — not string-interpolated prose (`logger.info(\`Payment ${id} failed\`)` is unqueryable).
- [ ] **[Critical] A correlation/request ID is on every line** — generated/accepted at the boundary and attached to every log, span, and outbound call; without it you can't reconstruct one request from interleaved logs.
- [ ] **[High] Log levels used consistently** — `error` (invariant broken, act), `warn` (degraded but handled), `info` (business event), `debug` (off in prod by default).
- [ ] **[High] No secrets/tokens/full PII in any log line** — allowlist fields; never log whole request bodies or auth headers. Telemetry pipelines are a classic leak path.
- [ ] **[High] Child logger per request** propagates the correlation ID downstream (e.g. Express middleware sets `req.log = logger.child({ requestId })`).
- [ ] **[Med] Log the *why*, not just the *what*** — include error codes, provider names, attempt counts, decision reasons so a reader can diagnose without source.
- [ ] **[Med] Avoid high-cardinality fields in logs-as-metrics** — keep user IDs/URLs in log fields, not metric labels.
- [ ] **[Low] Use a sampling/level toggle** so verbose debug can be turned on for a request without flooding global logs.

## 3. Metrics (RED / USE)

- [ ] **[Critical] RED on every endpoint and external dependency** — **R**ate (requests/sec), **E**rrors (failure rate), **D**uration (latency histogram, not average).
- [ ] **[Critical] USE on resources** — **U**tilization, **S**aturation, **E**rrors for queues, pools, hosts, disks.
- [ ] **[Critical] Latency is a histogram; percentiles (p50/p95/p99) are queryable** — an average hides the 1% having a terrible time. Never track only averages.
- [ ] **[High] Bounded label sets** — route template, status class (`2xx`/`5xx`), provider name. NEVER user IDs, raw URLs, email, request IDs, or error-message text as labels (cardinality bomb that tanks the backend).
- [ ] **[High] Status class, not exact code, as a label** (`status_class="5xx"`) to keep series count finite.
- [ ] **[Med] Business/SLI metrics emitted** — not just technical ones (orders placed, payments succeeded, jobs completed) so product-level health is visible.
- [ ] **[Med] Counter/up/down semantics correct** — use monotonic counters for rates; gauges for levels; never reset a counter to fake a delta.
- [ ] **[Low] Record queue depth, pool utilization, and saturation** as first-class metrics (they predict incidents before errors spike).

## 4. Distributed Tracing

- [ ] **[Critical] Tracing enabled (OpenTelemetry auto-instrumentation)** for HTTP/gRPC/DB clients — near-zero code, covers the cross-service hops logs can't.
- [ ] **[High] Context propagated across every async boundary** — HTTP headers, queue message metadata, scheduled jobs; a gap kills the trace at that hop.
- [ ] **[High] Manual spans around meaningful units of work** (`applyDiscounts`, `chargeProvider`) with attributes on-call will filter by — not per-line spans.
- [ ] **[High] Sample head-based at low rate by default; keep 100% of errors** if the backend supports tail sampling — control cost while preserving failure visibility.
- [ ] **[Med] One request followable end-to-end in the tracing UI** with no broken spans (verify in staging).
- [ ] **[Low] Span attributes bounded** — same cardinality discipline as metrics (no user IDs in span attributes).

## 5. Alerting

- [ ] **[Critical] Alert on symptoms users feel, not causes** — error rate > 1% for 5 min, p99 > 2s, queue age > 10 min are page-worthy; CPU 85% / one pod restart are dashboard-only.
- [ ] **[Critical] Every alert is actionable** — if the response is "ignore it, it self-heals," delete the alert.
- [ ] **[Critical] Every alert links to a runbook** — even three lines: what it means, first query, escalation path.
- [ ] **[High] Threshold + duration justified by SLO or history**, not a guess.
- [ ] **[High] Two severities only: page (user-facing, act now) and ticket (degradation, this week)** — a third tier becomes noise people ignore.
- [ ] **[Med] Each new alert test-fired once** (lower threshold temporarily) to confirm it reaches the right channel and the runbook link works.
- [ ] **[Med] De-dupe / group alerts** so one incident doesn't page 20 times.

## 6. SLO Instrumentation

- [ ] **[High] SLIs defined and emitted** — availability, latency, error budget burn rate trackable per service/feature.
- [ ] **[High] Error-budget burn alerts** — fast-burn (e.g. 14.4× for 1h) pages; slow-burn (e.g. 6× for 6h) tickets; both symptom-based.
- [ ] **[Med] SLO dashboard shows budget remaining** so teams can make ship/no-ship calls with data.
- [ ] **[Med] Multi-window burn-rate alerts** avoid flapping while catching real regressions.
- [ ] **[Low] Per-feature SLOs (not just global)** so a new feature's health is isolatable.

## 7. Verification of Telemetry Itself

- [ ] **[Critical] Induce a failure in staging → find it via `requestId` in logs** with fields structured (not `[object Object]`).
- [ ] **[Critical] Send test traffic → confirm metric series appear** with expected labels and sane values.
- [ ] **[High] Follow one request across services in the tracing UI** — no broken spans, context propagates.
- [ ] **[High] Spot-check actual log output for secret/PII leakage** — don't trust the code, check the emitted line.
- [ ] **[Med] Confirm an incident was diagnosable from telemetry alone**, without reading source — that's the bar.

## 8. Pre-Launch Instrumentation Gate

- [ ] **[Critical] No feature PR with retries/queues/external calls ships with zero new telemetry.**
- [ ] **[Critical] On-call questions written; each signal maps to one.**
- [ ] **[High] Structured logs + correlation ID on every line.**
- [ ] **[High] RED metrics on new endpoints/deps; histogram latency with p95/p99.**
- [ ] **[High] At least one symptom-based alert with a runbook link.**
- [ ] **[Med] Tracing covers the new cross-service path.**

---

### How to use this list
- Start from on-call questions (section 1), not from "add logging."
- If a feature PR has I/O, queues, or cross-service calls and no telemetry, that's a red flag — block or file a tracked follow-up.
- The full process, code samples, and rationalizations live in `SKILL.md`. Do not modify `SKILL.md`. This file is the at-a-glance supporting reference.
