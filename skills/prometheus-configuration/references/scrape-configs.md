# Prometheus Scrape Configs

Deep dive companion to `references/details.md`. Covers service discovery,
relabeling, and scrape hygiene for a production Prometheus.

## Minimal static config

```yaml
scrape_configs:
  - job_name: "api"
    static_configs:
      - targets: ["api:8080"]
    metrics_path: /metrics
    scrape_interval: 15s
```

## Relabeling — the core lever

Relabeling rewrites the target label set before scraping. Most real configs
live or die on this.

```yaml
  - job_name: "kubernetes-pods"
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # keep only pods that expose a metrics port
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      # rewrite the metrics path from the annotation
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      # set a stable job label from the pod
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: replace
        target_label: app
```

## Common relabel actions

| Action | Effect |
|--------|--------|
| `keep` | drop targets not matching `regex` |
| `drop` | drop targets matching `regex` |
| `replace` | copy/transform a label value |
| `labelmap` | promote SD metadata to labels |
| `hashmod` | shard targets across instances |

## Scrape hygiene

- Set `scrape_timeout` < `scrape_interval` (default equal — risky under load).
- Use `__param_*` / `params` for targets that need query args.
- Honor `Authorization` via `authorization` / `bearer_token_file`, never inline
  secrets in the config — mount from a secret store.
- Limit series cardinality: high-label dimensions (user_id, request_id) explode
  the TSDB. Drop them in relabel `action: labeldrop` or `drop`.

## Self-checks

- `up{job="api"} == 0` → target down or wrong path/port.
- `scrape_duration_seconds` near `scrape_timeout` → slow exporter; raise timeout
  or reduce work.
- `prometheus_tsdb_head_series` climbing unboundedly → cardinality leak.
