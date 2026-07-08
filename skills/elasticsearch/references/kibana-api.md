# Kibana API Reference

Operations against the Kibana HTTP API for dashboards, data views, saved
objects, and alerting rules. Base URL is your Kibana host (e.g.
`http://localhost:5601`). Most calls require `kbn-xsrf: true` and an auth
header.

## Saved Objects (export / import)

```bash
# Export a dashboard and its dependencies
curl -X POST "$KIBANA/api/saved_objects/_export" \
  -H 'kbn-xsrf: true' -H 'Content-Type: application/json' \
  -d '{ "objects": [{ "type": "dashboard", "id": "abc-123" }], "includeReferencesDeep": true }' \
  -o dashboard.ndjson
```

## Data Views

```bash
# Create a data view over an index pattern
curl -X POST "$KIBANA/api/data_views/data_view" \
  -H 'kbn-xsrf: true' -H 'Content-Type: application/json' \
  -d '{ "data_view": { "title": "logs-*", "timeFieldName": "@timestamp" } }'
```

## Alerting Rules

```bash
curl -X POST "$KIBANA/api/alerting/rule" \
  -H 'kbn-xsrf: true' -H 'Content-Type: application/json' \
  -d '{
    "name": "High error rate",
    "rule_type_id": ".index-threshold",
    "consumer": "alerts",
    "params": {
      "index": ["logs-*"],
      "timeField": "@timestamp",
      "aggType": "count",
      "groupBy": "all",
      "termSize": 1,
      "timeWindowSize": 5,
      "timeWindowUnit": "m",
      "thresholdComparator": ">",
      "threshold": [100]
    },
    "schedule": { "interval": "1m" },
    "actions": []
  }'
```

## Spaces

```bash
curl "$KIBANA/api/spaces/space" -H 'kbn-xsrf: true'
```

Always pass `kbn-xsrf: true` on state-changing calls; omitting it is the most
common 400 from automation scripts.
