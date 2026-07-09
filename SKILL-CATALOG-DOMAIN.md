# Domain Engineering Catalog — Custom Skills

> **64 custom skills organized by engineering domain**
> 📚 [Documentation Index](docs/index.md) | [SDLC Catalog](SKILL-CATALOG.md) (full 240-skill listing) | [Cheatsheet](SDLC-PHRASE-CHEATSHEET.md) | [Repo Root](SKILL.md)

> This catalog lists the **64 custom skills** organized by engineering domain.
> For the complete 240-skill listing, see [SKILL-CATALOG.md](SKILL-CATALOG.md).

> **Scope:** this catalog covers the 64 curated custom skills only. The 176 community
> skills are listed in [SKILL-CATALOG.md](SKILL-CATALOG.md) (SDLC view) and `skills.json`;
> their absence here is intentional, not a gap.

---

## Domain 1: Computer Science Foundations
*Algorithms, data structures, complexity, OS, memory, concurrency*

| Skill | What it does |
|-------|-------------|
| `computer-science-foundations` | Algorithms, data structures, complexity, OS, memory, compilers, concurrency |

## Domain 2: Software Engineering
*Craftsmanship, construction, maintenance, quality, tech debt, ethics*

| Skill | What it does |
|-------|-------------|
| `clean-code-principles` | Teach Clean Code — naming, functions, DRY, KISS, SOLID, smells |
| `clean-architecture-principles` | Teach Clean Architecture layers, dependency rule |
| `tech-debt-tracker` | Scan for TODOs, complexity, code smells |
| `dead-code-remover` | Find and remove unused exports, files, deps |
| `pr-writer` | Write structured PR descriptions from git diff |
| `codeowners-and-review-routing` | Define repository ownership boundaries, CODEOWNERS rules, and review routing |

## Domain 3: Software Development Lifecycle
*Every SDLC phase — conception through retirement*

| Phase | Skills |
|-------|--------|
| 🏗️ Architecture | `clean-architecture-principles`, `architecture-review`, `design-review`, `clean-code-principles`, `domain-driven-design-patterns`, `distributed-systems-patterns`, `resilience-patterns`, `backward-compatibility-and-change-management` |
| 💻 Implementation | `project-initializer`, `env-configurator`, `docker-configurator`, `db-migration-writer`, `data-modeler`, `spring-boot-patterns`, `spring-data-jpa-patterns`, `spring-security-patterns`, `flyway-migration-patterns`, `capacitor-mobile-patterns` |
| 🧪 Testing | `unit-test-writer`, `integration-test-writer`, `test-fixture-generator`, `java-testing-patterns`, `react-testing-library-patterns` |
| ✅ Code Review | `pr-writer`, `clean-code-principles`, `document-reviewer`, `codeowners-and-review-routing` |
| 🔒 Security | `spring-security-patterns`, `dependency-auditor` |
| 📖 Documentation | `readme-writer`, `api-documenter`, `code-documenter`, `code-commenter`, `document-reviewer`, `documentation-and-adrs`, `architecture-decision-records` |
| 🔧 Maintenance | `tech-debt-tracker`, `dead-code-remover`, `dependency-auditor`, `catalog-consistency-auditor`, `repository-archaeology`, `change-risk-assessment`, `operational-readiness-review`, `service-ownership-and-lifecycle-management`, `toil-analysis-and-automation` |
| 🔄 Git | `commit-writer`, `branch-manager`, `codeowners-and-review-routing` |

## Domain 5: Software Architecture
*Styles, patterns, DDD, Clean/Hex/Onion/Layered, Event-Driven, Microservices, architectural assessment*

| Skill | What it does |
|-------|-------------|
| `clean-architecture-principles` | Clean Architecture layers, dependency rule |
| `architecture-review` | Review an architecture against requirements, boundaries, risks, operability, and tradeoffs |
| `backward-compatibility-and-change-management` | Review interface, schema, and behavior changes for compatibility impact |
| `domain-driven-design-patterns` | DDD tactical + strategic patterns |
| `distributed-systems-patterns` | CAP, consistency models, sagas, consensus |
| `resilience-patterns` | Circuit breaker, retry, bulkhead, rate limiter |

## Domain 6: System Design
*HLD, LLD, scalability, reliability, availability, tradeoffs, solution design review*

| Skill | What it does |
|-------|-------------|
| `design-review` | Review a proposed design against requirements, complexity, alternatives, usability, and maintainability |
| `distributed-systems-patterns` | CAP, consistency models, sagas, consensus, data partitioning |
| `resilience-patterns` | Circuit breaker, retry, bulkhead, rate limiter, graceful degradation |

