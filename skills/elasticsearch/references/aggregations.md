# Aggregations Reference

Metric and bucket aggregations referenced from the main skill.

## Metric aggregations

- `avg`, `sum`, `min`, `max` — single-value stats
- `value_count` — number of values
- `cardinality` — distinct count (approximate, tune with `precision_threshold`)
- `percentiles` / `percentile_ranks` — distribution
- `top_hits` — best-matching docs per bucket
- `geo_centroid` / `geo_bounds` — spatial

```json
{
  "aggs": {
    "status_counts": { "terms": { "field": "status", "size": 10 } },
    "latency_p95": { "percentiles": { "field": "latency_ms", "percents": [50, 95, 99] } },
    "unique_users": { "cardinality": { "field": "user.id", "precision_threshold": 4000 } }
  }
}
```

## Bucket aggregations

- `terms` — top values (watch for `shard_size` / high-cardinality drift)
- `date_histogram` — time buckets (`fixed_interval`, `calendar_interval`)
- `histogram` — numeric buckets
- `range` / `date_range` — explicit ranges
- `composite` — paginated, deep bucket enumeration (for exports)
- `filters` — named, independent filter buckets
- `significant_terms` — terms that are unusually associated with the query
- `nested` / `reverse_nested` — aggregate inside/outside nested docs

## Nested aggregation example

```json
{
  "aggs": {
    "comments": {
      "nested": { "path": "comments" },
      "aggs": { "top_authors": { "terms": { "field": "comments.author" } } }
    }
  }
}
```

Use `composite` when you need to page through more buckets than `size` allows;
otherwise deep `terms` aggregations are truncated at `shard_size`.
