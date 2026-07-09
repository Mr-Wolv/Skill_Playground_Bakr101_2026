---
name: pytest-regression-suite
description: Add a hermetic pytest regression suite to a repo that ships validation/audit/lint scripts but has no tests. Use when a side-effecting script is run by hand and you want it gated in CI with repeatable evidence (e.g. a catalog/manifest consistency checker, a parity auditor, a docs validator).
---

# pytest-regression-suite

Turn a repo's manual validation script into a gated pytest suite so "it passed"
is repeatable instead of a fresh ad-hoc check every turn.

## When to use
- A repo has `scripts/validate_*.py` / `check_*.py` / `audit_*.py` that exits
  non-zero on drift, but nothing runs it automatically and you keep
  re-verifying by hand (temp `hermes-verify-*.py` scripts, inline `python - <<'PY'`).
- You added a new consistency rule (e.g. "catalog row labels must match the
  manifest") and want it enforced, not just documented.

## Technique
1. Refactor the script into a callable that returns errors instead of printing
   and exiting at import time:
   `def validate(root: Path) -> list[str]:` — empty list == PASS.
   Keep the CLI: `if __name__ == "__main__": sys.exit(1 if validate(ROOT) else 0)`.
   A callable is testable; a script that runs checks at module top-level is not.
2. Derive EVERY path from the `root` argument (skills dir, doc files, manifest).
   Do NOT pin paths to a module-level `ROOT` constant and reuse it inside
   `validate()` — that lets the check pass only because the real root happens to
   equal it, and makes it untestable against a synthetic repo. This root-pinning
   defect is the #1 silent failure (a snippet check that reads `DOC_FILES["x"]`
   keyed to module `ROOT` will never catch a mutation the test feeds via `root`).
3. Write HERMETIC tests that mutate the REAL files, assert, then restore in
   `try/finally`:
   ```
   orig = path.read_bytes()
   try:
       path.write_text(path.read_text().replace(anchor, bad), encoding="utf-8")
       assert any("expected message" in e for e in validate(repo))
   finally:
       path.write_bytes(orig)   # git status proves the restore worked
   ```
   A crash mid-test leaves the file dirty — `git status` after the run is your
   integrity signal.
4. Prove the red paths are real: temporarily NEUTER the mechanism (e.g. set the
   computed set to `set()`) and confirm the matching tests flip to FAIL while the
   others stay green. Then restore. A suite that only ever goes green has not
   demonstrated it can fail.
