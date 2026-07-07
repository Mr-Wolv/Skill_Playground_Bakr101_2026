---
name: readme-writer
description: Generate README files from project context, structure, and dependencies
---

# README Writer

Generates comprehensive README files from project codebase analysis.

## When to use

- A project is missing a README
- An existing README is outdated or incomplete
- Onboarding new contributors to an unfamiliar project

## Instructions

1. **Scan the project** — determine project name, language, runtime, and key dependencies
2. **Extract structure** — identify the main entry point, source layout, and test directory
3. **Generate sections**:
   - **Project name and description** — what it does, why it exists
   - **Quick start** — clone, install, configure, run
   - **Installation** — prerequisites and setup steps
   - **Usage** — code examples and common commands
   - **Configuration** — environment variables and config files
   - **Testing** — how to run tests
   - **Contributing** — how to submit changes
   - **License** — project license
4. **Use existing conventions** — mirror the style and tone of any existing docs

## What to include

- Badges (CI status, coverage, license) where applicable
- A table of contents for longer READMEs
- Architecture overview or project structure diagram
- Links to more detailed documentation

## Anti-patterns

- Writing a wall of text (use sections, lists, and code blocks)
- Assuming knowledge (explain prerequisites)
- Outdated setup instructions (test every step)
- No license section (clarify usage rights)
