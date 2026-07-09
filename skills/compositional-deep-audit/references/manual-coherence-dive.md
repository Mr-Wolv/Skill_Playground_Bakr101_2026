# Manual Coherence Dive — what automated gates do NOT cover

The climb / `gate.py` / `validate_catalog.py` prove *machine-checkable* coherence.
They do NOT read every artifact. A green gate can still ship real defects that
only a human-read + repo-wide grep catches. This is the layer the maintainer
asked for explicitly ("have you dived the docs? the skills?") and that found
shippable bugs a passing gate missed.

## When to run it
- After any audit/climb is green, as the final "are we *strict*?" pass.
- Whenever the user asks "did you dive X?" / "is everything really good and strict?"
- Before declaring a repo coherent to a human.

## Steps (do all; the gate already did the rest)

1. **Enumerate gate-blind artifacts.** `validate_catalog.py` reads only a
   handful of files (root catalogs + `docs/index.md` + `docs/catalog-governance.md`).
   Every OTHER doc in `docs/` (here 9 of 11) is gate-UNVALIDATED. List them:
   `ls -1 docs/` and `search_files(target='files', path='docs')`. Same for any
   root `.md` the validator doesn't key on.

2. **HUMAN-READ every gate-blind artifact.** Do not assert "it's fine" from the
   filename. Read the full file. Look for:
   - contradicted claims (says "9 scripts" but there are 15;
     says "single gate is `sync_and_validate.py`" but it's `gate.py`);
   - descriptions of temp/phantom files that no longer exist
     (e.g. `_audit_*` helpers listed as "to be removed" that were already gone);
   - count/category claims that drifted from `skills.json`.

3. **Repo-wide absolute-path / machine-username leak scan.** The privacy WARN in
   `deep_audit` only fires on the *resolved* username and `C:\Users\<user>`; it
   MISSES a hardcoded `D:\Skill-Playground` absolute path written by a human in
   prose. Grep the whole tree (skip `.venv`, `.git`):
   ```
   grep -rInE "[A-Za-z]:\\" --include="*.md" . --exclude-dir=.venv --exclude-dir=.git
   ```
   Then confirm no real username / `C:\Users` in TRACKED files:
   ```
   git grep -n "GIGABYTE"   # replace with the real resolved username
   git grep -n "C:\\Users"
   ```
   Fix any hit with a portable form (`<this-repo>`, `~/.agents/skills`). Note:
   the *live* root `AGENTS.md` and root catalogs were already clean here — the
   leaks were in an example copy (`docs/AGENTS-example-filled.md`), a governance
   doc, and `README.md`. Example/illustrative docs still leak; fix them too.

4. **Staleness scan on "last updated" / date stamps.** The maintainer treats a
   stale date as a real defect. Find them:
   ```
   grep -rIn "Last updated" docs/ README.md SKILL.md SKILL-CATALOG*.md
   grep -rIn "2026-07-08" docs/ README.md SKILL-CATALOG*.md   # yesterday's anchor
   ```
   Bump any that are != today (here 5 files said 2026-07-08, bumped to 2026-07-09).
   A doc whose content describes obsolete tooling is ALSO stale even without a
   date line — fix the content, not just the stamp.

5. **Confirm skills coverage is exhaustive, not sampled.** The user asks "did you
   dive the skills?" Distinguish:
   - *Automated coverage*: `deep_audit.run_all()` audits ALL N skills (print
     "auditing N skills (all-238)"). 0 CRITICAL, WARNs are known-benign example
     patterns (token/base64 in security skills) — not real secrets.
   - *Human line-by-line*: NOT done. State this limit honestly (it's a documented
     future pass). Do not claim semantic quality of every body — claim structural
     / coherence / privacy only.
   Run the audit and eyeball the per-skill WARN list to confirm they're all
   instruction-context patterns, not real credentials.

6. **Re-verify after fixes**: `validate_catalog.py` still passes, fast pytest
   subset green, and the absolute-path + username greps now return CLEAN.

## What this dive found (concrete example)
On a fully green gate, the manual dive surfaced and fixed:
- 3 hardcoded `D:\Skill-Playground` absolute paths (privacy/portability leak).
- 5 docs with a stale "Last updated: 2026-07-08" date.
- `docs/AUDIT-COMPLETENESS.md` §8 describing 9 scripts + 3 phantom `_audit_*`
  temp helpers and naming the wrong gate script — corrected to the real 15
  scripts and `gate.py`.
All committed; gate re-ran green via pre-commit hook.

## Embedding the maintainer's standing directive
This maintainer's operating rule (stated repeatedly): do NOT rubber-stamp;
verify independently; ACTIVELY loop and dig until you can't anymore; when you
find gaps, FIX them and record the finding in the docs, then verify. A "pass"
from existing tooling is a starting point for the manual dive, not the finish.
