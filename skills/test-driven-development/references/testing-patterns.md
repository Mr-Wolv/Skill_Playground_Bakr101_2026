# Testing Patterns — TDD Reference

This reference expands the Test-Driven Development skill with concrete patterns, test types, double
strategies (fakes/mocks/stubs), and specialized techniques (characterization, mutation, property).
Use it when writing tests or designing a test suite. The governing principle from the skill stays:
**write the failing test first; "seems right" is not done.**

---

## 1. The Red-Green-Refactor Cycle (core pattern)

1. **RED** — write a test that fails (because the behavior doesn't exist yet). A test that passes immediately proves nothing.
2. **GREEN** — write the *minimum* code to make it pass. No gold-plating, no extra features.
3. **REFACTOR** — with tests green, improve naming/structure/duplication. Run tests after every step.
4. **Repeat** — each new behavior starts a new RED. Small steps beat big leaps.

## 2. The Prove-It Pattern (bug fixes)

2. **Reproduce before fixing** — write a test that demonstrates the bug; it must FAIL first.
3. **Fix until green** — implement the minimal fix; the test now passes, proving the fix.
4. **Run the full suite** — confirm no regressions were introduced.

## 3. Test Pyramid & Sizes

5. **Pyramid shape** — ~80% unit (small), ~15% integration (medium), ~5% e2e (large). Most confidence per dollar is at the base.
6. **Small tests** — single process, no I/O/network/DB; milliseconds each. Pure logic, transforms.
7. **Medium tests** — multi-process, localhost only; seconds. API tests with a test DB, component tests.
8. **Large tests** — external services allowed; minutes. Reserve for critical user flows only.
9. **Decision guide** — pure logic → unit; crosses a boundary (API/DB/FS) → integration; critical flow → e2e.

## 4. Test Structure Patterns

10. **Arrange-Act-Assert** — set up state, perform the action, verify the outcome. One clear narrative per test.
11. **One assertion per concept** — separate tests for "rejects empty title" vs "trims whitespace" vs "enforces max length." Each names one behavior.
12. **DAMP over DRY** — tests should read like a specification; self-contained duplication is fine. Shared setup that obscures intent is not.
13. **Descriptive names** — `it('sets status to completed and records timestamp')`, never `it('works')` or `it('test3')`.

## 5. What to Assert (state vs interaction)

14. **Assert on state/outcome, not implementation** — test the result (`tasks[0].createdAt > tasks[1].createdAt`), not internal calls (`expect(db.query).toHaveBeenCalledWith(...)`). Interaction tests break on harmless refactors.
15. **Test your code, not the framework** — don't write tests that only exercise third-party libraries.
16. **Avoid snapshot abuse** — large auto-snapshots nobody reviews; use sparingly and review every diff.

## 6. Test Doubles — Preference Order

Use the *simplest* double that gets the job done. Confidence decreases down this list:

17. **Real implementation** (preferred) — highest confidence; catches real integration bugs.
18. **Fake** — an in-memory stand-in you control (e.g. `FakeUserStore` with a `Map`). Fast, deterministic, real-ish behavior.
19. **Stub** — returns canned data, no logic. Use when you only need a return value.
20. **Mock (interaction)** — verifies *which methods were called*. Use sparingly, only at boundaries where real deps are slow/non-deterministic (external APIs, email, time).

Over-mocking produces suites that are green while production is broken. Mock only when the real
thing is too slow, flaky, or has uncontrolled side effects.

## 7. Specialized Test Types

21. **Characterization tests** — when touching legacy/unknown code, write tests that *capture current (even buggy) behavior* before refactoring. They lock today's output so refactors don't silently change behavior. Name them honestly (`characterizes current off-by-one`). Use the "golden master" variant: snapshot the output of a complex function and assert future runs match. This is the safe door into refactoring untested code.
22. **Property-based tests** — instead of examples, assert properties hold for *all* inputs (e.g. `sort(x)` is always ordered; `reverse(reverse(x)) == x`). Libraries: Hypothesis (Python), fast-check (JS), ScalaCheck. Great for parsers, serializers, math.
23. **Mutation testing** — inject small faults (flip `>` to `<`, drop a line) and confirm tests fail. If a mutant survives, your tests have a gap. Tools: mutmut, Stryker. Use periodically, not in the hot loop.
24. **Contract tests** — verify a client and a service agree on the API shape (Pact). Prevents integration breakage when services deploy independently.
25. **Regression tests** — a failing test captured from every past bug, so it can never return. The Prove-It pattern's permanent artifact.
26. **Boundary/edge tests** — empty, max, zero, negative, null, Unicode, concurrent, timeout. Bugs live at edges.
27. **Table-driven tests** — loop over `{input, want}` cases in one test function (idiomatic in Go/Rust); keeps many cases readable without copy-paste.
28. **Fuzz tests** — feed random/evil input to find crashes and panics (Go's `testing.F`, cargo-fuzz, Atheris). Excellent for parsers and decoders.

## 8. Async & Concurrency Testing

29. **Await explicitly** — never fire-and-forget; await the promise or the test ends before the assertion.
30. **Hermetic concurrency** — for race tests, use real threads/atomics (Go `-race`); fakes must be thread-safe or the test lies.
31. **Deterministic time** — inject a clock/`fake timers` instead of sleeping; `await delay(10)` is flaky.

## 9. Fixtures & Isolation

32. **Each test owns its state** — set up in `beforeEach`/arrange, tear down after. No shared mutable fixtures across tests (the #1 cause of order-dependent failures).
33. **Seed deterministically** — random data only from a seeded RNG so failures reproduce.
34. **Clean up resources** — close DB connections, delete temp files; a leaking test pollutes the next.

## 10. Anti-Patterns (from the skill, reinforced)

35. **Tests that pass on first run** — they may not test what you think. A RED first is mandatory evidence.
36. **Flaky tests** — timing/order dependence erodes trust; isolate state and use deterministic time.
37. **Skipping to make green** — disabling/skipping a test to pass CI hides a real gap. Fix or delete with reason.
38. **Mocking everything** — see preference order; prefer real > fake > stub > mock.
39. **Re-running a green test for reassurance** — a clean run adds nothing unless the code changed since.

## 11. Coverage & Heuristics

40. **Beyoncé Rule** — if you liked it (shipped it), you should have put a test on it. Infrastructure, refactors, and migrations are not responsible for catching your bugs; your tests are.
41. **Coverage is a floor, not a ceiling** — 100% line coverage with weak assertions is worse than 70% with meaningful tests. Watch *branch* and *mutation* scores, not just lines.
42. **Test the behavior, document the contract** — a good test suite is the executable specification of what the code must do.

## 12. When NOT to TDD

43. **Pure config / static content** — no behavioral impact, nothing to prove.
44. **Throwaway spikes** — prove the approach first, then throw it away and re-implement test-first. (Or keep the spike's tests.)
45. **Exploratory research** — when you don't yet know the shape of the solution; switch to TDD once it stabilizes.

## Quick Reference: Double Selection

| Need | Use | Confidence |
|------|-----|------------|
| Real behavior, fast enough | Real impl | ★★★★★ |
| Fast, controllable dependency | Fake | ★★★★ |
| Just need a return value | Stub | ★★★ |
| Verify a call happened (boundary only) | Mock | ★★ |

## Quick Reference: Test Type Picker

| Situation | Pattern |
|-----------|---------|
| New behavior | RED-GREEN-REFACTOR |
| Bug report | Prove-It |
| Legacy code refactor | Characterization / golden master |
| Parser/serializer | Property-based / fuzz |
| Independent services | Contract test |
| Past incident | Regression test |
| Many input cases | Table-driven |
