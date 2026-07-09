# Manifest enumeration gap — counts vs name lists

A manifest that stores a category count as an integer (e.g. `skills.json`:
`"community_skills": 176`) lets docs reference individual skills in that
category that can NEVER be reconciled by name, and a future writer script will
silently clobber any enumeration you add. Close it so the QA is name-level.

## Symptom
- `validate()` only checks `community_skills == len(filesystem - custom_set)` as
  an aggregate count.
- A doc references 11 community skills by name; the validator can't confirm them
  because the manifest has no name list.
- A sync/union writer recomputes `community_skills = total - custom` on import
  and would drop any `community_skill_names` list you add.

## Fix pattern (applied to a 238-skill catalog repo)
1. Derive the list from the filesystem minus the custom set:
   ```python
   fs = {e.name for e in skills_dir.iterdir() if e.is_dir()}
   custom = {n for arr in data["categories"].values() for n in arr}
   community = sorted(fs - custom)
   assert len(community) == data["community_skills"]
   assert not (custom & set(community))
   data["community_skill_names"] = community
   ```
   Regenerate programmatically (don't hand-type 176 names).
2. Gate it in the validator:
   - missing 'community_skill_names' list -> fail
   - len(list) != community_skills -> fail
   - list overlaps custom set -> fail
   - set(list) != (filesystem - custom) -> report the exact extra/missing names
3. Make the WRITER maintain it (the part everyone forgets): in the save block,
   rebuild from the live filesystem after the custom set changes:
   ```python
   custom_names = {n for arr in manifest["categories"].values() for n in arr}
   manifest["community_skill_names"] = sorted(skill_dirs(REPO) - custom_names)
   save_manifest(manifest)
   ```
   Without this, the next real `sync --apply` reverts the list to nothing and the
   gate goes red on the next commit.
4. Test it hermetically (mutate skills.json, restore in try/finally):
   - pop a name -> "community_skill_names missing"
   - append a nonexistent name -> "lists non-community"
   - append a custom name -> "overlaps custom set"
   - append two names -> count mismatch
   Red-proof each by neutering the isinstance guard and watching the test flip.

## Related latent bug caught the same pass
Frontmatter `name:` parsed with `^name:\s*(.+)$` keeps surrounding quotes, so
`name: "foo"` becomes `"foo"` in the skill set and mismatches bare-name diffs.
Strip at capture: `.strip().strip('"').strip("'").
