---
name: skill-playground
description: Curated collection of 241 skills — testing, architecture, DevOps, documentation, code quality, and engineering mindset — mirrored with global skill store
---

# Skill Playground

A curated repository of **241 skills** for accelerating AI-assisted software development. These skills span testing patterns, architecture & design principles, DevOps automation, documentation generation, code quality tooling, engineering mindset practices, and much more.

All skills are treated as a mirrored pair between this project's `skills/` directory and your global `~/.agents/skills/` store.

## Quick Start

```bash
# Keep this agent's runtime in sync with the global source of truth
python scripts/sync_runtime_to_mirror.py --apply

# Export the global store into this repo (community copy; private skills stay out)
python scripts/sync_global_to_repo.py --apply

# Or run the full maintenance shortcut
python scripts/sync_and_validate.py
```

## Skill Categories

| Category | Representative Skills |
|----------|------------------------|
| 🧪 **Testing** | unit-test-writer, integration-test-writer, test-fixture-generator, react-testing-library-patterns, java-testing-patterns |
| 🏗️ **Architecture & Design** | clean-architecture-principles, architecture-review, design-review, domain-driven-design-patterns, backward-compatibility-and-change-management |
| ☸️ **Delivery & Operations** | shipping-and-launch, change-risk-assessment, operational-readiness-review, service-ownership-and-lifecycle-management, toil-analysis-and-automation |
| 📖 **Documentation & Decisions** | documentation-and-adrs, architecture-decision-records, readme-writer, api-documenter, document-reviewer, pr-writer |
| 🧹 **Code Quality & Review** | code-review, code-review-and-quality, code-review-excellence, tech-debt-tracker, dead-code-remover, codeowners-and-review-routing |
| 🔍 **Repository Intelligence & Analysis** | catalog-consistency-auditor, repository-archaeology, failure-analysis, research-note, research-methodology |
| 🧠 **Engineering Mindset** | long-term-engineering-mindset, adjacent-disciplines, autonomous-learner, computer-science-foundations |
| 🔐 **Security** | spring-security-patterns, dependency-auditor, security-and-hardening, owasp-security-check |
| 🗄️ **Data & Persistence** | spring-data-jpa-patterns, spring-boot-patterns, data-modeler, db-migration-writer, data-transform |
| 🔧 **Workflow Utilities** | commit-writer, branch-manager, planning-and-task-breakdown, request-refactor-plan, api-tester, skills-browser |

> **241 verified skills — mirrored with the global store**

See [SKILL-CATALOG.md](./SKILL-CATALOG.md) for the full SDLC-phase organization and [SKILL-CATALOG-DOMAIN.md](./SKILL-CATALOG-DOMAIN.md) for the domain-based organization.
