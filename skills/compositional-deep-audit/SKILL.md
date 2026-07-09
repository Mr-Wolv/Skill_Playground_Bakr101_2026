---
name: compositional-deep-audit
description: Ocean-deep auditing of a multi-artifact repo/skill-store by ascending a compositional pyramid (file -> folder -> cluster -> category -> full set -> collection -> store topology), re-verifying parents at each level. Use when auditing a skill library, catalog, or any system where drift only appears when two previously-passing collections meet.
---

# Compositional Deep-Audit

Audit coherence by **ascending a pyramid** and re-proving it at every level as
you go up. Never assert coherence once at the top — drift hides at the seams
between passing sub-collections.

## The ladder (each level = unit -> e2e -> re-verify parent)

```
L0 single file        (one SKILL.md)        — frontmatter, fenced blocks, refs, embedded-script safety
L1 single skill folder (SKILL.md plus a scripts/ subtree: references, templates, assets) — internal integrity, script syntax, destructive/exfil/secret scan
L2 thematic cluster   (e.g. script-bearing skills, "security") — overlap / trigger collisions, duplicate capability
L3 category           (skills.json group)    — completeness, no orphans / phantom members
L4 full set (238)                              — L0/L1 over EVERY member (unit) + L2 overlap (e2e)
L5 repo collection    (skills/ + docs + scripts + catalogs) — global coherence (canonical gates)
L6 repo <-> B         (source of truth)      — one-way mirror integrity
L7 B <-> C            (runtime / derived copy) — derived-copy parity
L8 four-store topology(B, repo, C, private)  — boundary / no-leakage / no machine paths
```

Per-level protocol:
1. **UNIT** — audit every member of the level in isolation, deepest grain practical. One defect per member, with evidence.
2. **E2E** — audit the collection together: cross-member references resolve, no undeclared overlap, the level invariant holds.
3. **RE-VERIFY PARENT** — re-run the already-passing parent's checks against the new members before ascending. Green parent + green child must stay green when composed; if not, the seam is a defect.

Only ascend when the current level is fully closed (real gates, not
rubber-stamped). Do NOT interleave a higher level's collective gate before the
lower level has had its isolation pass. (This ordering constraint was missed
once and had to be redone — isolation-first, then harmonic.)

## Severity model
- **CRITICAL** — breaks integrity: missing referenced file, script syntax error, malformed frontmatter, manifest/count mismatch, store parity diff. Fails the gate.
- **WARN** — needs human review but non-blocking: destructive/exfil/secret patterns in clearly-scoped instructional context, possible overlap. Reported, not failed.
- **INFO** — observation for the record.

