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

## Harness commands (full ladder)

- `python scripts/deep_audit.py categories` — **L3**: every `skills.json`
  category member exists on disk; no phantom members.
- `python scripts/deep_audit.py all` — **L4**: L0/L1 over **all 238**
  skills (unit) + L2 overlap (e2e) + parent re-verify.
- `python scripts/deep_audit.py topology` — **L6/L7/L8**: repo<->B mirror
  parity, B<->C derived-copy parity, four-store boundary + privacy-leak scan.
- `python scripts/deep_audit.py climb` — run L3, L4, L6/L7/L8 in order,
  re-running the L5 canonical gates (`validate_catalog.py`,
  `check_skill_mirror_parity.py`) after each level.

## Last full pass (2026-07-09)

`python scripts/deep_audit.py climb` -> **0 CRITICAL** across L3/L4/L6/L7/L8.

Genuine defects found and remediated this pass:
- **L4 (real, in source-of-truth B):** `sast-configuration` referenced
  `./scripts/run-sast.sh` and `references/semgrep-rules.md` that did not
  exist. Created both files (additive, non-destructive wrapper + rule
  examples). Re-exported B->repo and re-derived C from B.
- **L7 (real, runtime C stale vs B):** 3 shared skills
  (`capability-router`, `gap-analysis`, `research-methodology`) held old
  copies in C; `catalog-consistency-auditor` in C had 3 leftover old-layout
  files absent from B. Re-derived C from B (additive; C's 22 private skills
  left untouched), backing up B and C first.

Residual WARNs (5 on the full 238) are all benign pattern hits in
instructional text (e.g. `token=` in VAULT_TOKEN examples, `base64` in
crypto how-tos, `rm -rf` in documented "nuclear reset" steps) — not
violations. They are reported, not failed.

Canonical gates at pass: `validate_catalog.py` consistent,
`check_skill_mirror_parity.py` FULL_MIRROR_PARITY_CONFIRMED, `pytest` 31
passed.

## QC hardening — three dives beyond structural green-washing

After the first climb, the audit was extended from *structural* to *behavioral*
QC so no gate is a rubber stamp. See `tests/test_deep_qc.py`.

- **Dive 1 (negative / mutation):** prove the gates have teeth. Each test
  injects a broken artifact (dead fenced ref, missing frontmatter, python
  syntax error, parity file-set/content mismatch) and asserts the relevant
  gate FAILS. Running these surfaced a **real factory bug**: `deep_audit.
  fenced_blocks()` left `cur=None` on the opening fence, so every fenced
  block's body was silently dropped — the harness was blind to fenced-block
  references and dangerous patterns. Fixed; the climb WARN count is now the
  true surface (was under-reported).
- **Dive 2 (behavioral execution):** run the safety-critical tooling as a real
  subprocess against synthetic trees and assert exact behavior — sync is
  additive, non-overwriting by default, never deletes repo-extra, dry-run is a
  no-op; validate passes on a faithful repo and fails on a ghost reference.
  Also sandbox-execute every *suspicious* embedded script (those that trip the
  destructive/exfil scan) with the dangerous binaries stubbed, and assert NONE
  invoked a destructive/exfil call. One vetted self-authored script
  (`sast-configuration/scripts/run-sast.sh`) is executed end-to-end and
  asserted to print its documented header.
- **Dive 3 (CI tripwire + cross-ref graph):** pin a stable `dir_hash` of
  `skills/` (`scripts/BASELINE_MANIFEST.sha`); any drift fails the run until
  re-pinned with `UPDATE_BASELINE=1` (or `make qcaudit-baseline`). Build the
  global reference graph and assert zero dead-ends and no cross-skill cycles;
  project-relative example paths (`../src/...`) are correctly excluded.

All QC tests are hermetic (synthetic `tmp_path`, sandboxed execution, no live
stores touched). Run with `uv run --with pytest pytest`. CI also runs
`deep_audit.py climb`, `validate_catalog.py`, and `check_skill_mirror_parity.py`.

## Mechanical enforcement — making coherence PERSISTENT

Manual re-verification is not enough; a gate you can forget is not a gate.
Two layers make the above automatic:

- **WARN allowlist (drift-fail):** `scripts/warn_allowlist.json` records every
  reviewed WARN as a `(skill, category, regex-source)` triple. `climb --strict`
  fails on any WARN NOT in the allowlist (an unreviewed risk) AND on any
  allowlist entry with no matching finding (stale -> prune). Regenerate with
  `python scripts/deep_audit.py allowlist --write` after a human review. This
  turns the WARN tier into a hard 0/0 contract, not a soft advisory.
- **Single gate + pre-commit hook:** `scripts/gate.py` runs pytest,
  `validate_catalog.py`, `check_skill_mirror_parity.py`, and `climb --strict`
  in order; CI invokes it directly. `make install-hook` installs
  `scripts/pre-commit.hook` so EVERY local commit is gated by the identical
  toolchain — you cannot bypass in a commit what CI would block. Coherence,
  persistence, and completeness are enforced by the tooling, not by memory.

Run `make gate` to self-check before pushing; `make install-hook` to make it
unavoidable.
