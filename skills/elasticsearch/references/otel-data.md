# Querying OpenTelemetry Data

Elasticsearch commonly stores OTEL data exported via the OTel Collector. The
default data streams are:

- `logs-*-*` (OTEL logs)
- `traces-*-*` (OTEL traces / spans)
- `metrics-*-*` (OTEL metrics)

## Logs

```json
{
  "query": {
    "bool": {
      "must": [{ "match": { "body": "timeout" } }],
      "filter": [{ "range": { "@timestamp": { "gte": "now-1h" } } }]
    }
  },
  "sort": [{ "@timestamp": "desc" }]
}
```

Key fields: `service.name`, `severity_text`, `trace_id`, `span_id`.

## Traces / Spans

Find slow spans:

```json
{
  "query": { "range": { "duration": { "gte": 1000000 } } },
  "sort": [{ "duration": "desc" }]
}
```

Correlate a log to its trace with `trace_id`, then pivot to `traces-*-*` using
the same `trace_id` to see the full waterfall.

## Metrics

```json
{
  "aggs": {
    "by_service": {
      "terms": { "field": "resource.attributes.service.name" },
      "aggs": { "p95": { "percentiles": { "field": "histogram_value", "percents": [95] } } }
    }
  }
}
```

## Correlation pattern

1. Spot an anomaly in `metrics-*-*` (e.g. p95 latency spike).
2. Pull `trace_id`s from the affected service in `traces-*-*`.
3. Join to `logs-*-*` on `trace_id` to read the failure context.

This three-stream join is the standard OTEL-in-Elastic observability loop.
