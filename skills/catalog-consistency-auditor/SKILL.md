---
name: catalog-consistency-auditor
description: Audit skill catalogs and repository documentation for drift against the actual skill set. Use when counts look stale, indexes disagree, mirrored stores may be out of sync, or catalog artifacts need one-pass reconciliation.
---

# Catalog Consistency Auditor

Audit a skill repository for structural drift between the actual skill folders and the documents that describe them.

This skill is for **catalog integrity**, not general code quality. Use it when the problem is that repository artifacts, counts, indexes, or mirrored skill stores may no longer agree.

## When to use

- A README, catalog, or manifest mentions counts that may be stale
- The workspace `skills/` directory and a mirrored global skill store may have diverged
- A skill was added, removed, renamed, merged, or split and the surrounding docs may be inconsistent
- You want a one-pass reconciliation of catalog artifacts after changing the skill set
- You suspect documentation drift across skill indexes, manifests, and navigation docs

## Scope discipline (HARD RULE)

When the user asks you to "fix everything" / "close all findings" / "make it converge",
treat **every** defect as in-scope — including ones that pre-existed this session or
live outside the files you originally touched. "It was already broken" is NOT an
exemption and must never be offered as a reason to leave a defect standing. If a
convergence/completeness audit surfaces a gap, fix the gap. Pre-existing state is just
more of the audit's scope, not a permission to stop. The deliverable is a repo where
the stated completion claim actually holds, not one where known issues were rationalized
away.

## Boundary

Use this skill for repository catalog coherence: source-of-truth discovery, count verification, mirror parity checks, and reconciliation of catalog-bearing documents and manifests.

Do not use this skill for historical reconstruction of why a repository evolved the way it did. For that, use `repository-archaeology`.

Do not use this skill for general codebase health, tech debt, dead code, or dependency audits. Use the repository-intelligence specialist skill that matches that problem.

## What this skill owns

This skill focuses on:

- structural source of truth discovery
- count verification
- mirror parity checks
- documentation drift detection
- index and manifest reconciliation
- explicit reporting of unresolved ambiguities

This skill does **not** decide whether a new capability should exist. Use capability-architecture or planning skills for that question.

## Workflow

### 1. Establish the source of truth

Treat the actual skill folders as the structural source of truth.

At minimum, verify:

- repository skill directory set
- mirrored/global skill directory set, if applicable

If documentation disagrees with the folder set, the folder set wins.

### 2. Compute the verified state

Record the facts before editing docs:

- total skill directory count
- repo-only entries
- global-only entries
- exact parity status
- any renamed/suspicious near-duplicates discovered during review

Do not copy prior totals from docs.

### 3. Audit catalog-bearing artifacts

Check all repository artifacts that can drift from the source of truth, including:

- `README.md`
- root `SKILL.md`
- `SKILL-CATALOG.md`
- `SKILL-CATALOG-DOMAIN.md`
- `SDLC-PHRASE-CHEATSHEET.md`
- `skills.json`
- `docs/index.md`
- governance or maintenance docs
- `AGENTS.md` if it references catalog behavior or sync rules

Look for:

- stale counts
- conflicting totals
- outdated category claims
- references to missing skills
- missing references to newly added skills
- inaccurate sync statements
- obsolete maintenance instructions

### 4. Reconcile in one pass

When you fix drift, update all affected artifacts in the same change.

Prefer:

- verified counts over inherited counts
- operational language over marketing language
- explicit uncertainty where classification is ambiguous
- narrow factual claims that are easy to keep true

If an exact breakdown cannot be verified confidently, avoid inventing one. State the verified fact and note what remains unclassified.

### 5. Report unresolved issues explicitly

If you encounter ambiguity, record it clearly instead of guessing. Examples:

- a skill appears workflow-oriented and category placement is unclear
- the repo and global stores differ and intentionality is unknown
- legacy docs use a classification scheme that no longer maps cleanly to the current catalog

### 6. Automate derived counts — never hand-edit the sweep (USER PREFERENCE)

