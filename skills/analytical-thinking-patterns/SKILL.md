---
name: analytical-thinking-patterns
description: First-principles reasoning, systems thinking, tradeoff analysis, decision frameworks
---

# Analytical Thinking Patterns

Structured approaches to analytical problem-solving for engineering decisions.

## When to use

- Facing a complex problem with many variables
- Evaluating tradeoffs between different solutions
- Designing systems where interactions matter
- Making high-impact technical decisions

## Instructions

1. **First-principles reasoning** — break the problem down to its fundamental truths. What are we sure about? Build up from there instead of reasoning by analogy
2. **Systems thinking** — map the components and their interactions. A change in one area may have ripple effects. Look for feedback loops, delays, and non-linear effects
3. **Tradeoff analysis** — for each option, list: pros, cons, risks, costs. Compare on the dimensions that matter (performance, maintainability, cost, time)
4. **Decision frameworks**:
   - Decision matrix: score options against weighted criteria
   - Pre-mortem: assume the choice failed — why?
   - Opportunity cost: what else could we do with this effort?

## Example: Tradeoff analysis

| Criteria | Option A: SQLite | Option B: Postgres |
|----------|-----------------|-------------------|
| Setup complexity | 1 (trivial) | 3 (server needed) |
| Concurrency | 2 (single-writer) | 5 (multi-writer) |
| Cost | 5 (free, no infra) | 3 (requires hosting) |
| Durability | 3 (file-based) | 5 (WAL, replication) |

## Anti-patterns

- Analysis paralysis (set a timebox)
- Confirmation bias (looking for evidence that supports your preferred solution)
- False dichotomy (there may be more than two options)
- Ignoring sunk cost (past decisions don't justify bad current choices)
