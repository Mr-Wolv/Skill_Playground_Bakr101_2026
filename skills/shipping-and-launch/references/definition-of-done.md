# Definition of Done — Shipping and Launch

The launch **Definition of Done (DoD)** is the gate a release must clear *before* it is exposed to
users, and again *after* it is live. It sits on top of the implementation DoD: code that was not
"done" per incremental-implementation standards is not launch-ready. This DoD adds the production
concerns the implementation DoD does not cover — monitoring, rollback, staged exposure, and
post-launch verification.

## Pre-Launch Gate (before user exposure)

### Code Quality
- [ ] All tests pass (unit, integration, e2e)
- [ ] Build succeeds with no warnings
- [ ] Lint and type checking pass
- [ ] Code reviewed and approved
- [ ] No TODO/FIXME that should be resolved before launch
- [ ] No `console.log` / debug statements in production code
- [ ] Error handling covers expected failure modes

### Security
- [ ] No secrets in code or version control (see `security-checklist.md`)
- [ ] `npm audit` / `pip-audit` / dependency scan shows no critical or high vulnerabilities
- [ ] Input validation on all user-facing endpoints
- [ ] Authentication and authorization checks in place
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options, Referrer-Policy)
- [ ] Rate limiting on authentication and expensive endpoints
- [ ] CORS scoped to specific origins (no wildcard `*`)

### Performance
- [ ] Core Web Vitals within "Good" thresholds (see `performance-checklist.md`)
- [ ] No N+1 queries in critical paths
- [ ] Images optimized (compression, responsive sizes, lazy loading)
- [ ] Bundle size within budget
- [ ] Database queries have appropriate indexes
- [ ] Caching configured for static assets and repeated queries

### Accessibility
- [ ] Keyboard navigation works for all interactive elements
- [ ] Screen reader conveys page content and structure
- [ ] Color contrast meets WCAG 2.1 AA (≥4.5:1 for text)
- [ ] Focus management correct for modals and dynamic content
- [ ] Error messages descriptive and associated with form fields
- [ ] No accessibility warnings in axe-core / Lighthouse (see `accessibility-checklist.md`)

### Infrastructure
- [ ] Environment variables set in production
- [ ] Database migrations applied (or a verified, reversible apply step exists)
- [ ] DNS and SSL configured and verified
- [ ] CDN configured for static assets
- [ ] Logging and error reporting configured
- [ ] Health check endpoint exists and responds 200

### Documentation
- [ ] README updated with new setup requirements
- [ ] API documentation current
- [ ] ADRs written for architectural decisions
- [ ] Changelog updated
- [ ] User-facing documentation updated (if applicable)

### Launch Mechanics
- [ ] Feature flag configured (if applicable) — off by default, with owner and expiration
- [ ] Rollback plan documented (trigger conditions + steps + DB considerations)
- [ ] Monitoring dashboards set up (errors, latency, traffic, business metrics)
- [ ] Team notified of deployment window
- [ ] Staging deploy passed full suite + manual smoke test

## During Rollout (at each stage: team → canary 5% → 25% → 50% → 100%)

- [ ] Error rate within 10% of baseline (advancing) / <2× baseline (no rollback)
- [ ] P95 latency within 20% of baseline (advancing) / <50% above (no rollback)
- [ ] Client JS errors: no new error types at >0.1% of sessions
- [ ] Business metrics neutral or positive (no decline >5%)
- [ ] Each stage held for its monitoring window (24–48h canary, 1 week full)
- [ ] Rollback to previous percentage possible at any point

## Post-Launch Gate (first hour, then daily for a week)

- [ ] Health endpoint returns 200
- [ ] Error monitoring shows no new error types
- [ ] Latency dashboard shows no regression
- [ ] Critical user flow works manually
- [ ] Logs are flowing and readable
- [ ] Rollback mechanism verified ready (dry run if possible)
- [ ] Feature flag cleanup scheduled (remove dead path within 2 weeks of full rollout)

## Rollback Triggers (any one → roll back immediately)

- [ ] Error rate > 2× baseline
- [ ] P95 latency > 50% above baseline
- [ ] User-reported issues spike
- [ ] Data integrity issues detected
- [ ] Security vulnerability discovered

## Using the Launch DoD

The pre-launch gate is binary: all green or do not deploy. The rollout and post-launch gates are
*continuous* — monitor at every stage, advance only on green, and roll back on red. A launch is not
"done" until the full-rollout week passes clean. Until then, the feature is live-but-watched, not
finished.

> Every launch is reversible, observable, and incremental. A launch that fails this DoD — no
> monitoring, no rollback, big-bang exposure — is not a launch, it is a hope.
