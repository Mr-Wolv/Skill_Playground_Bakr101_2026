# k6 JavaScript API

The core objects available in every k6 script.

## Lifecycle functions

- `init` context — module-level code runs once per VU init.
- `export function setup()` — runs once before the test; return value is passed to `default`/`teardown`.
- `export default function (data) {}` — the VU function, run for the whole duration.
- `export function teardown(data) {}` — runs once after the test.

## Key modules

```javascript
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate } from 'k6/metrics';
import exec from 'k6/execution';
```

## http

- `http.get(url, params)`, `http.post(url, body, params)`
- `http.batch([...requests])` — send in parallel
- Response: `.status`, `.body`, `.json()`, `.timing`, `.headers`

## checks & thresholds

```javascript
check(res, { 'status 200': (r) => r.status === 200 });
export let options = {
  thresholds: { http_req_failed: ['rate<0.01'], http_req_duration: ['p(95)<300'] }
};
```

## metrics

`Trend`, `Rate`, `Counter`, `Gauge` — custom metrics via `k6/metrics`.

## execution

`k6/execution` exposes `exec.vu.idInTest`, `exec.scenario.name`,
`exec.instance.vusActive` for runtime introspection.
