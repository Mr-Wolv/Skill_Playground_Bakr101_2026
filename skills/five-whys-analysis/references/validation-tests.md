# Validating Root-Cause Analysis

Companion to `HOW_TO_USE.md`. A five-whys answer is only useful if the stated
root cause is *true*. This document gives concrete tests to verify a root
cause before you act on it.

## The core test: can you make it fail and fix it?

A genuine root cause passes three checks. If any fails, you stopped too early.

1. **Reversibility** — doing the opposite of the proposed cause changes the
   outcome. "We didn't validate input" is reversible: add validation, bug
   disappears.
2. **Specificity** — it names a concrete mechanism, not a vague label
   ("communication breakdown", "lack of process"). A real cause says *what
   specifically broke*.
3. **Evidence** — the cause is backed by the actual artifact (the commit, the
   log line, the schema), not by memory or assumption.

## Test templates

For each final "why", fill in:

```
ROOT CAUSE: <one sentence, mechanism-level>
EVIDENCE:   <file:line / log / metric that proves it>
COUNTERFACTUAL: "If <X> had been true, the failure would not have happened
                 because <reason>."
VERIFICATION: "We proved it by <change we made / experiment we ran>."
```

If you cannot write the COUNTERFACTUAL, you have not found the root cause.

## Common false roots (and what they hide)

| Stated cause | Usually hides |
|--------------|---------------|
| "human error" | a missing guardrail / unclear spec |
| "not enough testing" | unknown failure mode, no oracle |
| "bad communication" | ambiguous ownership or missing handoff artifact |
| "tight deadline" | risk not surfaced early enough |
| "third-party bug" | missing isolation / fallback on our side |

When you catch one of these, ask "why was that allowed to matter?" once more.

## Verification experiment

Prefer an experiment over an argument:

- **Injection**: reproduce the failure by forcing the suspected condition.
- **Removal**: apply the proposed fix in a branch and confirm the failure mode
  no longer triggers (add a regression test that asserts it).
- **Blast-radius**: confirm the fix does not just move the failure elsewhere.

## Scoring against the skill rubric

Map the result onto the quality dimensions in `HOW_TO_USE.md`:

- **Causal depth** — did you reach a mechanism, not a symptom?
- **Evidence quality** — is the proof the artifact, not opinion?
- **Actionability** — does the fix follow directly from the cause?

A root cause that scores low on any axis is not done. Re-run the chain.
