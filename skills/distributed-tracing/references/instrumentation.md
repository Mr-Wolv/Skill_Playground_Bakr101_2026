# Application Instrumentation — deep dive

Extends the inline "Application Instrumentation" in `details.md` with manual
span creation, context propagation, and common pitfalls.

## Initialize once, reuse the tracer

Create the `TracerProvider` at process startup and register it globally. Do
**not** create a new provider per request — it leaks processors.

```python
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

resource = Resource.create({SERVICE_NAME: "checkout-service"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger:4317")))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)
```

## Manual spans

Use `start_as_current_span` so child spans nest correctly:

```python
with tracer.start_as_current_span("charge_card") as span:
    span.set_attribute("payment.method", "card")
    span.set_attribute("payment.amount", 4200)
    try:
        do_charge()
    except Exception as e:
        span.record_exception(e)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        raise
```

- `set_attribute` adds queryable tags.
- `record_exception` attaches the stack trace.
- `set_status(ERROR)` marks the span failed so you can alert on error rate.

## Context propagation

Spans across services connect only if you propagate the trace context. With
auto-instrumentation (`opentelemetry-instrumentation-http`) this is automatic
for HTTP/gRPC. For custom transports (queues, raw sockets) inject/extract:

```python
from opentelemetry.propagate import inject, extract
from opentelemetry.context import attach, detach

# producer
headers = {}
inject(headers)
publish(topic, body, headers)

# consumer
ctx = extract(incoming_headers)
token = attach(ctx)
try:
    process()
finally:
    detach(token)
```

## Span kinds

| Kind | Use |
|------|-----|
| SERVER | inbound request handler |
| CLIENT | outbound call (DB, HTTP) |
| PRODUCER | message publish |
| CONSUMER | message receive |
| INTERNAL | in-process work |

## Pitfalls

- Spanning everything = noise. Instrument boundaries (handlers, external
  calls), not every helper.
- `BatchSpanProcessor` buffers — flush on shutdown: `provider.shutdown()`.
- Long-running spans hold memory; keep spans short-lived.
- Don't put PII (emails, tokens) in attributes — redact first.