Hard rule from the user: **"automate everything of a hardcoded kind; deep automation
for anything of such nuisance is needed so I'm not actively pained by it."** When a
catalog carries counts in many docs (README.md, SKILL.md, SKILL-CATALOG.md,
SKILL-CATALOG-DOMAIN.md, docs/index.md, docs/catalog-governance.md, skills.json),
hand-editing all of them on every skill add/remove is the brittle failure mode. The
resilient pattern is to **derive the counts from the filesystem and regenerate**:

- total = len([p for p in skills_dir.glob('*/') if (p/'SKILL.md').exists()])
- custom = union of all skills.json categories arrays
- community = total - custom (community_skill_names enumerates them exactly)

A small generator (e.g. scripts/refresh_derived_catalog.py with --check/--apply) rewrites
the manifests + prose in one idempotent pass. Wire it into the PRE-COMMIT HOOK so a
diverged count self-heals and stages before the gate — the commit can never be blocked
(or silently wrong) by a stale literal. Freeze-tests that assert counts must DERIVE
expected values from skills.json at runtime, never hardcode 240/241/64/65.

Exclude historical report files (VERSION-1.0-*.md, AUDIT-COMPLETENESS.md) from
regeneration — they record point-in-time numbers and must not be rewritten. Scripted
recipe + the exact file map: references/automate-derived-counts.md.

PITFALL — `sync_global_to_repo.py --force` is a SILENT NO-OP without `--apply`. The
apply block is nested inside `if args.apply`, so `--force` alone prints a plan and writes
nothing (you burn a run). Correct convergence invocation under merged (B==C) topology:
`python scripts/sync_global_to_repo.py --apply --force` (takes a timestamped backup at
`skills.backup-<ts>` first). It only overwrites SKILL DIRS whose content differs — root
docs (README.md/SKILL.md) are NOT touched, so count governance stays with
`refresh_derived_catalog.py`. Because the store IS the truth post-merge, `--apply --force`
is the SAFE way to converge a lagging export to the truth; do NOT hand-re-edit drifted
literals after a sync, re-run `refresh --apply`. The older "restore from git, the store
may be stale" warning was written pre-merge when B≠C — in merged topology the store cannot
be stale relative to itself.

## Convergence audit (the "many truths → one truth" pass)

When the task is not a one-off reconciliation but a *convergence audit* — declare a
catalog "complete", "coherent", or "Version 1.0" — produce a **report**, not just a
fix-list. The deliverable is a findings table where every finding carries
**impact / recommended action / priority / architectural justification**, plus a
go/no-go verdict on the completion claim. Framing: the goal is to find *inconsistencies,
ambiguity, duplication, drift, architectural debt, simplification opportunities* — not
to add capabilities.

Run the repo's own QC gate first and report its result as ground truth. A green
`gate.py` / `make verify` is strong evidence the *mechanical* foundation is converged
even when prose docs contradict each other. Convergence findings are almost always in
the *documents*, not the validator.

reusable techniques that caught real drift (cheap to re-run; see
`references/convergence-audit-recipe.md` for the scripted versions and
`references/merge-b-c-one-store.md` for the root-cause B<->C oscillation fix).
Recovery recipe when an in-place mutation test corrupts the working tree:
`references/test-suite-hygiene.md`.


1. **Source-of-truth contradiction check.** Grep every governance/doc for "source of
   truth" and confirm they agree on WHICH directory is authoritative. This session found
   `docs/catalog-governance.md` calling `skills/` the source of truth while
   `AGENTS.md`/`README.md`/`docs/index.md` called `~/.agents/skills` the source of truth
   — a direct "many similar truths" violation and the single highest-value finding. Check
   it first.
2. **Prose-count lint.** Docs hard-code totals that drift from the folder set (a catalog
   summary said "62 custom / 176 community = 238" while the validator confirmed 240/64/176).
   Cross-reference every literal count in markdown against `len(os.listdir('skills'))` and
   the json `total_skills`.
3. **Cross-artifact token cross-reference.** Parse every backtick-coded skill token out of
   each catalog/doc (skipping fenced code blocks), then diff against the folder set:
   orphans (token with no folder), missing (folder never mentioned), duplicates (token
   listed >1×). Diff `skills.json` `community_skill_names` vs folders to derive the implied
   custom set; compare to any `custom` markers in the catalogs.