## Domain 7: Design Principles
*SOLID, DRY, KISS, YAGNI, GRASP, Separation of Concerns*

| Skill | What it does |
|-------|-------------|
| `clean-code-principles` | SOLID, DRY, KISS, YAGNI, small functions, naming, smells |

## Domain 8: Databases
*Relational, NoSQL, schema design, indexing, optimization, migrations*

| Skill | What it does |
|-------|-------------|
| `spring-data-jpa-patterns` | N+1 detection, JOIN FETCH, EntityGraphs, batch, pagination |
| `flyway-migration-patterns` | Versioned DB migrations, naming, safety patterns |
| `data-modeler` | Design DB schemas, entities, relationships |
| `db-migration-writer` | Write versioned SQL/ORM migration files |
| `data-transform` | Convert JSON, CSV, YAML, base64, dates |

## Domain 9: APIs & Integration
*REST, GraphQL, gRPC, design, documentation, testing*

| Skill | What it does |
|-------|-------------|
| `api-documenter` | Generate API docs from code/specs |
| `api-tester` | Quick API endpoint testing with curl |

## Domain 11: Security
*Secure design, auth, RBAC, secrets, dependency auditing*

| Skill | What it does |
|-------|-------------|
| `spring-security-patterns` | Firebase Auth, RBAC, tenant isolation, CORS |
| `dependency-auditor` | Audit packages for CVEs, outdated, licenses |

## Domain 12: DevOps
*CI/CD, Docker, K8s, IaC, build systems, deployment*

| Skill | What it does |
|-------|-------------|
| `docker-configurator` | Generate Dockerfile, compose, .dockerignore |
| `project-initializer` | Scaffold new projects with structure, config, tooling |
| `env-configurator` | Set up .env files and environment config |
| `change-risk-assessment` | Assess delivery risk and recommend rollout safeguards |
| `operational-readiness-review` | Review whether a service or feature is ready to operate in production |
| `service-ownership-and-lifecycle-management` | Define ownership, support expectations, and lifecycle states |
| `toil-analysis-and-automation` | Identify repetitive manual work and design sustainable automation |

## Domain 14: Testing
*Unit, integration, system, acceptance, performance, automation*

| Skill | What it does |
|-------|-------------|
| `unit-test-writer` | Write unit tests for existing code |
| `integration-test-writer` | Write integration tests for API/DB flows |
| `test-fixture-generator` | Generate reusable test factories and seed data |
| `java-testing-patterns` | JUnit 5, Mockito, Spring Boot Test, Testcontainers |
| `react-testing-library-patterns` | Vitest + RTL, user interactions, async behavior |
| `pytest-regression-suite` | Hermetic pytest regression suite for repos that ship validation/audit scripts but have no tests |

## Domain 15: Debugging & Analysis
*RCA, logging, profiling, incident investigation, failure analysis*

| Skill | What it does |
|-------|-------------|
| `failure-analysis` | Timeline, causal network, defense-in-depth, action scoring |

## Domain 17: Reliability Engineering
*SRE, HA, DR, monitoring, circuit breakers, retry, idempotency*

| Skill | What it does |
|-------|-------------|
| `resilience-patterns` | Circuit breaker, retry, bulkhead, rate limiter, graceful degradation |
| `operational-readiness-review` | Review whether a service is truly ready for production operation |

## Domain 18: Repository Intelligence
*Repository analysis, auditing, dependency analysis, tech debt, dead code, consistency drift, and historical reconstruction*

| Skill | What it does |
|-------|-------------|
| `tech-debt-tracker` | Scan for TODOs, complexity, code smells |
| `dead-code-remover` | Find and remove unused exports, files, deps |
| `dependency-auditor` | Audit packages for CVEs, outdated, licenses |
| `catalog-consistency-auditor` | Audit skill catalogs and repository docs for drift against the actual skill set |
| `repository-archaeology` | Reconstruct how a codebase evolved using history, docs, naming drift, and structural clues |
| `change-risk-assessment` | Assess delivery risk and recommend safeguards before rollout |
| `operational-readiness-review` | Review whether a service or feature is ready for production operation |
| `service-ownership-and-lifecycle-management` | Define ownership, stewardship, and lifecycle states for systems |
| `toil-analysis-and-automation` | Identify repetitive low-value work and choose the right automation intervention |

## Domain 19: Code Quality
*Code reviews, refactoring, static analysis, linting, readability*

