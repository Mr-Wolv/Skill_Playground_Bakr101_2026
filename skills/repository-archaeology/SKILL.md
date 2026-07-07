---
name: repository-archaeology
description: Reconstruct how a codebase evolved using git history, docs, naming drift, and structural clues. Use when understanding legacy areas, inferring intent, tracing architectural evolution, or identifying likely ownership and decision eras.
---

# Repository Archaeology

Study a repository like a historical artifact.

Use this skill when the problem is not just "what does this code do now?" but also:

- why is it shaped this way?
- what decisions or migrations led here?
- which parts are legacy scars versus active design?
- where did a subsystem likely come from?
- who or what context probably owns this area?

This skill helps reconstruct intent from evidence when explicit documentation is incomplete.

## When to use

- Understanding a legacy subsystem before changing it
- Tracing how an architectural pattern or module boundary emerged
- Investigating why a strange abstraction, naming scheme, or workflow exists
- Inferring likely ownership from history, change concentration, and terminology
- Preparing refactors, migrations, or deprecations in poorly documented areas
- Reconstructing decision eras across a long-lived repository

## When not to use

- General code reading when current structure is already clear
- Simple blame-style attribution of individuals
- Replacing explicit ADRs or design docs that already answer the question
- Auditing current doc/index consistency; use catalog consistency skills for that

## Evidence sources

Prefer primary repository evidence:

- git history
- file creation and rename history
- commit messages
- ADRs and design docs
- changelogs and migration docs
- naming conventions and terminology drift
- dependency structure
- deleted or superseded files
- test evolution
- directory layout changes

Treat any single clue as weak evidence. Confidence comes from convergence across multiple signals.

## Questions this skill answers

- What seems to be the original shape of this subsystem?
- What later layers or migrations were added on top?
- Which abstractions look load-bearing versus accidental?
- What terminology changed over time?
- Where are there signs of partial migrations or unfinished convergence?
- Which files, modules, or directories appear central to the subsystem's evolution?
- What documentation or decision records are missing but would have helped?

## Workflow

### 1. Define the archaeological question

State the question explicitly before digging.

Examples:

- How did this service boundary emerge?
- Why is there both `orders-v1` and `orders-core`?
- Is this adapter layer still part of the active design or a migration remnant?
- Which subsystem appears to own this business rule?

### 2. Identify the relevant artifact set

Bound the investigation to the smallest useful scope:

- specific directories
- a subsystem
- a module family
- a naming family
- a migration path
- an architecture era or major rewrite

Avoid trying to explain the whole repository if the question is local.

### 3. Gather historical evidence

Collect signals such as:

- oldest surviving files in the area
- major rename/move events
- recurring authors or commit clusters
- bursts of changes around migrations
- docs or ADRs that coincide with structural shifts
- old and new terms coexisting in the same area
- wrappers, shims, compatibility layers, or duplicated concepts

### 4. Reconstruct the timeline

Build a plain-language timeline of how the area likely evolved.

Typical pattern:

1. original structure
2. pressure or new requirement
3. migration or layering event
4. partial convergence or divergence
5. current residue

Keep the timeline evidence-based. Distinguish verified facts from inference.

### 5. Identify present-day implications

Translate history into actionable insight.

Examples:

- this abstraction still appears load-bearing
- this layer looks like migration residue and may be removable
- terminology drift is causing conceptual duplication
- ownership is diffuse, so changes here are risky
- the subsystem lacks a durable decision record and should gain one before refactoring

## Output format

```markdown
# Repository Archaeology

## Question
[What was investigated]

## Scope
[Files, directories, subsystem, or period]

## Evidence
- [fact or clue]
- [fact or clue]

## Reconstructed Timeline
1. [verified fact or labeled inference]
2. [verified fact or labeled inference]
3. [verified fact or labeled inference]

## Current Interpretation
- [what this likely means now]
- [what appears load-bearing vs residual]

## Risks for Future Changes
- [risk]

## Recommended Next Step
- [next action, doc, ADR, refactor precaution, or follow-up investigation]
```

## Guardrails

- separate **verified fact** from **inference**
- avoid pretending commit authorship equals ownership without corroboration
- avoid historical storytelling that is not grounded in repository evidence
- prefer a useful bounded explanation over a grand but vague history
- when explicit docs disagree with inferred history, surface the conflict rather than forcing a conclusion

## Anti-patterns

- using git blame as a substitute for understanding
- asserting intent from one commit message alone
- overfitting a narrative to sparse evidence
- confusing migration residue with active architecture without verification
- turning archaeology into an excuse to avoid reading the current code
