# Definition of Done — Planning and Task Breakdown

This **Definition of Done (DoD)** is the planning-side gate. It applies to the *plan and task list*
before any code is written — the standing bar a plan must clear before it is trusted to drive
implementation. A good plan is what makes incremental implementation possible; a vague plan produces
a tangled mess. The DoD here answers "is this plan itself done?" — it complements the
implementation-side DoD that each task later clears when coded.

## 1. Plan Structure

- [ ] **Written, not verbal** — the plan lives in `tasks/plan.md`; the checklist lives in `tasks/todo.md`. No "it's in my head."
- [ ] **Read-only discipline held** — no code was written during planning; output is a plan document, not a partial implementation.
- [ ] **Overview present** — one paragraph states what is being built and why.
- [ ] **Architecture decisions captured** — key choices (and their rationale) are written, not assumed.
- [ ] **Risks and mitigations listed** — every meaningful risk has an impact rating and a mitigation strategy.

## 2. Task Decomposition

- [ ] **Every task is atomic** — each task does one thing; if the title needs an "and," it is two tasks.
- [ ] **Acceptance criteria on every task** — each task states specific, testable conditions for "done."
- [ ] **Verification step on every task** — each task names the command/manual check that proves it works.
- [ ] **Files likely touched listed** — each task enumerates the files it expects to change.
- [ ] **Dependencies identified** — each task lists what it depends on, or "None."
- [ ] **Sized Small/Medium** — no task exceeds ~5 files; anything L/XL is broken down further.
- [ ] **Acceptance criteria fit in ≤3 bullets** — if not, the task is too big and must split.

## 3. Slicing & Ordering

- [ ] **Vertical slices, not horizontal** — tasks build complete paths through the stack, not "all the DB, then all the API."
- [ ] **Dependency graph respected** — implementation order is bottom-up; foundations (schema) precede dependents (UI).
- [ ] **High-risk tasks early** — the riskiest/most uncertain work comes first to fail fast.
- [ ] **Each task leaves a working state** — after any task the system still builds and existing tests still pass.
- [ ] **Checkpoints between phases** — explicit verification gates after every 2–3 tasks or each phase.
- [ ] **Checkpoints have a human gate** — at least one checkpoint requires human review before proceeding.

## 4. Parallelization Plan

- [ ] **Parallel-safe tasks identified** — independent slices / tests / docs are marked safe to run concurrently.
- [ ] **Sequential dependencies called out** — migrations, shared-state changes, and dependency chains are marked must-be-sequential.
- [ ] **Coordinated work has a shared contract** — features sharing an API contract define the contract first, then parallelize.

## 5. Scope & Boundaries

- [ ] **Refactor work routed correctly** — if this is an ambiguous-refactor concern, it was sent to `request-refactor-plan`, not crammed here.
- [ ] **Out of scope stated** — the plan notes what it deliberately does NOT cover.
- [ ] **No solutioning beyond decomposition** — the plan decomposes and orders; it does not pre-emptively write implementation details.

## 6. Human Approval

- [ ] **Plan reviewed by human** — the human has read and approved the plan before implementation starts.
- [ ] **Open questions resolved** — every open question needing human input was answered or explicitly deferred.
- [ ] **Estimates sane** — scope tags reflect realistic effort; no task claims "2 hours" for a 5-file cross-cutting change.

## 7. Tooling Compatibility

- [ ] **Convention paths used** — outputs use `tasks/plan.md` and `tasks/todo.md` so `/build` and downstream tooling can consume them.
- [ ] **Tasks actionable by an agent** — each task is small enough that an agent can implement, test, and verify it in a single focused session.

## Using the Planning DoD

Run this gate before leaving plan mode. If any box is unchecked, the plan is **not done** and will
produce unreliable implementation. A plan that passes here is what lets the incremental-implementation
DoD be applied cleanly later — each task already has acceptance criteria, a verification step, and a
known dependency order.

> Planning *is* the task. A plan that passes this DoD turns "I'll figure it out as I go" into a
> checkpointed, reviewable, parallelizable sequence that survives session boundaries and compaction.
