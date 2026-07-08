# Query DSL Reference

Common Elasticsearch query types referenced from the main skill. All examples
use the `_search` endpoint with a JSON body.

## Match (full-text)

```json
{ "query": { "match": { "title": "quick brown fox" } } }
```

## Term (exact, keyword)

```json
{ "query": { "term": { "status": { "value": "published" } } } }
```

## Terms (several exact values)

```json
{ "query": { "terms": { "tags": ["go", "rust", "python"] } } }
```

## Range (numeric / date)

```json
{
  "query": {
    "range": {
      "@timestamp": { "gte": "now-24h", "lt": "now" }
    }
  }
}
```

## Wildcard / Regexp (avoid on large fields)

```json
{ "query": { "wildcard": { "path": { "value": "logs/*" } } } }
{ "query": { "regexp": { "email": ".*@example\\.com" } } }
```

## Nested (object arrays)

```json
{
  "query": {
    "nested": {
      "path": "comments",
      "query": { "match": { "comments.author": "alice" } }
    }
  }
}
```

## Exists (non-null field)

```json
{ "query": { "exists": { "field": "user.id" } } }
```

## Multi-match (across fields)

```json
{
  "query": {
    "multi_match": {
      "query": "latency",
      "fields": ["title^2", "body"]
    }
  }
}
```

## Bool (combine must/should/must_not/filter)

```json
{
  "query": {
    "bool": {
      "must": [{ "match": { "title": "incident" } }],
      "filter": [{ "term": { "env": "prod" } }],
      "must_not": [{ "exists": { "field": "resolved_at" } }]
    }
  }
}
```

Prefer `filter` over `must` for boolean conditions — filters are cached and do
not affect relevance scoring.