4. **Placeholder-description finder.** Regex the catalog table for empty/truncated cells
   (`| > |`, `| >- |`, `| ~ |`) — unfinished entries in a "complete" deliverable.
5. **Coverage gaps.** List folders in NO catalog row and NO cheatsheet trigger phrase;
   prioritize surfacing high-value meta/orchestration skills that are undiscoverable.

### Operational pitfalls (learned the hard way)

- **B AND C ARE ONE STORE (post-2026-07 core nuke) — the old "write to B, never to C" rule is RETIRED.**
  The recurring B↔C oscillation was NEVER fixed by hand-promoting C→B; that was
  symptom-patching. The real root cause: B, C, AND the `~/.agents/skills` fallback
  resolved to **three distinct physical directories** (B=`~/.agents/skills` 240,
  C=`<LOCALAPPDATA>/hermes/skills` 263 nested, plus a separate real fallback
  `~/.agents/skills`). The runtime auto-wrote into C while B was a distinct place
  nobody wrote to; the one-directional additive sync (B→C, skipping differing
  content) meant C's versions could never reconcile back. The structural fix:
  junction `~/.agents/skills` → `<LOCALAPPDATA>/hermes/skills` (back up the 240
  first) AND make `global_skills_dir()`/`runtime_skills_dir()` `.resolve()` so B
  and C are string-identical. Now the runtime IS the source of truth — `skill_manage`
  AND file tools both land in the single store, so no second place can diverge.
  `assert_merged_topology()` in `scripts/skill_paths.py` fails the gate loudly if B
  and C ever resolve to different directories again. **Do NOT reintroduce
  "write to B not C" advice** — that rule was itself the oscillation source.
- **Detect multi-directory divergence before "fixing" anything.** When gate.py
  reports an L7 `runtime diff vs B`, do not immediately copy C→B. First run
  `python -c "import sys;sys.path.insert(0,'scripts');import skill_paths as s;print(s.global_skills_dir());print(s.runtime_skills_dir())"` and compare the RESOLVED paths. If they point at two different real dirs (or B falls back to a separate `~/.agents/skills`), the topology itself is split — the durable fix is the junction/`.resolve()` merge above, not a content copy. A content copy only treats the symptom; the next reload re-diverges.
