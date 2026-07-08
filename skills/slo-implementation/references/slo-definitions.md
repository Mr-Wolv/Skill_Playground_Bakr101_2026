# SLO Definitions — How to Define SLIs, Objectives, and Windows

This reference expands the SLO Implementation skill with the step-by-step method for defining
Service Level Indicators (SLIs), Service Level Objectives (SLOs), and the windows over which they
are measured. The goal: user-perceived reliability expressed as a number you can alert on and a
budget you can spend.

---

## 1. The SLI/SLO/SLA Hierarchy

1. **SLA** — a contractual promise to a customer (often with penalties). Usually looser than the SLO.
2. **SLO** — the internal reliability target you set *above* the SLA so you have margin.
3. **SLI** — the actual measurement of user-perceived behavior. SLOs are written *against* SLIs.

Rule: SLO target should be tighter than the SLA so you get alerted and can act before you breach contract.

## 2. What Makes a Good SLI

2. **Measure user-perceived experience**, not system-internal health ("requests served" ≠ "users served").
3. **Define "good" explicitly** — a request is "good" only if it succeeded *and* met its latency/validity criterion.
4. **Be measurable with existing telemetry** — if you can't instrument it cheaply, pick a proxy you can.
5. **Be ratio-shaped** — almost all SLIs reduce to `good events / valid events`.
6. **Exclude known-bad traffic** — bot traffic, health-check pings, and client-aborted requests usually distort the ratio.
7. **Aggregate at the edge or request boundary**, where the user actually experiences the result.

## 3. SLI Types and How to Select Them

8. **Availability SLI** — `successful requests / total requests`, where success = 2xx/3xx and not a 5xx. The default starting SLI.
9. **Latency SLI** — `requests faster than threshold / total requests` (e.g. < 500ms). Pairs with availability.
10. **Durability / correctness SLI** — `successful writes / total writes`, or `correct results / total computed`. For storage and data pipelines.
11. **Freshness SLI** — `records processed within age budget / total records`. For analytics/ETL.
12. **Coverage SLI** — `events handled by the system / events that should be handled`. For queues and batch jobs.
13. **Throughput SLI** — `requests served at or above target rate / total time`. For capacity-constrained systems.
14. **Saturation-aware SLI** — when the system is near saturation, treat as degraded even if individual requests succeed.

Selection rule: pick **at most 2–4 SLIs** per user journey. More than that and nobody watches any of them.

## 4. Choosing the Latency Threshold

15. **User-perceived threshold over SLA threshold** — base the latency SLI on what users notice (≈ 100–500ms for API reads, < 1s for writes), not on what is easy to hit.
16. **Per-route thresholds** — a health endpoint and a report-export endpoint should not share one latency SLI. Group endpoints by class.
17. **Stick to one percentile per SLI** — define the latency SLI as "% of requests under X ms," not "p95 under X." Keep the ratio shape.

## 5. Setting SLO Targets

18. **Start from current performance** — measure the SLI for the last 28 days; set the first SLO at a level you already meet ~95–99% of the time, then tighten.
19. **Account for user tolerance** — a payment endpoint wants 99.95–99.99%; an internal admin tool may be fine at 99%.
20. **Leave SLA headroom** — set SLO = SLA − buffer (e.g. SLA 99.9%, SLO 99.95%).
21. **Differentiate by criticality** — critical user journeys get stricter SLOs than nice-to-have features.
22. **Be honest about cost** — each extra "9" costs disproportionately more (99.9%→99.99% is ~7× less downtime budget). Don't over-promise.

## 6. Downtime Reference (for picking availability targets)

| SLO %  | Downtime / month | Downtime / year |
| ------ | ---------------- | --------------- |
| 99%    | 7.2 hours        | 3.65 days       |
| 99.9%  | 43.2 minutes     | 8.76 hours      |
| 99.95% | 21.6 minutes     | 4.38 hours      |
| 99.99% | 4.32 minutes     | 52.56 minutes   |

## 7. Choosing the Measurement Window

23. **Rolling window over calendar window** — a 28-day rolling window recovers automatically after an incident; a calendar month freezes the miss for the rest of the month.
24. **Match window to SLO stability** — 28–30 days is the SRE default; shorter (7d) reacts faster but is noisier.
25. **One window per SLO** — don't report the same SLI over three windows; pick the one your error budget math uses.

## 8. Writing the SLO Spec

26. **YAML/structured form** — name, target, window, and the exact SLI query, so tooling can compute compliance:

```yaml
slos:
  - name: api_availability
    target: 99.9
    window: 28d
    sli: |
      sum(rate(http_requests_total{status!~"5.."}[28d]))
      / sum(rate(http_requests_total[28d]))
  - name: api_latency_p95
    target: 99
    window: 28d
    sli: |
      sum(rate(http_request_duration_seconds_bucket{le="0.5"}[28d]))
      / sum(rate(http_request_duration_seconds_count[28d]))
```

27. **Record the SLI as a Prometheus recording rule** so dashboards and alerts read a stable series:

```yaml
groups:
  - name: sli_rules
    interval: 30s
    rules:
      - record: sli:http_availability:ratio
        expr: |
          sum(rate(http_requests_total{status!~"5.."}[28d]))
          / sum(rate(http_requests_total[28d]))
      - record: sli:http_latency:ratio
        expr: |
          sum(rate(http_request_duration_seconds_bucket{le="0.5"}[28d]))
          / sum(rate(http_request_duration_seconds_count[28d]))
```

28. **Record compliance and error-budget-remaining** so the dashboard is one query away:

```yaml
  - name: slo_rules
    interval: 5m
    rules:
      - record: slo:http_availability:compliance
        expr: sli:http_availability:ratio >= bool 0.999
      - record: slo:http_availability:error_budget_remaining
        expr: (sli:http_availability:ratio - 0.999) / (1 - 0.999) * 100
```

## 9. Multi-Service / User-Journey SLOs

29. **Define SLOs per user journey, not per microservice** — a checkout journey SLI = "checkout requests that succeeded end-to-end," aggregating the services it touches.
30. **Composite SLIs** — when a journey spans services, the SLI is good only if *every* hop succeeded (logical AND), not just the edge.

## 10. Anti-Patterns to Avoid

31. **SLI ≠ uptime of the server** — a 200 from a health endpoint while the DB is down is not availability.
32. **Don't set SLOs you can't measure** — an un-instrumented SLO is a wish.
33. **Don't make the SLO the SLA** — you lose the early-warning margin.
34. **Don't over-fit the target to a good week** — baselining during a quiet period produces an SLO you'll violate under real load.
35. **Don't track 20 SLIs** — attention is the scarce resource; 2–4 per journey.
36. **Don't define SLOs without an owner** — every SLO needs a team accountable for its error budget.

## 11. Review Cadence

37. **Quarterly SLO review** — confirm targets still match user tolerance and current performance; tighten gradually.
38. **Post-incident adjustment** — if a breach reveals the SLO was wrong (too strict or too loose), change it deliberately and document why.

## Quick Start

1. Pick the critical user journey.
2. Choose 2–4 SLIs (availability + latency + one domain-specific).
3. Write each as `good / valid` ratio with an explicit "good" definition.
4. Baseline current performance over 28 days.
5. Set target a notch tighter than the SLA, at a level you meet ~95–99% of the time.
6. Encode SLI + compliance + error-budget as recording rules.
7. Wire burn-rate alerts (see `error-budget.md`) and a dashboard.
8. Assign an owner and review quarterly.
