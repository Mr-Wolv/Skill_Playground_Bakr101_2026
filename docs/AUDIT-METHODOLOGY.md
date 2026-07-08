# Deep-Audit Methodology (Compositional / Pyramid)

A standing standard for "ocean-deep" auditing of this skill ecosystem.
Auditing is **compositional**: coherence is *re-proven at every level as you
ascend*, never asserted once at the top. Drift that only appears when two
previously-passing collections meet is caught at the seam.

## The ladder

```
L0  single file        (one SKILL.md)        — frontmatter, body, fenced blocks,
                                                   internal refs, embedded-script safety
L1  single skill folder (SKILL.md + scripts/references/templates/assets)
                                                   — internal integrity, script syntax,
                                                   destructive/exfil/secret scan
L2  thematic cluster   (e.g. script-bearing skills, "security") — overlap/trigger
                                                   collisions, duplicate capability
L3  category           (skills.json group)    — completeness, no orphans
L4  full skills/ (238)                        — manifest/catalog/domain parity,
                                                   duplicate capability
L5  repo collection    (skills/ + docs + scripts + catalogs) — global coherence
L6  repo <-> B         (source of truth)      — one-way mirror integrity
L7  B <-> C            (runtime)              — derived-copy parity
L8  four-store topology(B, repo, C, private)  — boundary / no-leakage
```

## Per-level protocol (unit -> e2e -> re-verify parent)

For each level N:

1. **UNIT** — audit every member of N in isolation, to the deepest grain
   practical for that member. One defect per member, with evidence.
2. **E2E** — audit the collection of N's members together: cross-member
   references resolve, no undeclared overlap, the level's invariant holds.
3. **RE-VERIFY PARENT** — re-run the already-passing parent level's checks
   against the new members before ascending. A green parent + green
   child must still be green when composed; if not, the seam is a defect.

Only ascend when the current level is fully closed (real gates, not
rubber-stamped). Do not interleave a higher level's collective gate before
the lower level has had its isolation pass.

## Severity model

- **CRITICAL** — breaks integrity: missing referenced file, script syntax
  error, malformed frontmatter, manifest/count mismatch. Fails the gate.
- **WARN** — needs human review but non-blocking: destructive/exfil/secret
  patterns in a clearly-scoped context, possible overlap, stale counts in
  prose. Reported, not failed.
- **INFO** — observation for the record.

## Tooling

`scripts/deep_audit.py` is the reusable harness. Subcommands:

- `python scripts/deep_audit.py skill <name>` — L0+L1 for one skill folder.
- `python scripts/deep_audit.py cluster [--scope <glob>]` — L0+L1 for every
  matching skill, then L2 cluster analysis, then L3/L4/L5 parent re-verify.
- `python scripts/deep_audit.py report` — summarize the last run's JSON.

Output is machine-readable (JSON sidecar) and human-readable (console).
Every CRITICAL is a real, evidence-backed finding — never synthesized.

## Scope of the first ocean-deep pass

L0->L2 over the **script-bearing cluster** (skills that ship an executable
`scripts/` dir): highest blast radius because embedded code can be
destructive, exfiltrate, or leak secrets. After it closes, ascend L3->L8
incrementally, re-verifying parents at each step.