## Gotchas (learned the hard way)
- A fenced-block parser that initializes `cur=[]` instead of `cur=None` will
  treat all prose *before the first ``` fence* as "block 0" and false-flag
  prose references. Start `cur=None`.
- Reference-existence checks must run ONLY inside fenced code blocks. Prose
  like "- add templates/checklists" or external pointers ("Allium
  references/...") are not dead links.
- Cross-skill links (`../other-skill/references/x.md`) and external paths
  must be skipped, not flagged.
- When comparing a runtime store to a source-of-truth store, skills present in
  the runtime but absent from source are EXPECTED additive drift (private
  skills) — never CRITICAL. Only a source skill missing from runtime, or a
  content mismatch on a shared skill, is a real defect.
- Containment/leak checks must skip when two logical stores resolve to the
  SAME physical dir on a given machine (common on Windows: runtime C == private
  path). Require DISTINCT dirs before flagging nesting.
- Privacy/leak scan: match the real resolved username and `C:\Users\<user>`,
  NOT a generic `[A-Za-z]:\` drive pattern — that false-positives on Python
  f-strings like `f"text:\n{var}"`.
- Shell `bash -n` subprocess often cannot resolve Windows/UNIX paths in an
  MSYS/CI spawn — don't make it a CRITICAL gate; scan script bodies for the
  patterns instead, and lint shells by hand.

## Working on a source-of-truth store (do no harm)
- B (source of truth) is authoritative; repo is a downstream export; runtime C
  is a derived copy. Fix in B, then re-export/re-derive down.
- ALWAYS take a timestamped backup of any live store (B, C) BEFORE writing.
- Be additive and non-destructive: never delete; overwrite only when
  re-deriving a copy from its source; never touch a store's private skills.

## Reference implementation
This repo's `scripts/deep_audit.py` is a working harness:
`categories` (L3), `all` (L4), `topology` (L6/L7/L8), `climb` (run all in
order, re-verifying L5 gates after each). Reuse it; the patterns above are
exactly what it encodes.

## Enumerate-and-read: keyword scans miss different wording
A narrow regex like `(?i)(to-?do|future pass|pending)` is NOT a real
audit. The user's standing bar: "act like a human and read every single
file." When asked for "no To-do / for the future / whatever there is," a
keyword sweep will MISS different wording ("candidate for future cleanup,"
"revisit later," "remaining consolidation candidates," "TBD," "planning
cluster watchlist," "when it becomes a bigger concern"). The correct pass:

1. **ENUMERATE** every file (skip `.git`, `.venv`, backups, binaries);
   build a manifest. Count text vs binary.
2. **UNIT** — verify each file standalone parses/compiles: `.py` via
   `ast.parse` (NOT `py_compile.compile(source=...)` — that kwarg is 3.13+
   only and false-fails on 3.10/3.11), `.yaml` via multi-doc
   `yaml.safe_load_all` (single-doc `safe_load` false-fails on `---`
   separators), `.json`/`.toml` parse. Assert 0 failures.
3. **E2E** — resolve EVERY cross-reference: markdown `[label](target)`
   links (relative to each file's dir), `SKILL.md` frontmatter
   `related_skills`/`required_commands` against the skill set / `PATH`.
   Assert 0 dangling / 0 missing.
4. **SEMANTIC OPEN-WORK SWEEP** — run a BROAD human-style lexicon
   (see `references/semantic-openwork-sweep.md` for the two-pass regexes),
   then **personally READ every ambiguous hit** to judge false-positive vs
   genuine. Do NOT auto-dismiss on a second keyword list — read the file.

**Scoping rule that prevents false mass-flagging:** when sweeping for
"open work," scope the lexicon to repo-level artifacts (`docs/`, root
`*.md`, `scripts/`) and EXCLUDE `skills/**` body content. Skill bodies
legitimately USE words like `backlog`, `roadmap`, `milestone`, `Next
Steps`, `Open Questions`, `Planned` (enum value), `DRAFT` (GraphQL
`PostStatus` enum), and template `# TODO: Customize` — those are the
skill's DOMAIN, not repo debt. Editing them corrupts the skills. The
ONLY genuine repo-level open-work hits are:
- explicit "future cleanup / for the future / candidate for future" wording
  in governance/proposal docs (fix: rewrite as a closed decision);
- `AGENTS.md`/`AGENTS-*.md` "revisit later" — this is the repo's OWN
  expansion-control policy (defer speculative skill creation until
  evidence), NOT open work; leave it.
Judge each hit; fix genuine, document the rest as intentional.

## Beyond structural: three QC dives + the manual coherence dive
A gate that can never fail is worthless. After the climb is green, harden:
0. **MANUAL COHERENCE DIVE** (gates miss prose artifacts). A green gate still
0. **MANUAL COHERENCE DIVE** (gates miss prose artifacts). A green gate still
   ships real defects in files the validator doesn't read. Before declaring a
   repo "strict", enumerate gate-blind artifacts (every doc `validate_catalog.py`
   does NOT key on — here 9 of 11 docs), human-read each, repo-wide grep for
   hardcoded absolute paths (`D:\...`, `C:\Users`) and stale "Last updated"
   dates, and confirm skills coverage is automated-exhaustive (not just sampled).
   Full technique + the real bugs it caught: `references/manual-coherence-dive.md`.
   This maintainer treats a stale date or a leaked absolute path as a defect, and
   expects the dive to FIX findings, not just report them.

1. **NEGATIVE / MUTATION** — inject a broken artifact and assert the gate
   FAILS. This is how you find factory bugs in your own checker. Here,
   mutation-testing `deep_audit.fenced_blocks()` exposed that it left `cur=None`
   on the opening fence, silently dropping every fenced block's body -> the
   harness was blind to fenced refs/dangerous patterns. Fix: open-fence starts
   `cur=[]`, close-fence flushes. Always re-run the whole suite after such a fix
   — the WARN/CRIT counts may jump (the true surface was previously masked).
2. **BEHAVIORAL EXECUTION** — don't just lint the tooling, RUN it. Invoke
   sync/validate/parity as real subprocesses against synthetic `tmp_path`
   trees and assert exact behavior (additive, non-overwriting, dry-run no-op).
   Sandbox-execute every "suspicious" embedded script (those tripping a
   destructive/exfil scan) with the dangerous binaries STUBBED, and assert NONE
   actually called a destructive/exfil op. Use `--import <name>` rather than
   writing `import.allow` so tests never touch a tracked repo file.
3. **CI TRIPWIRE + GRAPH** — pin a `dir_hash` of the artifact tree; fail on
   drift unless re-pinned (env `UPDATE_BASELINE=1`). Build the cross-reference
   graph and assert zero dead-ends + no cycles; exclude project-relative
   example paths (`../src/...`) — they are targets inside a user's repo, not
   catalog links.

All QC tests HERMETIC: synthetic `tmp_path`, sandboxed execution, no live
stores touched. Run `make verify` (full pytest) + `make qcaudit` (climb).

## Whole-catalog fuzz (prove redundancy can't drift)
The catalog is 4-way redundant (skills.json categories + community list +
counts, the on-disk skills/*/SKILL.md tree, the prose docs). To prove it
can't be silently drifted: materialise a FAITHFUL snapshot into tmp (copytree
of skills/, skills.json, root docs + the 2 docs/*.md validate() reads — never
the tracked tree), inject ONE drift per operator across every axis (json
drop/rename, wrong counts, ghosted/omitted/overlapping community names,
invalid JSON; disk orphan/deleted/corrupt-frontmatter/empty; doc dropped
custom-label row, wrong count snippet, missing doc). Assert for EVERY
mutation: (a) CRASH-SAFETY — validate() returns list[str], never raises; (b)
SOUNDNESS — every genuine drift is REPORTED (non-empty errors).
- This caught a REAL bug: a missing doc left `text=None` and CRASHED the
  gate instead of reporting. Fix: make the safe-read helper return ("", err)
  on missing files so the function never dereferences None. Always make
  missing-file/unreadable/corrupt-input helpers return a sentinel + error
  tuple, never raise, so the gate reports rather than explodes.
- Operator targeting matters: only mutate what the validator KEYED on
  (e.g. delete the whole custom-label TABLE ROW, not one of several backtick
  mentions; replace ALL "N skills" occurrences, not count=1). A "silent PASS"
  in soundness is usually a mis-targeted operator, not a validator hole —
  fix the operator before assuming the validator is weak.
- Make the snapshot SHALLOW (only files validate() reads) and cap trials
  (~40); full-repo copytree × hundreds of trials times out on MSYS. Run the
  fuzz alone with a long timeout.

## Mechanical enforcement (turn gates into tooling, not memory)
A gate you can forget is not a gate. After the climb is green:
- **WARN allowlist (drift-fail).** Record every reviewed WARN as a
  `(skill, category, regex-source)` triple in `scripts/warn_allowlist.json`.
  `climb --strict` fails on any WARN NOT in the allowlist (unreviewed risk)
  and on any allowlist entry with no matching finding (stale -> prune). The
  WARN tier becomes a hard 0/0 contract, not a soft advisory. Regenerate with
  `python scripts/deep_audit.py allowlist --write` after a human review.
- **Property-based fuzz (no external dep).** A deterministic generator applies
  N mutation operators to valid SKILL.md frontmatter; assert two invariants
  hold for EVERY input: (a) crash-safety — the checker never raises (no
  green-wash-by-explosion on malformed input); (b) soundness — a doc with no
  valid frontmatter is ALWAYS CRITICAL (the checker cannot be fooled into
  silent approval of trash). Iterate operators EXPLICITLY (not via RNG-per-seed)
  or you'll mis-map which op a seed hits and get flaky assertions.
- **Single gate + pre-commit hook.** `scripts/gate.py` runs pytest + validate
  + parity + `climb --strict` in order; CI calls it directly. Install
  `scripts/pre-commit.hook` (chmod +x) so every local commit is gated by the
  identical toolchain — you cannot bypass in a commit what CI blocks. Coherence
  is then enforced by tooling, not by re-verification.

## CI-safety: the public repo must be self-coherent (not depend on a local store)
A mirrored-skill repo whose source-of-truth store (`~/.agents/skills`, B) lives
only on the author's machine will run `gate.py` GREEN locally but RED in CI,
because CI has no B. The four concrete failure modes and the exact fixes are in
`references/ci-safe-coherence-gates.md` — read it before touching the gate or
the climb. Rules of thumb:
- Store-parity against B and the L6 topology are LOCAL-MACHINE concerns. Gate
  them behind a `_store_present()` check; **skip with a notice** when B is
  absent, never crash.
- The `username`-leak WARN is machine-specific: on the runner `USERNAME=runner`
  trips it. Gate the scan behind `LEAK_USER` (empty for CI/service accounts) so
  it only fires on the author's real machine. Keep the strict WARN allowlist
  exact by regenerating it locally.
- Normalize CRLF→LF in any `dir_hash` tripwire, and **skip the strict tripwire
  comparison in CI** (`CI`/`GITHUB_ACTIONS` env) — the pre-commit hook already
  enforces it locally. In CI it only re-validates committed content.
- Before pushing, PROVE the fix by emulating the runner:
  `HERMES_SKILLS_HOME=/nonexistent/ci-sim USERNAME=runner CI=1 uv run --with pytest python scripts/gate.py`
  then confirm the REAL run with `gh run list --workflow "Regression Suite" --limit 1`.

## Pitfalls (learned the hard way)
- `uv` is a STANDALONE binary, not a module: invoke `["uv","run",...]`, not
  `[sys.executable,"-m","uv",...]`. Bare `pytest`/`python -m pytest` can pick a
  DIFFERENT interpreter than `uv run --with pytest pytest` — make the gate use
  the identical `uv` invocation so local/CI behavior matches.
- When writing fixtures into the real `skills/` tree, `mkdir(parents=True)`
  before `write_text` or you get FileNotFoundError; always `rmtree` in finally.
- `_run`/mutation tests that write to a real dir must never commit the temp;
  clean up before asserting.
- MSYS `bash` path translation: invoke scripts by relative name with `cwd=tmp`,
  or copy the real script into the sandbox and run the copy.