- **L6 "in B but not in repo" WARNs are expected for private-by-default skills — keep the allowlist CI-stable.**
  The merged store exposes global-only skills the repo legitimately excludes
  (private-by-default union model). If the L6 check emits a WARN for every
  `extra_b` skill, the local finding set grows and a regenerated `warn_allowlist.json`
  becomes STALE on CI (where B is empty) → `TestWarnAllowlist` fails with
  "stale allowlist entries". Fix in `scripts/deep_audit.py`: L6 should WARN only for
  opted-in skills (`scripts/import.allow`); all other `extra_b` are expected (like
  L7's `extra_c`, already INFO). Then regenerate the allowlist with
  `python scripts/deep_audit.py allowlist --write` — it collapses to the
  repo-derived, CI-identical set (~42 entries, not 117). The WARN contract must be
  repo-derived so local and CI agree.
- **"Nuke it at the core" means remove the structural contradiction, not patch symptoms.**
  When the user insists on a root-cause fix ("whatever the cost"), prefer the
  one-store/one-truth collapse (junction + `.resolve()` + guard) over repeated
  C→B promotion. Promotion is a stopgap that the next reload undoes. The merged
  topology + `assert_merged_topology()` guard is the only durable end-state.
- **Pre-commit gate blocks foreground commits.** If the repo installs a pre-commit hook
  that runs the full `gate.py` (~3 min on a 240-skill tree), a foreground `git commit`
  in a 60s/180s terminal will time out and abort the commit — leaving changes staged but
  uncommitted. Run the commit in the **background** (notify_on_complete) and poll, or run
  the gate separately first. The gate failing is a real signal, not a timeout artifact.
- **A green gate ≠ ready to commit if the gate itself fails.** Read the gate tail:
  `0 CRITICAL` + `ALL GATES PASS` is the only success state. A single `[CRITICAL]` (even
  in a deep-audit L-level) blocks the commit.
- **Manifest tripwire re-pin is an intended change, not a bug.** If you add/rename/modify
  a tracked file (e.g. publish a stranded `references/*.md`), the manifest hash baseline
  (`scripts/BASELINE_MANIFEST.sha`) drifts and `TestManifestTripwire` fails. Re-pin with
  `UPDATE_BASELINE=1 .venv/Scripts/python -m pytest -q -p no:cacheprovider tests/test_deep_qc.py::TestManifestTripwire`,
  then confirm it passes WITHOUT the flag. The tripwire ALSO fires after an `--apply --force`
  convergence pull (any `skills/` content change drifts the hash). Only re-pin for intended changes.
- **L7 runtime↔global drift means the topology is split — merge, don't promote.**
  `gate.py` runs `deep_audit.py climb --strict` which checks the runtime store (C)
  against the source of truth (B). A `file-set-mismatch` / `content-mismatch` on a
  *shared* skill historically meant "runtime diverged from source; promote C→B".
  That promotion pattern is now OBSOLETE: B and C are intentionally the SAME
  physical directory (junction + `.resolve()`), so a genuine L7 mismatch means
  either (a) B and C resolved to different dirs — re-apply the junction/`.resolve()`
  merge — or (b) a real content fault in a shared skill, which the manifest
  tripwire catches. The 80+ `extra_in_C` skills are private/runtime-only and are
  INFO by design — leave them. Do NOT reintroduce the "copy C into B" dance; if
  B != C on path, fix the topology, not the bytes.
- **A count generator must CORRECT drift, not just confirm it.** A generator built
  on exact-match no-op pairs (`("241 skills","241 skills")` via `str.replace`) only
  rewrites a count that is ALREADY correct — it silently leaves a *drifted* literal
  (`"240 skills"`) untouched, so the pre-commit "self-heal" heals nothing and the
  commit is then blocked by the validator instead. Use REGEX substitution keyed on
  the phrase, not the number: `re.sub(r"(\d+) custom skills", f"{cu} custom skills", ...)`.
  Order specific phrases (`\d+ custom/verified/community skills`, the catalog title)
  BEFORE the generic bare `(\d+) skills`, so qualifiers are consumed by their own rule
  and the generic pass only touches remaining bare totals. Unit-test this directly
  (feed a doc with a WRONG count, assert it becomes the derived one) — the downstream
  validator catches drift opaquely and late; a generator unit test catches it at source.
- **A green count guard is NOT proof the guard covers every surface — blind spots pass silently.** A guard built on prose regexes over a *fixed file list* will report CONSISTENT while authoritative artifacts outside that list still contradict the folder set. This session: `refresh_derived_catalog.py --check` passed GREEN while `skills.json` free-text `description` ("240 verified skills") and `SKILL-CATALOG-DOMAIN.md` scope ("64 curated custom skills") + its "complete 240-skill listing" phrasing had all drifted — because the rewriter never touched the JSON description and the domain file's qualified wording ("N curated custom skills", "complete N-skill listing") fell outside the bare `(\d+) skills` rule. Fix: enumerate EVERY count-bearing surface and add a derived-correcting rule for each — JSON `description` (regex `\b\d+ verified skills\b`), the domain catalog's `(\d+) curated custom skills`, and `complete (\d+)-skill listing` (hyphenated, missed by the bare rule). Then prove the fix with a GUARD-LEVEL adversarial test (below). A green `refresh --check` only means "the surfaces I wired up agree" — it cannot assert coverage of a surface you forgot to wire.
- **The catalog Summary `**Total**` row + the catalog TITLE are easy to miss.** Two
  real bugs shipped hidden until a unit test: (1) the bold Summary row `| **Total** | **N** |`
  needs a regex that consumes the surrounding `**` (`\*{0,2}` on both sides of the digits),
  or it never updates; (2) the title `# SDLC Skills Catalog — N Skills` lived in
  SKILL-CATALOG.md, which the generator handled ONLY via the summary-table rewriter and
  EXCLUDED from the prose rewriter — so the title drifted forever. Run the prose rewriter
  on SKILL-CATALOG.md too (it's safe on the summary rows: no `digit␠skills` adjacency
  there). Make the title pattern dash-agnostic + case-insensitive (`.*?(\d+) Skills`,
  `re.IGNORECASE`) so an em-dash/en-dash or case mismatch can't silently skip it.
- **f-string regex quantifier footgun.** Inside `rf"..."` a `*` is the repetition
  operator, so `\*{0,2}` collapses to `\*(0, 2)` (a buggy pattern). Use a bracketed
  quantifier `[*]{0,2}` instead, or build the pattern from a plain string. Symptom: a
  regex that looks correct but matches nothing.
- **Verify against the real toolchain, hermetically.** This repo runs tests via
  `uv run --with pytest pytest` — but that form re-resolves the pytest wheel from
  the network on EVERY call and HANGS on flaky links. The durable fix: `uv sync --dev`
  once, then run via the synced interpreter with no uv resolution —
  `.venv/Scripts/python -m pytest -q -p no:cacheprovider` (Windows) — or
  `uv run --offline --no-sync pytest` when `.venv` is absent. A full gate on the
  240-skill tree takes ~3 min and the deep compositional suite ~4–5 min; that is
  NOT a hang — do not kill it at ~2 min. Background the commit and poll.
- **Reversibility over deletion when the user asserts file ownership.** If the user
  blocks a delete of a stray store file (e.g. a recipe/markdown in C that the repo
  canon lacks), do NOT force-remove it. Relocate instead: copy to a timestamped
  backup (`$TEMP/<name>.bak-<ts>`) AND move the live file out of the store to
  `$TEMP/<name>` so parity passes. Fully reversible, zero irreversible action, and
  it satisfies the "use a safety net" directive. Only delete when the user
  explicitly confirms.
- **Grep for references BEFORE deleting a "stale" artifact — it may be a skill dependency.** A report that looks like dead drift can be referenced from a skill's `references/`. One session found `VERSION-1.0-CONVERGENCE-REPORT.md` looked stale (its 240/64 counts were overtaken by growth) but `skills/catalog-consistency-auditor/references/automate-derived-counts.md` lists it as a frozen historical input — deleting it would break a skill. Correct move when an artifact is referenced: KEEP it and add a `> ⚠️ SUPERSEDED by <newer-artifact>` header pointing at the current file; do NOT delete. This is grep-driven, not assumption-driven, and complements the Reversibility-over-deletion rule above.
- **Run parity as a SEPARATE gate — count gates and `gate.py` are disjoint in coverage.** `refresh_derived_catalog.py --check` AND `gate.py` were both GREEN while `check_skill_mirror_parity.py` independently caught a `content-mismatch` (the export lagged the truth by 2 learned lines in one skill). None of the count/coherence gates checks repo↔store byte parity. After ANY convergence change run ALL FOUR independently and confirm each: `refresh_derived_catalog.py --check` (derived counts), `validate_catalog.py` (structural), `check_skill_mirror_parity.py` (repo↔store parity), `check_merged_topology.py` (B==C). Green on one is NOT green on all.
- **In-place mutation tests are a HAZARD, not a wart — eliminate them, don't recover.** `tests/test_validate_catalog.py` patched shared root files directly — `skills.json` via `json.dumps(data)` (NO `indent=2`, collapsing it to one line) and `data["custom_skills"] = 1` (writing a corrupt count) — to exercise drift checks. When one of these tests FAILED mid-run, its `try/finally` restore did NOT run, leaving the tree dirty; the NEXT run then failed on the *corruption*, not the code. This session 3 validate tests failed purely because a prior run left `skills.json` as a collapsed `custom_skills: 1`. User mandate: **"hazards > anything; be fool-proof; do not sleep on a hazard."** So the durable fix is structural, not a recovery recipe: **run the test against a throwaway COPY of the repo** (a `scratch` fixture clones the tree into `tmp_path`, excluding `.venv`/`.git`/`*.backup-*` so it stays small and avoids `OSError: [Errno 28] No space left on device`). All mutations target `scratch/...`; the committed tree is physically impossible to corrupt, and there is no shared-file `try/finally` to skip. This is now the shipped design — if you touch that suite again, KEEP the scratch model; do not reintroduce real-tree mutation. Recovery (only if you inherit the old design): `python scripts/refresh_derived_catalog.py --apply` rebuilds `skills.json`+prose from disk, then re-run on the healed tree. Full fix + proof recipe: `references/test-suite-hygiene.md`.
- **Reload itself is a safe no-op on merged topology — reload-regression checks watch the EXPORT, not the store.** `python scripts/sync_runtime_to_mirror.py --apply` prints `applied: false, "nothing to add"` and writes nothing when source==dest (B==C junction), so it cannot mutate the truth. Run it TWICE and assert `check_merged_topology.py` → `resolved-identical: True` each time (idempotency). The real regression surface a reload exercise exposes is a *lagging export* (the export had older learned lines than the truth) — which `check_skill_mirror_parity.py` catches independently. So a "reload to check regression" pass = assert reload no-ops + assert parity, not "does the runtime change."

## Verification discipline — taste, don't promise

A single green gate run is NOT proof a fix holds. Reject "it's fixed" claims that
rest on one passing run; demand empirical proof. Before declaring a
convergence/stores fix complete, stress-test it:

1. **Idempotency under reload.** Re-run the reload/re-sync mechanism
   (e.g. `python scripts/sync_runtime_to_mirror.py --apply`) at least twice;
   assert B==C each time. A fix that re-diverges on the next boot was not a fix.
1c. **Count-guard blind-spot test (after touching the regenerator).** The general
   adversarial step (2) below tests `gate.py`, but the *count guard* deserves its
   own injection because its blind spots pass as GREEN. Re-inject a stale literal into
   a surface the guard claims to cover — e.g. `sed -i 's/65 curated custom skills/64 curated custom skills/' SKILL-CATALOG-DOMAIN.md` — then run `python scripts/refresh_derived_catalog.py --check` and assert it exits NON-ZERO ("DIVERGENT"); restore the file and assert `--check` is GREEN (exit 0). If the injected drift is NOT caught, the guard has a coverage hole — add the missing rule (see the blind-spot pitfall above) until the guard fails closed. This is the only way to prove the guard actually watches the surfaces you think it watches.
2. **Adversarial injection.** Deliberately reintroduce the exact old failure mode
   (e.g. append a junk line to C's shared skill, or write a file B lacks) and
   confirm `gate.py` CATCHES it (non-zero exit + a `[CRITICAL]` line). This proves
   the safety net is live, not silent. A fix whose guard never fires on a real
   fault is worthless.
3. **Restore + confirm green.** Copy B back over the injected file, re-run the
   gate; assert `ALL GATES PASS, 0 CRITICAL`.

Only after all three pass is "no more drift / no more oscillation" *earned*, not
*promised*. Scripted recipe: `references/verify-fix-holds.md`.

## Hazard discipline — "hazards > anything"

The user's standing instruction for this class of work: **a hazard outweighs any
convenience or speedup; make the bad state structurally impossible rather than
recover from it; never sleep on a hazard.** Concretely:

- If a fix removes a failure mode only by adding cleanup/restore logic, it is NOT
  done. Prefer a design where the failure cannot occur (e.g. tests run on a throwaway
  copy instead of mutating shared files in place).
- When the user flags a hazard ("don't sleep on THAT", "fool-proof", "hazard > anything"),
  treat it as a P0: chase it to root cause and close it, even if other work is pending.
- A hazard that can corrupt the repo or the toolchain (in-place test mutation,
  disk-exhausting copies, irreversible deletes) is worse than a missing feature.
  Eliminate it; do not document-and-defer it.

## Output expectations

For a reconciliation pass, produce a concise summary with:

- verified total skill count
- mirror parity result
- artifacts updated
- remaining ambiguities, if any

For a convergence audit, produce the report described in the section above.

## Anti-patterns

- trusting stale document counts over actual directories
- updating one index while leaving adjacent indexes stale
- inventing precise category breakdowns without verification
- silently ignoring repo/global divergence
- treating mirrored stores as synced without checking
- declaring a catalog "complete" from a green gate alone — prose-doc contradictions are
  the convergence defects a passing validator does not see
