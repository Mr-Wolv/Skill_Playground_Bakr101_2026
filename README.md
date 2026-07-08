# Skill Playground

[![Validate Catalog](https://github.com/Mr-Wolv/Skill_Playground_Bakr101_2026/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/Mr-Wolv/Skill_Playground_Bakr101_2026/actions/workflows/validate.yml)
[![Mirror Parity Guidance](https://github.com/Mr-Wolv/Skill_Playground_Bakr101_2026/actions/workflows/mirror-parity.yml/badge.svg?branch=main)](https://github.com/Mr-Wolv/Skill_Playground_Bakr101_2026/actions/workflows/mirror-parity.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **A curated skill repository — 238 skills, mirrored with the global skill store.**
> Current supported operating model: manage `skills/` in this repo and sync into `~/.agents/skills/`.

---

## Quick Start

```bash
# 1. Keep this agent's runtime store in sync with the global source of truth
python scripts/sync_runtime_to_mirror.py --apply

# 2. Export the global store into this repo (community copy; private skills stay out)
python scripts/sync_global_to_repo.py --apply

# 3. Validate catalogs and mirror parity
python scripts/sync_and_validate.py

# 4. Use the skills from your global store

#    "Set up Docker for this app"        → loads docker-configurator
#    "Find tech debt in this codebase"   → loads tech-debt-tracker

# Or use the cheatsheet to find the right phrase:
open SDLC-PHRASE-CHEATSHEET.md
```

---

## What is this?

Skill Playground is a **skills repository** for the agent skills ecosystem. It currently contains **238 skills**, organized by both [SDLC phase](SKILL-CATALOG.md) and [engineering domain](SKILL-CATALOG-DOMAIN.md).

All skills are treated as a mirrored pair between this project's `skills/` directory and the global skill store at `~/.agents/skills/`.

---

## Operating Model

The **global skill store** (`~/.agents/skills`) is the **source of truth**. It
is curated across all your agents. Everything else is a *derived export*:

- **My runtime** (`$HERMES_HOME/skills`, default `~/.hermes/skills`) — Hermes's live load of the global
  store, for this agent only. Derived from global. The actual path is resolved by `runtime_skills_dir()`
  in `scripts/skill_paths.py` via `$HERMES_RUNTIME_SKILLS` → `$HERMES_HOME/skills` → `~/.hermes/skills`,
  so a non-default `HERMES_HOME` (e.g. `<LOCALAPPDATA>/hermes`) is followed automatically.
- **This repo** (`D:\Skill-Playground`) — a **community/localized export** of
  the global store. Downstream; never authoritative.
- **Private store** (`<LOCALAPPDATA>/hermes/skills`) — skills this agent
  authors for itself; excluded from all sync.

Two downstream sync directions flow FROM global:

- **global → runtime** (`sync_runtime_to_mirror.py`) — keeps this agent's
  loaded skills in step with the global source. Additive and non-destructive:
  never deletes, never overwrites differing content, never touches the private
  store, re-runs a safety audit on every skill it adds. Dry-run by default;
  `--apply` to write (backs up first).
- **global → repo** (`sync_global_to_repo.py`) — the export to community.
  Additive: never removes repo-only skills. Private-by-default: global-only
  skills are NOT copied into the (public) repo unless opted in via
  `scripts/import.allow`, `--import <name>`, or `--import-all`. Dry-run by
  default; `--apply` to write (backs up first).

> The older `sync_skills_to_global.py` (repo → global) runs **backwards** under
> this model and will clobber the source. It now refuses to run unless you pass
> `--i-understand-repo-is-downstream`. Prefer the two downstream scripts above.

The global store location is resolved portably (no hardcoded username): it
reads `$HERMES_SKILLS_HOME`, else `~/.agents/skills`, else
`$XDG_DATA_HOME/hermes/skills`.

The supported workflow is:

```bash
# Keep this agent's runtime store in sync with global (additive, safe)
python scripts/sync_runtime_to_mirror.py --apply

# Export global into this repo (community copy; private skills stay out)
python scripts/sync_global_to_repo.py --apply

# Validate docs/manifests and verify full recursive parity
python scripts/sync_and_validate.py --apply
```

After sync, skills are available at `~/.agents/skills/<skill-name>/SKILL.md`.

> `custom` and `community` are source/classification labels inside this repository. They do not represent remote ownership, package identity, or namespace semantics.

---

## Skills at a Glance

| Category | Representative Skills |
|----------|------------------------|
| 🧪 **Testing** | `unit-test-writer`, `integration-test-writer`, `test-fixture-generator`, `react-testing-library-patterns`, `java-testing-patterns` |
| 🏗️ **Architecture & Design** | `clean-architecture-principles`, `architecture-review`, `design-review`, `domain-driven-design-patterns`, `distributed-systems-patterns`, `backward-compatibility-and-change-management` |
| ☸️ **Delivery & Operations** | `shipping-and-launch`, `change-risk-assessment`, `operational-readiness-review`, `service-ownership-and-lifecycle-management`, `toil-analysis-and-automation` |
| 📖 **Documentation & Decisions** | `documentation-and-adrs`, `architecture-decision-records`, `readme-writer`, `api-documenter`, `document-reviewer`, `pr-writer` |
| 🧹 **Code Quality & Review** | `code-review`, `code-review-and-quality`, `code-review-excellence`, `tech-debt-tracker`, `dead-code-remover`, `codeowners-and-review-routing` |
| 🔍 **Repository Intelligence & Analysis** | `catalog-consistency-auditor`, `repository-archaeology`, `failure-analysis`, `research-note`, `research-methodology` |
| 🧠 **Reasoning & Mindset** | `analytical-thinking-patterns`, `adjacent-disciplines`, `autonomous-learner`, `long-term-engineering-mindset`, `computer-science-foundations` |
| 🔐 **Security** | `spring-security-patterns`, `dependency-auditor`, `security-and-hardening`, `owasp-security-check` |
| 🗄️ **Data & Persistence** | `spring-data-jpa-patterns`, `spring-boot-patterns`, `data-modeler`, `db-migration-writer`, `data-transform` |
| 🔧 **Workflow Utilities** | `commit-writer`, `branch-manager`, `planning-and-task-breakdown`, `request-refactor-plan`, `api-tester`, `skills-browser` |

---

## Organization: Two Views

This repo organizes skills in two complementary ways — use whichever helps you find what you need:

### By SDLC Phase ([SKILL-CATALOG.md](SKILL-CATALOG.md))

Skills grouped by where they fit in the software development lifecycle — Architecture & Design, Implementation, Testing, Code Review, Documentation, Maintenance, etc.

### By Engineering Domain ([SKILL-CATALOG-DOMAIN.md](SKILL-CATALOG-DOMAIN.md))

Skills mapped across an **engineering domain framework** covering everything from Computer Science Foundations through AI Engineering and Long-Term Engineering Mindset. Each skill appears in the domain(s) where it's most relevant.

> The 28-domain framework includes: CS Foundations, Software Engineering, SDLC, Requirements, Architecture, System Design, Design Principles, Databases, APIs, Networking, Security, DevOps, Cloud, Testing, Debugging, Performance, Reliability, Repository Intelligence, Code Quality, Documentation, Research, PM, Product Engineering, Communication, Analytical Thinking, AI Engineering, Long-Term Mindset, and Adjacent Disciplines.

---

## Complete Catalog

See [SKILL-CATALOG.md](SKILL-CATALOG.md) for the full verified skill listing organized by SDLC phase.

---

## Contributing

New skills are welcome. To contribute:

### Skill Requirements

Each skill must follow the standard format:

```markdown
---
name: your-skill-name
description: One-line description of what the skill does
---

# Your Skill Name

Detailed instructions for the AI agent on how to execute this skill.

Include:
- Step-by-step instructions
- When to use this skill vs. others
- Common patterns and anti-patterns
- Examples and edge cases
```

### Submission Process

1. **Create the skill**: Add `skills/<your-skill-name>/SKILL.md` with valid frontmatter
2. **Update the catalogs**: Add your skill to both `SKILL-CATALOG.md` and `SKILL-CATALOG-DOMAIN.md` under the appropriate phases/domains
3. **Update the cheatsheet**: Add natural-language trigger phrases to `SDLC-PHRASE-CHEATSHEET.md`
4. **Update `skills.json`**: Add your skill to the appropriate categories in the manifest
5. **Sync and validate**: Run `python scripts/sync_and_validate.py`
6. **Open a PR**: Describe what your skill does and which phase/domain it belongs to

### Guidelines

- **Names**: Lowercase with hyphens (`my-skill-name`)
- **Descriptions**: Clear, actionable, < 200 chars
- **Body**: At least one paragraph explaining what the skill does, when to use it, and how it works
- **Scope**: Skills should be focused on a single capability (avoid kitchen-sink skills)
- **Originality**: Prefer skills that aren't already available from community sources

---

## Project Structure

```
├── skills/                       # 238 skills (each has SKILL.md)
├── SKILL.md                      # Root overview for the mirrored skill catalog
├── SKILL-CATALOG.md              # Skills by SDLC phase (full listing)
├── SKILL-CATALOG-DOMAIN.md       # Custom skills by engineering domain
├── SDLC-PHRASE-CHEATSHEET.md     # Natural language → skill triggers
├── skills.json                   # Machine-readable manifest
├── scripts/                      # Validation and mirror-maintenance helpers
│   ├── validate_catalog.py       # Structural catalog validator
│   ├── check_skill_mirror_parity.py # Recursive repo/global parity checker
│   ├── sync_global_to_repo.py   # Export global (source) -> repo (community copy)
│   ├── sync_runtime_to_mirror.py # global -> my runtime (resolved via runtime_skills_dir: $HERMES_RUNTIME_SKILLS | $HERMES_HOME/skills | ~/.hermes/skills)
│   └── sync_skills_union.py      # Opt-in publisher: global-only -> repo (privacy-gated)

└── .github/workflows/validate.yml  # CI: frontmatter + catalog validation
```

---

## Skill Lifecycle

```
Create → skills/<name>/SKILL.md
Catalog → SKILL-CATALOG.md + SKILL-CATALOG-DOMAIN.md
Trigger → SDLC-PHRASE-CHEATSHEET.md
Manifest → skills.json
Mirror → python scripts/sync_global_to_repo.py
Verify → python scripts/validate_catalog.py + python scripts/check_skill_mirror_parity.py
Tests → `uv run --with pytest pytest` (regression suite in tests/)
Shortcut → python scripts/sync_and_validate.py
Use → skills load from the global source of truth (`~/.agents/skills/`)
```


---

## License

This repository is licensed under the [MIT License](LICENSE).

It is intended to be reusable, modifiable, and shareable as a skill collection for the agent skills ecosystem. See individual skill sources for any third-party attribution requirements.

---

For catalog governance and sync rules, see [docs/catalog-governance.md](docs/catalog-governance.md). The catalog is now in a mature maintenance phase, so new skills are expected to clear a higher bar than improvements to existing ones.

If you want to apply a similar governance model in another repository, start from [docs/AGENTS-template.md](docs/AGENTS-template.md). If you want a near-copy of this repo's exact policy model, use [docs/AGENTS-example-filled.md](docs/AGENTS-example-filled.md). For a concise cross-project always-on behavior layer, use [docs/GLOBAL-AGENT-INSTRUCTIONS.md](docs/GLOBAL-AGENT-INSTRUCTIONS.md), or choose the [minimal](docs/GLOBAL-AGENT-INSTRUCTIONS-MINIMAL.md), [strict](docs/GLOBAL-AGENT-INSTRUCTIONS-STRICT.md), or [copy-paste](docs/GLOBAL-AGENT-INSTRUCTIONS-PERSONAL-COPYPASTE.md) variant.

*See [docs/index.md](docs/index.md) for the full artifact navigation.*
