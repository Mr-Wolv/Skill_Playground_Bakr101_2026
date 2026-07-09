# SDLC Phrase Cheatsheet

> **How to talk to me so I load the right skill.**
> Just say what you want in plain English — I match your intent automatically.
> 📚 [Documentation Index](docs/index.md) | [SDLC Catalog](SKILL-CATALOG.md) | [Domain Catalog](SKILL-CATALOG-DOMAIN.md) | [Repo Root](SKILL.md)
> 📦 This repo is a community export of your global skill store (`~/.agents/skills/`, the source of truth). Export with `python scripts/sync_global_to_repo.py`.

---

## Quick Reference

| Phase | You Say... | Skill Loaded |
|-------|------------|--------------|
| 🏗️ **Architecture** | *"Architect this"* / *"Design the architecture"* | `clean-architecture-principles` |
| 🏗️ **Architecture review** | *"Review this architecture"* / *"Assess this architecture"* / *"Is this architecture sound?"* | `architecture-review` |
| 🔁 **Compatibility review** | *"Is this a breaking change"* / *"Maintain backward compatibility"* / *"Compatibility review"* | `backward-compatibility-and-change-management` |
| 📐 **Design review** | *"Review this design"* / *"Is this design too complex?"* / *"Evaluate this proposal"* | `design-review` |
| 🏗️ **DDD** | *"Model this domain"* / *"Apply DDD patterns"* | `domain-driven-design-patterns` |
| 💻 **Scaffold** | *"Set up a new project"* / *"Initialize a repo"* | `project-initializer` |
| 💻 **Env config** | *"Set up environment variables"* / *"Create .env"* | `env-configurator` |
| 💻 **Docker** | *"Containerize this app"* / *"Create Dockerfile"* | `docker-configurator` |
| 🗄️ **DB schema** | *"Design the data model"* / *"Create a DB schema"* | `data-modeler` |
| 🗄️ **DB migration** | *"Write a migration"* / *"Add this column"* | `db-migration-writer` |
| 🔁 **Resilience** | *"Make this resilient"* / *"Add circuit breakers"* | `resilience-patterns` |
| 🔁 **Distributed** | *"Design distributed system"* / *"Handle consistency"* | `distributed-systems-patterns` |
| 🧪 **Unit tests** | *"Write tests"* / *"Add unit tests"* / *"Cover this"* | `unit-test-writer` |
| 🧪 **Integration tests** | *"Test the API"* / *"Write integration tests"* | `integration-test-writer` |
| 🧪 **Test fixtures** | *"Generate test data"* / *"Create factories"* | `test-fixture-generator` |
| 🧪 **React tests** | *"Test React components"* / *"RTL tests"* | `react-testing-library-patterns` |
| 🧪 **Java tests** | *"Test this Java code"* / *"JUnit tests"* | `java-testing-patterns` |
| ✅ **PR write** | *"Write a PR description"* / *"Summarize changes"* | `pr-writer` |
| 🧹 **Tech debt** | *"Find tech debt"* / *"Scan for TODOs"* | `tech-debt-tracker` |
| 🧹 **Dead code** | *"Clean up dead code"* / *"Remove unused"* | `dead-code-remover` |
| ✅ **CODEOWNERS** | *"Set up CODEOWNERS"* / *"Who should review what"* / *"Route reviews automatically"* | `codeowners-and-review-routing` |
| ⚠️ **Change risk** | *"How risky is this deploy"* / *"Do a preflight risk review"* / *"What safeguards should we add"* | `change-risk-assessment` |
| 🚦 **Operational readiness** | *"Are we operationally ready"* / *"Production readiness review"* / *"Go-live readiness"* | `operational-readiness-review` |
| 🧭 **Service ownership** | *"Who owns this service"* / *"Define service ownership"* / *"Set lifecycle policy"* | `service-ownership-and-lifecycle-management` |
| 🤖 **Toil reduction** | *"Automate this repetitive process"* / *"This is too manual"* / *"Find toil in this workflow"* | `toil-analysis-and-automation` |
| 🧭 **Catalog drift** | *"Audit catalog consistency"* / *"Find documentation drift"* / *"Reconcile skill indexes"* | `catalog-consistency-auditor` |
| 🏺 **Repository archaeology** | *"Explain how this code evolved"* / *"Trace the history of this subsystem"* / *"Why is this shaped like this?"* | `repository-archaeology` |
| 📖 **README** | *"Write a README"* / *"Generate project docs"* | `readme-writer` |
| 📖 **API docs** | *"Document this API"* / *"Generate API docs"* | `api-documenter` |
| 📖 **Code docs** | *"Add docstrings"* / *"Document this code"* | `code-documenter` |
| 📖 **Comments** | *"Add comments"* / *"Explain this code"* | `code-commenter` |
| 📖 **Review docs** | *"Review this document"* / *"Check this doc"* | `document-reviewer` |
| 🔍 **Failure analysis** | *"Analyze this failure"* / *"Postmortem deep-dive"* | `failure-analysis` |
| 🔍 **Research** | *"Research methodology"* / *"Evaluate sources"* | `research-methodology` |
| 🔒 **Dependency audit** | *"Audit dependencies"* / *"Check for CVEs"* | `dependency-auditor` |
| 🔒 **Spring security** | *"Configure security"* / *"Set up auth"* | `spring-security-patterns` |
| 🔄 **Spring Boot** | *"Spring Boot patterns"* / *"Build Spring app"* | `spring-boot-patterns` |
| 🔄 **JPA** | *"Optimize JPA queries"* / *"Fix N+1"* | `spring-data-jpa-patterns` |
| 🔄 **Flyway** | *"DB migration patterns"* / *"Flyway setup"* | `flyway-migration-patterns` |
| 🔄 **Mobile** | *"Capacitor setup"* / *"Android wrapper"* | `capacitor-mobile-patterns` |
| 🔄 **Commit** | *"Write a commit message"* / *"Conventional commit"* | `commit-writer` |
| 🔄 **Branch** | *"Manage branches"* / *"Git branch ops"* | `branch-manager` |
| 🔧 **Data transform** | *"Convert this data"* / *"Transform format"* | `data-transform` |
| 🔧 **Regex** | *"Build a regex"* / *"Test this pattern"* | `regex-builder` |
| 🔧 **API test** | *"Test this endpoint"* / *"Quick API check"* | `api-tester` |
| 👀 **Browse skills** | *"What skills are available?"* / *"List skills"* | `skills-browser` |
| 📐 **Clean code** | *"Write clean code"* / *"Apply SOLID"* | `clean-code-principles` |
| 🧠 **CS foundations** | *"CS fundamentals"* / *"Algorithms help"* | `computer-science-foundations` |
| 🧠 **Analytical thinking** | *"Think through this"* / *"First principles"* | `analytical-thinking-patterns` |
| 🧠 **Engineering mindset** | *"Long-term thinking"* / *"Engineering mindset"* | `long-term-engineering-mindset` |
| 🧠 **Learn** | *"I want to learn X"* / *"Teach me"* | `autonomous-learner` |
| 🧠 **Adjacent fields** | *"Cross-disciplinary insights"* / *"Related fields"* | `adjacent-disciplines` |
| 🧩 **Orchestrate** | *"Plan and sequence these capabilities"* / *"Compose a multi-step plan"* | `capability-orchestrator` |
| 🧭 **Route** | *"Which skill fits this request"* / *"Map this to a capability"* | `capability-router` |
| 🔭 **Detect phase** | *"What SDLC phase is this"* / *"Which phase are we in"* | `engineering-phase-detector` |
| 🛡️ **Assumptions** | *"Check my assumptions"* / *"Surface hidden bias"* | `assumption-and-bias-check` |
| 🔁 **Systems** | *"Model the feedback loops"* / *"Second-order effects"* | `systems-thinking` |
| 🪞 **Deep audit** | *"Audit this skill store"* / *"Compositional deep audit"* | `compositional-deep-audit` |
| 📜 **Contract test** | *"Consumer-driven contract test"* / *"API contract test"* | `api-contract-testing` |
| 🔐 **Threat model** | *"Derive security requirements"* / *"Map threats to controls"* | `security-requirement-extraction` |
| 🗺️ **Threat map** | *"Map threats to mitigations"* / *"Threat-to-control matrix"* | `threat-mitigation-mapping` |
| 🔭 **Distributed trace** | *"Trace requests across services"* / *"Jaeger/Tempo setup"* | `distributed-tracing` |
| 🔗 **Correlation** | *"Add correlation IDs"* / *"Propagate trace context"* | `correlation-tracing` |
| 📈 **SLO** | *"Define SLOs/SLIs"* / *"Error budget policy"* | `slo-implementation` |
| 📡 **Observability** | *"Set up SRE observability"* / *"Prometheus/Grafana/OTel"* | `observability-sre` |

---

## TL;DR

**Don't think about skill names. Just tell me what you want to do in English.**

- *"Write tests for this"* → I load the right test skill
- *"Set up Docker"* → I load Docker configurator
- *"Find tech debt"* → I scan the codebase
- *"Document this API"* → I generate docs
- *"Make this resilient"* → I add circuit breakers
- *"Design the architecture"* → I apply Clean Architecture

These skills are available through the repo/global mirror model (`skills/` ↔ `~/.agents/skills/`)
