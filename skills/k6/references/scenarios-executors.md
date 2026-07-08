# k6 Scenarios & Executors

Scenarios let one script model multiple, independent workloads. Executors
determine how VUs are scheduled.

## Scenarios block

```javascript
export let options = {
  scenarios: {
    browse: { executor: 'constant-vus', vus: 10, duration: '5m', exec: 'browse' },
    checkout: { executor: 'ramping-vus', startVUs: 0, stages: [{ target: 50, duration: '2m' }], exec: 'checkout' }
  }
};
export function browse() { /* ... */ }
export function checkout() { /* ... */ }
```

## Executors

- `shared-iterations` — fixed total iterations across VUs.
- `per-vus-iterations` — each VU runs N iterations.
- `constant-vus` — hold a fixed VU count for a duration.
- `ramping-vus` — stage-based VU ramp.
- `constant-arrival-rate` — fixed requests/sec (needs `rate` + `preAllocatedVUs`).
- `ramping-arrival-rate` — stage-based requests/sec.
- `externally-controlled` — driven by `k6 run --out` / control API.

## Tips

- Prefer arrival-rate executors when you care about RPS, not concurrency.
- `preAllocatedVUs` must cover the peak rate or k6 will drop iterations.
- Use `exec` to point a scenario at a specific exported function.
