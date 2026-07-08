# k6 Test Types

Standard test shapes and when to use them.

## Smoke test
Tiny load (1–2 VUs, short) to verify the script runs and the system is reachable.

```javascript
export let options = { vus: 1, iterations: 1 };
```

## Load test
Constant or stepped VUs to measure behavior under expected traffic.

```javascript
export let options = { stages: [{ duration: '5m', target: 100 }] };
```

## Stress test
Push past expected peak to find the breaking point.

```javascript
stages: [{ duration: '10m', target: 200 }, { duration: '5m', target: 300 }]
```

## Soak test
Sustained medium load over hours to surface leaks and degradation.

```javascript
stages: [{ duration: '2h', target: 50 }]
```

## Spike test
Sudden large jump in VUs, then back down — tests elasticity.

```javascript
stages: [{ duration: '10s', target: 1000 }, { duration: '1m', target: 50 }]
```

## Breakpoint test
Incrementally increase load until the system fails, to find capacity.

Pair every test with thresholds so k6 exits non-zero on SLO breach.
