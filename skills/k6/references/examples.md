# k6 Examples

Minimal runnable scripts. Run with `k6 run script.js`.

## GET smoke test

```javascript
import http from 'k6/http';
import { check } from 'k6';

export default function () {
  const res = http.get('https://test.k6.io/');
  check(res, { 'status 200': (r) => r.status === 200 });
}
```

## POST with JSON body

```javascript
import http from 'k6/http';

export let options = { vus: 10, duration: '30s' };

export default function () {
  http.post('https://httpbin.test.k6.io/post',
    JSON.stringify({ hello: 'world' }),
    { headers: { 'Content-Type': 'application/json' } });
}
```

## Staged load

```javascript
export let options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '3m', target: 50 },
    { duration: '1m', target: 0 }
  ]
};
```

## Thresholds

```javascript
export let options = {
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01']
  }
};
```

See `references/javascript-api.md`, `references/test-types.md`, and
`references/scenarios-executors.md` for the full reference.
