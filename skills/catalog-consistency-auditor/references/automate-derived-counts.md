# Automate Derived Catalog Counts

Companion recipe for SKILL.md §6 (Automate derived counts). Use this when a catalog
carries skill totals across many docs and you must eliminate the hand-edit sweep.

## The single source of truth

Counts are DERIVED, never stored:

- `total`     = `len([p.name for p in SKILLS_DIR.glob("*/") if (p/"SKILL.md").exists()])`
- `custom`    = `{s for arr in skills.json["categories"].values() for s in arr}`
- `community` = `set(total_skills) - custom`; `skills.json["community_skill_names"]`
               enumerates them exactly (no overlap, length == community_skills).

`skills.json` fields (`total_skills`, `custom_skills`, `community_skills`,
`community_skill_names`) are themselves derived and rewritten by the generator.

## Generator shape (scripts/refresh_derived_catalog.py)

```
--check   fail (non-zero, no writes) if any artifact diverges   # CI / hook safe
--apply   idempotent rewrite; only writes files that actually change
```

Rewrite targets (live docs only):
- `skills.json` — the four count fields above
- `SKILL-CATALOG.md` — Summary table `Community skills | Custom skills | **Total**`
- `README.md`, `SKILL.md`, `SKILL-CATALOG-DOMAIN.md`, `docs/index.md`,
  `docs/catalog-governance.md` — prose count snippets (`N skills`, `N custom skills`,
  `N verified skills`, `Repository/Global skill directories: **N**`, etc.)

Use EXACT `(old, new)` string pairs (plain `str.replace`, no regex) so the mapping is
auditable and there is no backslash/f-string hazard. Each pair is a no-op when the
artifact already carries the derived count, so re-running is idempotent.

## Pre-commit self-heal (the key resilience step)

In `.git/hooks/pre-commit` (or `scripts/pre-commit.hook`):

```
if ! python scripts/refresh_derived_catalog.py --check >/dev/null 2>&1; then
    python scripts/refresh_derived_catalog.py --apply
    git add skills.json SKILL-CATALOG.md README.md SKILL.md \
            SKILL-CATALOG-DOMAIN.md docs/index.md docs/catalog-governance.md
fi
exec python scripts/gate.py
```

A stale hardcoded count can never block or silently pass a commit — it regenerates
and stages before the gate.

## Freeze-tests must derive, not hardcode

In `tests/test_validate_catalog.py`, the count-drift tests read `skills.json` at runtime:

```python
sj = json.loads((repo / "skills.json").read_text())
fs_count, custom_count = sj["total_skills"], sj["custom_skills"]
# patch the displayed value to a WRONG one, assert validator reports the DERIVED expected
_patch(cat, f"| Custom skills | {custom_count} |", f"| Custom skills | {custom_count-2} |")
errs = vc.validate(repo)
assert any(f"Summary 'Custom skills'={custom_count-2} but expected {custom_count}" in e
            for e in errs)
```

Never assert against a literal `240`/`241`/`64`/`65` — those rot when the catalog grows.

## Excluded (do NOT regenerate)

Historical report files record point-in-time numbers and must stay frozen:
- `VERSION-1.0-CONVERGENCE-REPORT.md`
- `docs/AUDIT-COMPLETENESS.md`

## Pitfall: external `--force` sync can corrupt root docs

`sync_global_to_repo.py --force` copies root docs (README.md/SKILL.md) from the STORE
copy when they differ. The store copy can be stale (this session produced a `0 skills`
README via that path). The derive-and-regenerate generator reads ONLY `skills/` +
`skills.json`, so it cannot pull the bad store value — but if a `--force` sync already
wrote a wrong count, `git checkout -- <doc>` to restore, then re-run the generator.
Do NOT hand-edit the literal back; let the generator own it.
