# Skill-Playground Documentation

> Central navigation for all project artifacts.
> Last updated: 2026-07-08

---

## 📋 Catalogs & References

| Document | Description |
|----------|-------------|
| [SDLC Phrase Cheatsheet](../SDLC-PHRASE-CHEATSHEET.md) | Say-this-get-that mapping — natural language → skill invocation |
| [Skill Catalog (SDLC Phases)](../SKILL-CATALOG.md) | 233 verified skills organized by SDLC phase |
| [Skill Catalog (Domains)](../SKILL-CATALOG-DOMAIN.md) | 52 custom skills organized by engineering domain |
| [Skills JSON Manifest](../skills.json) | Machine-readable index of all skills |
| [Merge Proposal](./merge-proposal.md) | Recommended keep/merge/rename plan for overlapping skill clusters |
| [Final Audit (2026-07-08)](./final-audit-2026-07-08.md) | Final architectural audit of the catalog, overlaps, and remaining cleanup candidates |
| [Publication Summary (2026-07-08)](./publication-summary-2026-07-08.md) | Publication-oriented summary of the catalog cleanup, additions, and validation model |
| [AGENTS Template](./AGENTS-template.md) | Reusable governance template for repositories that need source-of-truth, sync, and validation rules |
| [AGENTS Example (Filled)](./AGENTS-example-filled.md) | Concrete copy-paste example based on this repository's finalized governance model |
| [Global Agent Instructions Template](./GLOBAL-AGENT-INSTRUCTIONS.md) | Concise always-on instruction template for cross-project skill-aware agent behavior |
| [Global Agent Instructions (Minimal)](./GLOBAL-AGENT-INSTRUCTIONS-MINIMAL.md) | Lightweight always-on variant with minimal standing instruction weight |
| [Global Agent Instructions (Strict)](./GLOBAL-AGENT-INSTRUCTIONS-STRICT.md) | Higher-discipline variant for stronger anti-sprawl and workflow enforcement |
| [Global Agent Instructions (Personal Copy-Paste)](./GLOBAL-AGENT-INSTRUCTIONS-PERSONAL-COPYPASTE.md) | Copy-paste-ready block for personal/global instruction fields |
| [Skill Playground Root](../SKILL.md) | Entry-point skill — loaded when repo is installed via `npx skills add` |

## 🏗️ Project Structure

```
Skill-Playground/
├── skills/                       # 233 skills (each has SKILL.md)
├── SKILL.md                      # Root skill — repo entry point
├── SKILL-CATALOG.md              # SDLC-phase organized catalog
├── SKILL-CATALOG-DOMAIN.md       # Domain-organized catalog
├── SDLC-PHRASE-CHEATSHEET.md     # Natural language skill triggers
├── skills.json                   # Machine-readable manifest
├── README.md                     # Repo overview + install + contributing
├── .github/workflows/validate.yml  # CI: SKILL.md frontmatter + catalog sync
├── scripts/                      # Validation and mirror-maintenance helpers
│   ├── validate_catalog.py       # Structural catalog validator
│   ├── check_skill_mirror_parity.py # Recursive repo/global parity checker
│   └── sync_skills_to_global.py  # One-way sync from repo skills/ to global mirror
└── docs/                         # This directory — central navigation
    ├── index.md                   # Navigation hub
    ├── catalog-governance.md      # Source-of-truth and sync rules
    ├── merge-proposal.md          # Consolidation and boundary recommendations
    ├── final-audit-2026-07-08.md  # Current architectural audit snapshot
    ├── publication-summary-2026-07-08.md # Publication summary
    ├── AGENTS-template.md          # Reusable governance template
    ├── AGENTS-example-filled.md    # Concrete filled governance example
    ├── GLOBAL-AGENT-INSTRUCTIONS.md # Cross-project always-on instruction template
    ├── GLOBAL-AGENT-INSTRUCTIONS-MINIMAL.md # Lightweight always-on variant
    ├── GLOBAL-AGENT-INSTRUCTIONS-STRICT.md # Stronger discipline variant
    ├── GLOBAL-AGENT-INSTRUCTIONS-PERSONAL-COPYPASTE.md # Personal instruction block
```

## 🔗 Quick Links

- **[Browse the skill catalog](../SKILL-CATALOG.md)** — see all 233 verified skills by SDLC phase
- **[Install skills](../SKILL.md)** — `npx skills add <owner>/skill-playground`
- **[Contribute a new skill](../README.md#contributing)** — see contributing guidelines

## Custom Skills at a Glance

The repo includes 52 custom skills with expanded instruction bodies. Here are the categories:

| Category | Skills |
|----------|--------|
| 🧪 **Testing** (5) | unit-test-writer, integration-test-writer, test-fixture-generator, react-testing-library-patterns, java-testing-patterns |
| 🏗️ **Architecture** (7) | clean-architecture-principles, architecture-review, design-review, clean-code-principles, domain-driven-design-patterns, resilience-patterns, distributed-systems-patterns |
| ☸️ **DevOps** (6) | docker-configurator, env-configurator, project-initializer, flyway-migration-patterns, db-migration-writer, capacitor-mobile-patterns |
| 📖 **Documentation** (6) | readme-writer, api-documenter, code-documenter, code-commenter, document-reviewer, pr-writer |
| 🧹 **Code Quality** (5) | tech-debt-tracker, dead-code-remover, dependency-auditor, clean-code-principles, regex-builder |
| 🔍 **Analysis** (8) | failure-analysis, analytical-thinking-patterns, research, research-methodology, skills-browser, data-transform, catalog-consistency-auditor, repository-archaeology |
| 🧠 **Mindset** (4) | adjacent-disciplines, autonomous-learner, long-term-engineering-mindset, computer-science-foundations |
| 🔐 **Security** (2) | spring-security-patterns, dependency-auditor |
| 🗄️ **Data** (5) | spring-data-jpa-patterns, spring-boot-patterns, data-modeler, db-migration-writer, data-transform |
| 🔧 **Git & Workflow** (4) | commit-writer, branch-manager, api-tester, regex-builder |

Plus the remainder of the verified repository skills from community and workflow-oriented sources — see [SKILL-CATALOG.md](../SKILL-CATALOG.md) for the full listing.

---

See also [Catalog Governance and Sync Model](./catalog-governance.md) for maintenance rules, [Merge Proposal](./merge-proposal.md) for overlap-reduction planning, [Final Audit (2026-07-08)](./final-audit-2026-07-08.md) for the current architectural assessment, and [Publication Summary (2026-07-08)](./publication-summary-2026-07-08.md) for a publication-oriented overview.

Useful local maintenance scripts:

- `python scripts/validate_catalog.py`
- `python scripts/check_skill_mirror_parity.py`
- `python scripts/sync_skills_to_global.py`
- `python scripts/sync_and_validate.py`

*See [README.md](../README.md) for install instructions and contributing guidelines.*
