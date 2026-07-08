# Prometheus Recording Rules

Companion to `references/scrape-configs.md`. Recording rules pre-compute
expensive queries so dashboards and alerts stay fast.

## Syntax

```yaml
groups:
  - name: node_rules
    interval: 30s
    rules:
      - record: instance:node_cpu_utilisation:rate1m
        expr: |
          100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))
```

## Naming convention

`level:metric:operation` — e.g. `instance:node_cpu_utilisation:rate1m`:

- **level** — the label set the rule aggregates to (instance, job, cluster).
- **metric** — the underlying metric, namespaced.
- **operation** — the function (rate1m, sum, ratio).

Following this lets dashboards reuse rules without re-reading raw series.

## When to record

- A query is slow (>1s) on a dashboard loaded by many viewers.
- An alert expression is expensive and evaluated often.
- You repeatedly aggregate the same raw series across multiple views.

Do **not** record everything — rules add write load and TSDB cost. Record only
hot paths.

## Testing rules

```bash
promtool test rules tests/recording_test.yaml
```

```yaml
# tests/recording_test.yaml
rule_files:
  - recording_rules.yml
evaluation_interval: 1m
tests:
  - interval: 1m
    input_series:
      - series: 'node_cpu_seconds_total{mode="idle",instance="a"}'
        values: '1 0.9 0.8 0.7'
    promql_expr_test:
      - expr: instance:node_cpu_utilisation:rate1m
        exp_samples:
          - labels: {instance: a}
            value: 20  # 100 - (0.8*100)
```

## Pitfalls

- `interval` on the group overrides global; keep it >= scrape interval.
- Recording rules depend on raw data existing — if a source metric is renamed,
  the rule silently emits nothing. Lint with `promtool check rules`.
- Don't chain too many recording rules (A computed from B computed from C);
  each hop adds staleness.
