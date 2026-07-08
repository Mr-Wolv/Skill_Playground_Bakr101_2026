# Error Budget Policy

An **error budget** is the allowable failure for a given SLO. If SLO = 99.9% availability, you are
*allowed* 0.1% downtime — that is your budget to "spend" on risk: launches, experiments, and
aggressive changes. The budget turns reliability from a feeling into an accounting system that
balances innovation against stability. This reference defines how to calculate, monitor, and
enforce the budget.

---

## 1. Error Budget Calculation

**Formula:**

```
Error Budget = 1 - SLO Target
```

**Worked example (availability):**

- SLO target: 99.9%
- Error budget: 1 − 0.999 = **0.1%** = 43.2 minutes/month
- Current error: 0.05% = 21.6 minutes/month
- Remaining budget: (0.1 − 0.05) / 0.1 = **50%**

**Worked example (latency SLI):**

- SLO: 99% of requests under 500ms
- Error budget: 1% of requests may exceed 500ms
- If 0.4% exceeded this month → 60% budget remaining

**Remaining budget as a percentage (for dashboards):**

```
remaining% = (SLI_ratio − SLO_target) / (1 − SLO_target) × 100
```

In PromQL (availability, target 0.999):

```promql
(sli:http_availability:ratio - 0.999) / (1 - 0.999) * 100
```

## 2. Why Error Budgets Exist

The budget is the reconciliation between two competing forces:

- **Reliability team** wants 100% — no risky changes.
- **Product/feature team** wants to ship fast — many risky changes.

The error budget is the agreed amount of unreliability the service is permitted. While budget
remains, ship freely. When it is gone, reliability wins until it is restored.

## 3. Burn Rate

**Burn rate** = how fast you are consuming the budget relative to the nominal rate.

- Nominal rate = 1 budget per window (e.g. 1 per 28 days).
- Burn rate of **1×** = exactly on track to exhaust the budget at the end of the window.
- Burn rate of **14.4×** = exhausts the *entire* 28-day budget in **2 days** (28 / 14.4 ≈ 2).
- Burn rate of **6×** = exhausts the budget in ~4.7 days.

**Fast-burn alert (14.4× over 1h):** consumes ~2% of the budget in 1 hour. Catches acute outages.

```promql
# 5-minute burn rate for a 99.9% availability SLO
(1 - (sum(rate(http_requests_total{status!~"5.."}[5m]))
      / sum(rate(http_requests_total[5m]))))
/ (1 - 0.999)
```

**Slow-burn alert (6× over 6h):** consumes ~5% of the budget in 6 hours. Catches chronic, low-grade degradation.

```promql
(1 - (sum(rate(http_requests_total{status!~"5.."}[6h]))
      / sum(rate(http_requests_total[6h]))))
/ (1 - 0.999)
```

## 4. Burn-Rate Alert Rules

```yaml
groups:
  - name: slo_alerts
    interval: 1m
    rules:
      # Fast burn: 14.4x, 1h window — consumes 2% budget/hour
      - alert: SLOErrorBudgetBurnFast
        expr: |
          slo:http_availability:burn_rate_1h > 14.4
          and slo:http_availability:burn_rate_5m > 14.4
        for: 2m
        labels: { severity: critical }
        annotations:
          summary: "Fast error budget burn detected"
          description: "Error budget burning at {{ $value }}x rate"

      # Slow burn: 6x, 6h window — consumes 5% budget/6h
      - alert: SLOErrorBudgetBurnSlow
        expr: |
          slo:http_availability:burn_rate_6h > 6
          and slo:http_availability:burn_rate_30m > 6
        for: 15m
        labels: { severity: warning }
        annotations:
          summary: "Slow error budget burn detected"
          description: "Error budget burning at {{ $value }}x rate"

      # Exhaustion
      - alert: SLOErrorBudgetExhausted
        expr: slo:http_availability:error_budget_remaining < 0
        for: 5m
        labels: { severity: critical }
        annotations:
          summary: "SLO error budget exhausted"
          description: "Error budget remaining: {{ $value }}%"
```

