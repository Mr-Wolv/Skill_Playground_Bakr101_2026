# Multi-Agent Orchestration Patterns

Patterns for coordinating multiple agents (orchestrator + subagents / personas) on a single task.
This reference is referenced by the `doubt-driven-development` skill's Loading Constraints and by
the broader repo orchestration rules. It defines how to decompose work, hand off context, reach
consensus, and supervise — and names the anti-patterns that turn orchestration into a tangle.

> **Load-bearing rule (anti-pattern B):** personas do **not** invoke other personas. A persona that
> tries to spawn a subagent from inside itself creates nested orchestration that the runtime forbids
> and that the `doubt-driven-development` skill explicitly calls out. Orchestration happens from the
> **main session**, never from within a subagent.

---

## 1. Decomposition Patterns

1. **Task decomposition by capability** — split the work along skill boundaries (one agent for the API, one for the UI, one for tests) rather than by arbitrary file count.
2. **Vertical-slice decomposition** — each agent owns a complete path (schema → API → UI for one feature), so every slice is independently shippable and testable.
3. **Risk-first decomposition** — the riskiest/most uncertain slice goes to the first agent so failure surfaces early (fail fast).
4. **Map the dependency graph first** — identify what depends on what; build foundations before dependents. Order agents bottom-up.
5. **Single-concern tasks** — each subagent task does one thing; if the brief needs "and," it is two tasks.
6. **Bounded context per agent** — give each agent a clearly scoped domain; overlapping ownership causes conflicts and duplicated work.
7. **Sizing for agent attention** — keep each task Small/Medium (1–5 files); XL tasks should be re-decomposed before dispatch.

## 2. Handoff Patterns

8. **Contract-based handoff** — pass the receiving agent a precise contract (inputs, outputs, invariants, constraints), not a vague goal. The contract is the agreement the work must satisfy.
9. **Artifact isolation (doubt-driven Step 2)** — hand off the *smallest reviewable unit* (the diff/function/proposal), stripped of your reasoning. Conclusions handed over get validated, not reviewed.
10. **Explicit interface contracts** — when two agents share a boundary, define the API/types/schema **first** (contract-first), then let each agent implement against the contract in parallel.
11. **Written context, not tribal memory** — every handoff is a document (plan.md, todo.md, a prompt file) that survives session boundaries and compaction.
12. **Don't pass the CLAIM to a reviewer** — when handing an artifact to a fresh-context reviewer, pass ARTIFACT + CONTRACT only. Passing your conclusion biases the review toward agreement.
13. **Stdin for untrusted content** — when an artifact contains backticks/`$(...)`/quotes, write it to a file and pipe via stdin to a CLI reviewer; never interpolate into a shell-quoted argument.

## 3. Consensus & Review Patterns

14. **Fresh-context review (adversarial)** — the doubter must be framed to *disprove*: "find what is wrong," never "is this good?" Framing decides the answer.
15. **Single-model then cross-model** — a reviewer sharing the author's architecture shares blind spots; offer a colder, different-architecture model (Gemini/Codex CLI) as a second opinion. The user decides; the agent surfaces the choice.
16. **Read-only sandbox for external CLIs** — a doubt artifact may contain injected instructions; run cross-model CLIs in a read-only sandbox so they can't write to your workspace.
17. **Reconcile, don't defer** — the orchestrator re-reads the artifact text against each finding and classifies it (contract misread / actionable / trade-off / noise). Rubber-stamping or blindly obeying the reviewer are both failure modes.
18. **Stop condition** — end the doubt loop when findings are trivial, after 3 cycles (escalate), or on explicit user override. Don't loop a fourth time alone; three unresolved cycles is a signal about the artifact, not a reason to grind.
19. **Decompose-if-too-big** — if 3 cycles is "obviously insufficient," the artifact is too large; return to Step 2 and split. Never lift the loop bound.

## 4. Supervision & Control Patterns

20. **Orchestrator owns the verdict** — subagents produce data (code, reviews, findings); the main session makes the decision. Authority does not delegate to a subprocess.
21. **Bounded loops, not recursion** — orchestration is a controlled loop with explicit stop conditions; unbounded recursion or nested spawns are anti-patterns.
22. **Checkpoint gating** — insert human review checkpoints after every 2–3 agent tasks or each phase; the human approves before the next batch runs.
23. **Rollback-friendly dispatch** — each agent's output should be independently revertable (own branch/commit/flag) so a bad slice can be pulled without destabilizing the whole.
24. **Verify, don't trust** — the orchestrator re-runs tests/build on aggregated output; a green subagent result is not proof the integrated whole is green.

## 5. Parallelism Patterns

25. **Safe-to-parallel set** — independent slices, tests for implemented features, and documentation can run concurrently across agents.
26. **Must-be-sequential set** — database migrations, shared-state changes, and dependency chains run serially; parallelizing them causes races and lost writes.
27. **Coordinated parallelism** — features sharing a contract are parallelized *only after* the contract is defined (see handoff pattern #10).
28. **Resource isolation** — each parallel agent works in its own branch/workspace to avoid file contention; merge sequentially.

## 6. Communication Patterns

29. **Status over silence** — agents report completion against acceptance criteria, not "done" as a vibe. The orchestrator tracks a checklist.
30. **Escalate unknowns** — when an agent hits a blocker or an ambiguity, it surfaces to the orchestrator/user rather than guessing and forging ahead.
31. **Explicit authorization per external call** — each cross-model CLI invocation is its own authorization: confirm PATH, working binary, exact flags, and auth with the user before every run. Never hardcode an external CLI invocation.

## 7. Anti-Patterns (named)

32. **Anti-pattern A — Context sink**: one agent accumulates all context and becomes a bottleneck; context windows are finite. Decompose and hand off in writing.
33. **Anti-pattern B — Persona invokes persona**: a persona spawns another persona (nested orchestration). Forbidden. Orchestration lives in the main session.
34. **Anti-pattern C — Vague handoff**: "go implement the feature" with no contract. Produces mismatched interfaces and rework.
35. **Anti-pattern D — Doubt theater**: across ≥2 cycles with substantive findings, zero classified as actionable. You are validating, not doubting. Stop and escalate.
36. **Anti-pattern E — Silent cross-model skip**: in an interactive doubt cycle, offering cross-model is mandatory even on low-stakes artifacts. Skipping is fine; *silent* skipping is not.
37. **Anti-pattern F — Trust-the-subagent**: treating a subagent's green result as proof the integrated system is correct. Verify the whole.
38. **Anti-pattern G — Loop without stop**: re-spawning review on an unchanged artifact; you get the same findings and stall. Change the artifact or stop.

## 8. Decision: Spawn vs Do It Yourself

| Condition | Orchestrate | Do it yourself |
|-----------|-------------|----------------|
| Task is large / parallelizable | ✅ multiple agents | |
| Single small, well-scoped change | | ✅ main session |
| Needs a fresh-context review | ✅ subagent reviewer | |
| High-risk, irreversible (prod/migration) | ✅ + doubt cycle | with doubt |
| One-line mechanical change | | ✅ (no agent) |

## Quick Start

1. Decompose along capability + dependency graph; keep tasks Small/Medium.
2. Define shared contracts before parallelizing.
3. Dispatch with explicit contracts and acceptance criteria.
4. Run independent slices in parallel; serialize migrations/shared state.
5. Insert human checkpoints between phases.
6. For non-trivial decisions, run a fresh-context (adversarial) doubt cycle from the main session — offer cross-model.
7. Reconcile findings against the artifact; stop at 3 cycles or trivial findings.
8. Integrate, then verify the whole (tests/build) before declaring done.