| Skill | What it does |
|-------|-------------|
| `clean-code-principles` | Teach Clean Code — naming, functions, DRY, KISS, smells |
| `pr-writer` | Write structured PR descriptions from git diff |
| `document-reviewer` | Review docs for clarity, structure, completeness |
| `codeowners-and-review-routing` | Define ownership boundaries and review routing rules |
| `code-review` | Two-axis review (Standards + Spec) |
| `code-review-and-quality` | Multi-axis code review |
| `code-review-excellence` | Effective code review practices |

## Domain 20: Documentation
*README, architecture docs, API docs, ADRs, runbooks, specs*

| Skill | What it does |
|-------|-------------|
| `readme-writer` | Generate README from project context |
| `api-documenter` | Generate API docs from code/specs |
| `code-documenter` | Add docstrings and code documentation |
| `code-commenter` | Add inline explanatory comments |
| `document-reviewer` | Review docs for clarity, structure, completeness |
| `documentation-and-adrs` | Record durable engineering context in docs, notes, and decision records |
| `architecture-decision-records` | Write and maintain formal Architecture Decision Records |

## Domain 21: Research
*Technical research, literature review, source evaluation, knowledge synthesis*

| Skill | What it does |
|-------|-------------|
| `research-methodology` | Source hierarchy, CRAAP test, RFC analysis, synthesis |

## Domain 25: Analytical Thinking
*First-principles, critical thinking, systems thinking, decision analysis*

| Skill | What it does |
|-------|-------------|
| `analytical-thinking-patterns` | First-principles, systems thinking, tradeoff analysis, decision frameworks |
| `autonomous-learner` | Knowledge acquisition guided by analytical frameworks |
| `adjacent-disciplines` | Cognitive biases, decision science, systems thinking |

## Domain 27: Long-Term Engineering Mindset
*Ownership, accountability, professional skepticism, continuous learning*

| Skill | What it does |
|-------|-------------|
| `long-term-engineering-mindset` | Ownership, accountability, curiosity, evidence-based |
| `compositional-deep-audit` | Ocean-deep repo/skill-store audit ascending a compositional pyramid (file→folder→cluster→category→set→collection→topology) |
| `autonomous-learner` | Continuous learning across domains |
| `analytical-thinking-patterns` | Evidence-based decision making |
| `clean-code-principles` | Simplicity and maintainability |
| `clean-architecture-principles` | Long-term thinking at the architecture level |
| `capability-orchestrator` | Select, sequence, compose engineering capabilities into a plan |
| `capability-router` | Route a request to the right capability by SDLC phase |
| `engineering-phase-detector` | Detect the active SDLC phase of a request or artifact |
| `assumption-and-bias-check` | Surface hidden assumptions, bias, and overconfidence |
| `systems-thinking` | Feedback loops, delays, second-order effects for systemic problems |

## Domain 28: Adjacent Disciplines
*Systems engineering, HCI, cognitive psychology, decision science, leadership*

| Skill | What it does |
|-------|-------------|
| `adjacent-disciplines` | Systems eng, HCI, cognitive psych, game theory, leadership |

## 🧰 Cross-Cutting Skills

| Skill | What it does |
|-------|-------------|
| `data-transform` | Convert JSON, CSV, YAML, base64, dates |
| `regex-builder` | Build, explain, test regular expressions |
| `api-tester` | Quick API endpoint testing with curl |
| `skills-browser` | Interactive skill browser and reference |
| `autonomous-learner` | Self-directed knowledge acquisition |
| `project-initializer` | Scaffold new repos with structure, config, tooling |
| `env-configurator` | Set up .env files and environment config |

## 🤖 Meta-Skills

This repository also includes higher-order workflow skills such as `implement`, `triage`, `to-prd`, `to-issues`, `wayfinder`, `wizard`, `teach`, `handoff`, `grill-me`, `grill-with-docs`, and `writing-great-skills`.

These operate as orchestration or guidance layers rather than narrow engineering capabilities.

---

## Summary

| Category | Count |
|----------|-------|
| Domain catalog entries | 64 custom skills |
| Meta/workflow skills | present in repository but not exhaustively enumerated here |
| **Repository total** | **240 verified skills** |

---

*Skills in this catalog are managed through the repo/global mirror model and synced into `~/.agents/skills/`.*
*📚 See [SKILL-CATALOG.md](SKILL-CATALOG.md) for SDLC-phase organization and [SDLC-PHRASE-CHEATSHEET.md](SDLC-PHRASE-CHEATSHEET.md) for natural-language command reference*