Multi-window, multi-burn-rate alerts (the Google SRE approach) reduce both false positives (require
both short and long windows to agree) and detection latency (alert within minutes of a fast burn).

## 5. Days-to-Exhaustion

```promql
# Days until the budget is gone at the current burn rate
(slo:http_availability:error_budget_remaining / 100)
* 28
/ ((1 - sli:http_availability:ratio) * (1 - 0.999))
```

## 6. Error Budget Policy (Tiered Response)

The policy maps remaining budget to permitted action. Tiers are enforced by the owning team, not optional.

```yaml
error_budget_policy:
  - remaining_budget: 100%        # healthy
    action: Normal development velocity. Ship freely.
  - remaining_budget: 50%         # caution
    action: Consider postponing risky changes. Review upcoming launches.
  - remaining_budget: 20%         # warning
    action: Freeze non-critical changes. Only reliability + urgent fixes.
  - remaining_budget: 10%         # critical
    action: Feature freeze. All effort on reliability. No launches.
  - remaining_budget: 0%          # exhausted
    action: Hard freeze. Roll back recent risky changes. Postmortem required.
```

A common concrete policy:

| Remaining | Status      | What happens                                                        |
| --------- | ----------- | ------------------------------------------------------------------- |
| > 50%     | Healthy     | Ship normally.                                                      |
| 20–50%    | Caution     | Review launches; defer the riskiest.                                |
| 10–20%    | Warning     | Freeze non-critical; reliability work only.                         |
| < 10%     | Critical    | Feature freeze; focus entirely on reliability.                      |
| 0%        | Exhausted   | Revert recent changes; required postmortem before any ship.         |

## 7. Policy on Exhaustion

When the budget hits 0%:

1. **Stop the bleeding** — page the owning team; the fast-burn alert should already have fired.
2. **Freeze launches** — no new feature deployments until budget recovers above the threshold.
3. **Prioritize reliability** — sprint capacity shifts to fixes, not features.
4. **Roll back recent risky changes** — the last few launches are the prime suspects; revert or flag them off.
5. **Postmortem** — blameless analysis of what consumed the budget; action items tracked.
6. **Do not "borrow" from next month** — rolling windows already recover automatically; calendar windows require waiting out the month.

## 8. Policy on Healthy Budget

When budget is abundant (> 50%):

- **Spend it deliberately** — launch the risky feature, run the experiment, do the migration.
- **Don't waste it on recklessness** — the budget is for *calculated* risk, not for skipping tests.
- **Use it to accelerate** — teams with healthy budgets can move faster; that is the point.

## 9. Reset & Window Mechanics

- **Rolling window (28d):** budget recovers continuously as old bad data ages out — good for fast recovery after a fix.
- **Calendar window (month):** a breach freezes the count for the rest of the month; recovery waits for the reset.
- **Choose rolling** for most services so the policy self-heals; use calendar only when contracts demand it.

## 10. Anti-Patterns

- **Ignoring the budget** — shipping anyway when exhausted defeats the purpose.
- **Re-setting the SLO after a breach** to "make the budget look fine" — that hides the incident; change SLOs only via the quarterly review.
- **Alerting on the SLI, not the burn rate** — a flat SLO-compliance alert is too slow; burn-rate alerts catch outages in minutes.
- **One-size budget for all services** — a 99.99% SLO for an internal tool wastes engineering effort.
- **No owner** — an error budget with no accountable team is never enforced.

## Quick Start

1. Compute budget = 1 − SLO target.
2. Record `error_budget_remaining` as a PromQL series.
3. Add fast (14.4×/1h) and slow (6×/6h) burn-rate alerts.
4. Add an exhaustion alert (< 0%).
5. Publish the tiered policy with action per remaining-budget band.
6. Review budget weekly in the team standup; enforce the freeze on exhaustion.