5. Run with no install step (when pytest isn't in the base env):
   `uv run --with pytest pytest`. Add `pyproject.toml` with
   `[tool.pytest.ini_options] testpaths=["tests"]; pythonpath=["scripts"]` so the
   validator module is importable and `addopts = "-q"`.

## When the script is path-parameterized (sync/parity, not ROOT-derived)
Catalog validators take a `root` and read real files (mutate/restore pattern
above). But sync/parity scripts often expose a PURE function that takes two
`Path` trees as args (e.g. `plan(global_base, repo_base, ...)`,
`check_parity(repo_root, global_root)`). Test those with SYNTHETIC trees in
`tmp_path` — no real files touched, no `try/finally` restore needed:
```python
def _make_skill(base, name, content="body\n"):
    d = base / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(content, encoding="utf-8")
    return d

def test_global_only_blocked_unless_optin(tmp_path):
    _make_skill(tmp_path / "global", "secret")
    p = sync.plan(tmp_path / "global", tmp_path / "repo",
                  {"secret"}, set(), force=False, explicit_imports=[],
                  import_all=False, allowed=[])
    assert p["private_blocked"] == ["secret"]   # additive: never auto-published
```
If the pure function has defaults that reference a hardcoded module `ROOT`/
`GLOBAL`, extract the comparison logic into the parameterized function and have
`main()` call it — same refactor as step 1, but the unit is two paths, not one
`root`. Both roots must exist before calling (a non-existent dir raises
`FileNotFoundError` on `.iterdir()`), so `mkdir(exist_ok=True)` each root even
when only one side has skills.

## Pitfalls (all hit in real use)
- `str.replace(old, new, 0)` means "replace ZERO occurrences" in Python — `count`
  is a LIMIT, not a flag. To replace ALL copies, call `text.replace(old, new)`
  with no count, or special-case `count == 0`. A `_patch(..., count=0)` helper
  silently no-ops, so a red test that expected the snippet gone will falsely
  fail while the file was never actually mutated.
- Don't assert on the script's stdout text to decide pass/fail; assert on the
  returned error list / process exit code.
- Keep tests fast and side-effect-free outside the mutate/restore window; never
  commit a mutated file. Use `repo` fixture = real repo root, not a temp copy,
  so tests exercise the actual files.
- The validation gate may only check AGGREGATE counts, not per-row labels
  (e.g. a custom skill tagged `community`). Such drift slips past — add explicit
  set-equality checks (labeled set must equal canonical set, both directions).
- A test asserting a script's DOCUMENTED contract can surface DEAD CODE: write
  the test for the behavior the docstring/README promises, run it, and if it
  fails because the feature was never wired in, fix the wiring FIRST, then keep
  the test as its regression gate. Real example: a sync script documented
  "opt in via scripts/import.allow" but `plan()` never called `allowed_imports()`,
  so opted-in global-only skills stayed `private_blocked`. The test caught it;
  the fix was a one-line arg pass-through. Tests are a spec, not just a gate.
- Proof-of-load-bearing: when you fix such dead code, NEUTER the mechanism and
  confirm the new test flips to FAIL (e.g. drop the `allowed` arg from the
  explicit set in `plan()`, expect `test_optin_via_allow_set` to fail), then
  restore. This proves the fix — not coincidence — makes the test pass.
- Frontmatter `name:` parsing must STRIP surrounding quotes. A regex capturing
  `^name:\s*(.+)$` keeps the value verbatim, so `name: "foo"` enters the skill
  set as `"foo"` (WITH literal quotes) and mismatches every bare-name comparison
  downstream (doc-ref checks, community-set diffs). Fix at capture time:
  `name = name_match.group(1).strip().strip('"').strip("'")`. In one repo 3
  skills had quoted names and the whole community-set comparison was silently
  broken until the quotes were stripped. Scan all SKILL.md `name:` values for
  quotes whenever a name-set comparison behaves oddly.
- Manifest stores a COUNT but not a NAME LIST — the enumeration gap. A manifest
  like `skills.json` with `community_skills: 176` (int) lets docs reference
  individual community skills that can NEVER be reconciled by name, and a future
  writer (e.g. a sync script) will silently clobber any enumeration you add.
  Close it: derive the name list from the filesystem minus the custom set, store
  it as a new field (`community_skill_names`), gate it (length == the int,
  no overlap with custom, set-equals filesystem-minus-custom), and — critically —
  make the WRITER script rebuild that list from the filesystem on every save so
  a later real sync stays green instead of wiping it. See
  `references/manifest_enumeration.md`.
- Missing-skill-ref scans over a README false-positive on PROSE/FENCE code-spans
  (`uv`, `pytest`, `make`, `python`, `bash`, `name`, `description`...). A naive
  `re.findall(r"`([^`]+)`")` over the whole file catches multi-line fenced blocks
  AND inline commands. Restrict the README scan to table rows: build the text
  from lines `ln.strip().startswith("|")`, then `re.findall(r"`([a-z][a-z0-9_-]+)`")`.
  Category tables (`| 🧪 Testing | `skill-a`, `skill-b` |`) are the only place a
  README legitimately names skills; this excludes fences/prose while still
  catching a real missing-skill reference in a table cell.

## Collective integration QA before deep dives
When the task spans MANY files/scripts edited across a session, don't declare
done after per-file unit tests pass. Run the real INTEGRATION shortcut end-to-end
(e.g. `python scripts/sync_and_validate.py` — the script that calls every
validate/sync sub-script in order) and confirm it exits 0 / prints its
completion token. Then reconcile the gate's inputs against GROUND TRUTH computed
independently (not via the gate itself): count filesystem dirs, parse the
manifest, diff the per-row doc labels against the canonical set by hand. This
catches cross-cutting regressions unit tests miss — e.g. a refactored validator
whose CLI is still invoked by the shortcut, a manifest field that's an int where
the docs need a name list, or a privacy-control parser that's now load-bearing
but untested. A session that ends "all unit tests green" while the shortcut or
the ground-truth diff is red is NOT done. The user explicitly prefers this
collective cross-file check before going deeper into per-file detail.

## Wire into CI (or the suite gates nothing)
Creating the suite locally is only half the job. Real repos often ALREADY have
a CI workflow that runs the OLD ad-hoc script (e.g. `python scripts/validate_catalog.py`)
on push/PR — and that workflow will NOT know about your new `tests/`. If you stop
here, the suite still passes on your machine but is never enforced in PRs, and a
regression merged between sessions slips past. Add a workflow that runs the suite:

```yaml
# .github/workflows/tests.yml
name: Regression Suite
on: [push, pull_request]          # see gotcha below about `on`
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v3
      - name: Run pytest regression suite
        run: uv run --with pytest pytest
      - name: Validate catalog coherence
        run: python the repo scripts/ dir's validate_catalog.py
```
A local alias helps humans too: add a `Makefile` `verify` target
(`uv run --with pytest pytest`) and point the README at it. (`make` may be
absent in some shells — the README should document the direct `uv` command.)

Gotcha — validating the workflow YAML with PyYAML locally: `on:` parses as the
boolean key `True` under YAML 1.1, so `yaml.safe_load(open(".github/workflows/tests.yml"))`
yields keys `['name', True, 'jobs']`. Don't assert on the literal string `"on"`;
check `True in d` (or `str(k).lower() == "on"`). The file is still valid GH Actions.

See `references/example_ci_workflow.yml` for a copy-pasteable workflow + Makefile
for a copy-pasteable workflow + Makefile `verify` target.

## Two catalog gates that belong in validate() (catalog repos)
When the audited repo has an overview doc and a skill tree, add these two checks
to `validate()` so they can't regress — both surfaced only by a deep cross-file
scan, never by the unit tests alone:

- **SKILL.md representative-skills table.** The "Skill Categories" overview table
  lists skills in PLAIN-TEXT comma-separated cells (not backticks), so the
  backtick-scan that covers other docs misses them. Parse table rows: split on
  `|`, take the 2nd cell, `re.split(r",\s*", cell)`, keep tokens matching
  `^[a-z][a-z0-9_-]+$`, and fail if any is not in the on-disk set. One repo had
  51 representative names only reachable this way.
- **Orphan check.** Every skill *directory* must be named in the manifest
  (custom categories OR the community name list) OR referenced by backtick in a
  catalog/overview doc. Compute `mentioned = manifest_names ∪ all doc backtick
  refs`; fail for any `skill in fs_skills if skill not in mentioned`. Catches a
  skill on disk that is silently documented nowhere. Have `validate()` re-read
  the manifest for the name set itself (don't depend on a variable the caller
  computes later — that's an ordering bug that raises NameError).

Runnable independent probe: `scripts/catalog_coherence_audit.py` (exit 0 = OK).
It recomputes all of the above WITHOUT calling the gate, so it catches a gate
that itself drifted. Run it for the "QA senior deep scan" pass after unit tests
go green.

## Verification
`uv run --with pytest pytest` -> all green; then re-run after a real injected
regression to confirm at least one test fails. See `references/example_validate_suite.md`
for a copy-pasteable template (validate() + conftest + hermetic test + pyproject)
and `references/example_sync_parity_tests.md` for the synthetic-tree (tmp_path)
pattern for path-parameterized sync/parity scripts. Also
`references/example_ci_workflow.yml` for the CI workflow + Makefile `verify` target
that gates the suite on every push/PR (the step most repos forget). Also
`references/manifest_enumeration.md` for closing the counts-vs-name-list gap
(derive list from filesystem, gate it, make the writer maintain it) plus the
frontmatter `name:` quote-strip gotcha.
