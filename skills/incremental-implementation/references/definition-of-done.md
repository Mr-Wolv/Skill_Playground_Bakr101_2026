# Definition of Done — Incremental Implementation

The **Definition of Done (DoD)** is the project-wide gate that every increment must clear
*in addition* to the per-increment checklist. The increment checklist (`npm test`, `npm run build`,
commit) verifies the *local* slice. The DoD verifies the *whole* that the slice now belongs to.
An increment is not "done" until every box below is checked. DoD is binary: either it passes or it
does not — there is no "done enough."

## 1. Functional Correctness

- [ ] **Acceptance criteria met** — every acceptance criterion from the source task is satisfied and demonstrable.
- [ ] **Works end-to-end** — the feature works through the full stack (DB → API → UI), not just in isolation.
- [ ] **Edge cases handled** — empty input, max input, concurrent calls, network failure, and invalid data are covered.
- [ ] **Error paths exercised** — failures return correct status codes / messages; no unhandled exceptions leak to users.
- [ ] **Behavior matches spec** — the implemented behavior matches what was requested, not what was convenient.

## 2. Automated Tests

- [ ] **Tests pass** — the full suite is green: `npm test` (or `pytest`, `go test ./...`, etc.).
- [ ] **New behavior is tested** — every new code path has at least one test proving it works.
- [ ] **Bug fixes have reproduction tests** — any fix is guarded by a test that failed before the fix.
- [ ] **No regressions** — existing tests still pass; no previously-green test was deleted or muted to make the suite green.
- [ ] **Flaky tests fixed, not retried** — intermittent failures were rooted out, not looped or `@flaky`-ignored.
- [ ] **Coverage not degraded** — if coverage is tracked, the net change does not reduce it below the agreed floor.

## 3. Build & Static Analysis

- [ ] **Build succeeds** — `npm run build` (or equivalent) completes with no errors and ideally no new warnings.
- [ ] **Type checking passes** — `npx tsc --noEmit` / `mypy` / `go vet` show no new errors.
- [ ] **Linting passes** — `npm run lint` is clean; no disabled rules to silence a finding.
- [ ] **No debug leftovers** — no `console.log`, `print`, `fmt.Println` debug statements, no commented-out dead code left in.
- [ ] **No TODO/FIXME that blocks launch** — outstanding markers are tracked, not silently shipped.

## 4. Code Review

- [ ] **Reviewed and approved** — at least one other human (or fresh-context reviewer) approved the change.
- [ ] **Scope discipline held** — only the task's files were touched; no "while I was here" cleanup or refactor.
- [ ] **Single concern per increment** — the change does one logical thing; mixed concerns were split into separate commits.
- [ ] **Simplicity confirmed** — no premature abstraction; the naive obviously-correct version shipped; optimizations came only after tests proved correctness.
- [ ] **Naming and structure clear** — a reviewer can understand intent without a meeting.

## 5. Documentation

- [ ] **Public API documented** — new endpoints, exported functions, or config keys are documented.
- [ ] **README/setup updated** — new environment variables, services, or run steps are reflected in docs.
- [ ] **Decisions captured** — any non-obvious architectural choice has an ADR or inline rationale.
- [ ] **Changelog updated** — user-visible change noted in the changelog/release notes.

## 6. Observability & Operability

- [ ] **Observable** — key actions emit metrics, logs, or traces; production failures are diagnosable without code changes.
- [ ] **Health check viable** — if the service exposes a health endpoint, the new code does not break it.
- [ ] **Safe defaults** — new behavior defaults to conservative/safe; opt-in features are off by default.
- [ ] **Feature-flagged if incomplete** — work-in-progress behind a flag is not user-visible until ready.

## 7. Rollback & Safety

- [ ] **Independently revertable** — the increment can be reverted (or its flag disabled) without breaking the system.
- [ ] **Migrations have rollbacks** — any DB migration ships with a corresponding down-migration or idempotent backout.
- [ ] **No destructive surprises** — deletes/overwrites are scoped and, where risky, reversible.
- [ ] **Secrets not committed** — no credentials, keys, or tokens in the diff or VCS history.

## 8. Integration State

- [ ] **No uncommitted changes** — the working tree is clean; `git status` shows nothing pending.
- [ ] **Main branch still green** — after merge, CI on the integration branch passes.
- [ ] **Follow-up noted** — anything discovered outside scope is captured as a new task, not silently fixed inline.

## Using the DoD

Apply the DoD at the **end of a task** (after all its increments), not after each slice. After each
slice use the lighter increment checklist; after the whole task, run this full gate. If any box
cannot be checked, the task is **not done** — revert or finish it; do not mark it complete and move on.

> A task marked "done" that fails the DoD is worse than an unfinished task: it hides the gap from
> everyone downstream. The DoD exists so "done" means the same thing to every agent and human.
