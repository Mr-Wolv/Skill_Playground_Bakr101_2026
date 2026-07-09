# Skill Playground — Documentation

> Navigation hub for the **Skill Playground** skill catalog: 240 verified skills (64 custom), mirrored with your global agent skill store.
> Last updated: 2026-07-09

---

## Start here

| Document | What it's for |
|----------|---------------|
| [README](../README.md) | What this repo is, how to sync it into your agent, and how to contribute a skill. **Read this first.** |
| [SKILL.md](../SKILL.md) | The root catalog overview and skill categories at a glance. |
| [Skill Catalog (SDLC Phases)](../SKILL-CATALOG.md) | All 240 skills organized by where they fit in the software development lifecycle. |
| [Skill Catalog (Domains)](../SKILL-CATALOG-DOMAIN.md) | The 64 custom skills organized by engineering domain. |
| [SDLC Phrase Cheatsheet](../SDLC-PHRASE-CHEATSHEET.md) | "Say this → get that" — natural-language phrases that map to specific skills. |

## How to use the skills

1. Sync the catalog into your agent's global skill store:
   ```bash
   python scripts/sync_global_to_repo.py       # export global -> this repo (community copy)
   ```
2. Invoke a skill by name or by natural language. For example:
   - *"Write unit tests for this function"* → loads `unit-test-writer`
   - *"Set up Docker for this app"* → loads `docker-configurator`
   - *"Find tech debt in this codebase"* → loads `tech-debt-tracker`
3. Browse [SKILL-CATALOG.md](../SKILL-CATALOG.md) or the [cheatsheet](../SDLC-PHRASE-CHEATSHEET.md) to discover more.

## Governance & reusable templates (for maintainers)

These artifacts define the catalog's source-of-truth, sync, and validation rules. They are useful if you want to apply the same governance model to another repository.

| Document | What it's for |
|----------|---------------|
| [Catalog Governance](./catalog-governance.md) | Source-of-truth and mirror-sync rules; how the repo stays consistent. |
| [AGENTS Template](./AGENTS-template.md) | Reusable governance template (source-of-truth, sync, validation) for any repo. |
| [AGENTS Example (Filled)](./AGENTS-example-filled.md) | A concrete, copy-paste example based on this repo's finalized model. |
| [Global Agent Instructions](./GLOBAL-AGENT-INSTRUCTIONS.md) | Concise always-on instruction block for skill-aware agent behavior. |
| [Minimal variant](./GLOBAL-AGENT-INSTRUCTIONS-MINIMAL.md) | Lightweight always-on variant with minimal standing instruction weight. |
| [Strict variant](./GLOBAL-AGENT-INSTRUCTIONS-STRICT.md) | Higher-discipline variant for stronger anti-sprawl and workflow enforcement. |
| [Personal copy-paste](./GLOBAL-AGENT-INSTRUCTIONS-PERSONAL-COPYPASTE.md) | Ready-to-paste block for personal/global instruction fields. |

## Maintenance commands

```bash
# Source of truth is the GLOBAL store (~/.agents/skills). Two downstream syncs:
python scripts/sync_runtime_to_mirror.py   # global -> my runtime (resolved via runtime_skills_dir: $HERMES_RUNTIME_SKILLS | $HERMES_HOME/skills | ~/.hermes/skills)
python scripts/sync_global_to_repo.py      # global -> this repo (community export)
python scripts/sync_and_validate.py        # both (--apply) + validate + parity
python scripts/validate_catalog.py         # structural catalog validation
python scripts/check_skill_mirror_parity.py# verify repo/global skill parity
# sync_skills_to_global.py (repo->global) is DEPRECATED: runs backwards, refuses
#   unless --i-understand-repo-is-downstream. sync_skills_union.py is the opt-in
#   publisher for global-only skills into the repo.
```

*See [README.md](../README.md) for the full operating model and contributing guidelines.*
