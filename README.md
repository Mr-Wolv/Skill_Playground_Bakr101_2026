# Skill Playground

> **A curated skill repository — 227 skills, bidirectionally synced.**
> Install via `npx skills add <owner>/skill-playground`

---

## Quick Start

```bash
# 1. Install all skills from this repo
npx skills add <owner>/skill-playground

# 2. List available skills
npx skills list

# 3. Pick a skill — say what you want in plain English
#    "Write unit tests for this function" → loads unit-test-writer
#    "Set up Docker for this app"        → loads docker-configurator
#    "Find tech debt in this codebase"   → loads tech-debt-tracker

# Or use the cheatsheet to find the right phrase:
open SDLC-PHRASE-CHEATSHEET.md
```

---

## What is this?

Skill Playground is a **skills repository** for the agent skills ecosystem. It currently contains **227 skills**, organized by both [SDLC phase](SKILL-CATALOG.md) and [engineering domain](SKILL-CATALOG-DOMAIN.md).

All skills are treated as a mirrored pair between this project's `skills/` directory and the global skill store at `~/.agents/skills/`.

---

## Install

```bash
# Install all skills from this repo
npx skills add <owner>/skill-playground

# Or install individual skills by name
npx skills add <owner>/skill-playground --skill unit-test-writer
npx skills add <owner>/skill-playground --skill docker-configurator

# List available skills
npx skills list
```

After installation, skills are available at `~/.agents/skills/<skill-name>/SKILL.md`.

---

## Skills at a Glance

| Category | Representative Skills |
|----------|------------------------|
| 🧪 **Testing** | `unit-test-writer`, `integration-test-writer`, `test-fixture-generator`, `react-testing-library-patterns`, `java-testing-patterns` |
| 🏗️ **Architecture & Design** | `clean-architecture-principles`, `architecture-review`, `design-review`, `domain-driven-design-patterns`, `distributed-systems-patterns` |
| ☸️ **DevOps & Delivery** | `docker-configurator`, `env-configurator`, `project-initializer`, `flyway-migration-patterns`, `db-migration-writer`, `shipping-and-launch` |
| 📖 **Documentation & Decisions** | `documentation-and-adrs`, `architecture-decision-records`, `readme-writer`, `api-documenter`, `document-reviewer`, `pr-writer` |
| 🧹 **Code Quality & Review** | `code-review`, `code-review-and-quality`, `code-review-excellence`, `tech-debt-tracker`, `dead-code-remover` |
| 🔍 **Repository Intelligence & Analysis** | `catalog-consistency-auditor`, `repository-archaeology`, `failure-analysis`, `research`, `research-methodology` |
| 🧠 **Reasoning & Mindset** | `analytical-thinking-patterns`, `adjacent-disciplines`, `autonomous-learner`, `long-term-engineering-mindset`, `computer-science-foundations` |
| 🔐 **Security** | `spring-security-patterns`, `dependency-auditor`, `security-and-hardening`, `owasp-security-check` |
| 🗄️ **Data & Persistence** | `spring-data-jpa-patterns`, `spring-boot-patterns`, `data-modeler`, `db-migration-writer`, `data-transform` |
| 🔧 **Git & Workflow** | `commit-writer`, `branch-manager`, `planning-and-task-breakdown`, `request-refactor-plan`, `api-tester` |

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
├── skills/                       # 227 skills (each has SKILL.md)
├── SKILL.md                      # Root skill — loaded when repo is added
├── SKILL-CATALOG.md              # Skills by SDLC phase (full listing)
├── SKILL-CATALOG-DOMAIN.md       # Custom skills by engineering domain
├── SDLC-PHRASE-CHEATSHEET.md     # Natural language → skill triggers
├── skills.json                   # Machine-readable manifest
├── docs/index.md                 # Navigation hub for all artifacts
└── .github/workflows/validate.yml  # CI: frontmatter + catalog validation
```

---

## Skill Lifecycle

```
Create → skills/<name>/SKILL.md
Catalog → SKILL-CATALOG.md + SKILL-CATALOG-DOMAIN.md
Trigger → SDLC-PHRASE-CHEATSHEET.md
Manifest → skills.json
Mirror → python scripts/sync_skills_to_global.py
Verify → python scripts/validate_catalog.py + python scripts/check_skill_mirror_parity.py
Shortcut → python scripts/sync_and_validate.py
Install → npx skills add <owner>/skill-playground
```

---

## License

This repository is licensed under the [MIT License](LICENSE).

It is intended to be reusable, modifiable, and shareable as a skill collection for the agent skills ecosystem. See individual skill sources for any third-party attribution requirements.

---

For catalog governance and sync rules, see [docs/catalog-governance.md](docs/catalog-governance.md).

If you want to apply a similar governance model in another repository, start from [docs/AGENTS-template.md](docs/AGENTS-template.md). If you want a near-copy of this repo's exact policy model, use [docs/AGENTS-example-filled.md](docs/AGENTS-example-filled.md).

*See [docs/index.md](docs/index.md) for the full artifact navigation.*
