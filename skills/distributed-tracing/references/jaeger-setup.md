# Jaeger Setup — deep dive

This reference extends the inline "Jaeger Setup" in `details.md` with
production deployment models, storage backends, sampling, and querying.

## Deployment models

- **all-in-one** (`jaegertracing/all-in-one`) — single process, in-memory
  storage. Use for local dev and demos only; spans are lost on restart.
- **production** — separate `jaeger-collector`, `jaeger-query`,
  `jaeger-ingester`, with a real storage backend. Deploy via the Jaeger
  Operator (recommended on Kubernetes) or the `jaeger` Helm chart.

### Operator (Kubernetes)

```bash
kubectl create namespace observability
kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.51.0/jaeger-operator.yaml -n observability

kubectl apply -f - <<'EOF'
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: https://elasticsearch:9200
  ingress:
    enabled: true
EOF
```

## Storage backends

| Backend | Durability | Query latency | Notes |
|---------|-----------|---------------|-------|
| memory | none | lowest | all-in-one only |
| Cassandra | high | medium | mature, multi-DC |
| Elasticsearch | high | low | most common in prod |
| Badger | medium | low | embedded, single-node |
| gRPC plugin | custom | varies | bring your own |

## Sampling

Samplers decide which traces to keep. Without sampling, high-traffic services
drown storage.

```yaml
# Collector sampling config (tracing.sampling.strategies-file)
default_strategy:
  service_strategies:
    - service: "my-service"
      type: probabilistic
      param: 0.1          # keep 10%
    - service: "auth-service"
      type: ratelimiting
      param: 100          # 100 traces/sec max
  operation_strategies:
    - service: "my-service"
      operation: "GET /health"
      type: probabilistic
      param: 0.001
```

Per-service head sampling can also be set on the SDK side, but the collector
strategy file is the single source of truth in production.

## Receiving spans

| Protocol | Port | Format |
|----------|------|--------|
| Jaeger thrift (UDP) | 6831 | compact |
| Jaeger thrift (UDP) | 6832 | binary |
| Jaeger gRPC | 14250 | OTLP/OTLP-J |
| Zipkin (HTTP/thrift) | 9411 | Zipkin v1/v2 |
| OTLP HTTP | 4318 | OpenTelemetry |
| OTLP gRPC | 4317 | OpenTelemetry |

Prefer OTLP (4317/4318) for new services; it is the vendor-neutral path and
lets you switch backends without re-instrumenting.

## Querying

- UI: `http://<jaeger>:16686`. Filter by service, operation, duration, tags.
- Trace JSON API: `GET /api/traces?service=my-service&limit=20`.
- Compare traces with the "Compare" view to find latency regressions.

## Operational checks

- Collector healthy: `GET /metrics` shows `jaeger_collector_spans_received`.
- Look for `jaeger_collector_spans_dropped_total > 0` → sampling too low or
  storage unavailable.
- Old spans: set `es.max-span-age` / TTL so storage does not fill.
