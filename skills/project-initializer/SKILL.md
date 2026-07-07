---
name: project-initializer
description: Scaffold new projects with directory structure, configuration files, and tooling setup
---

# Project Initializer

Scaffolds new software projects from scratch with proper structure, configuration, and tooling.

## When to use

- Starting a new project from scratch
- Setting up a consistent project structure across a team
- Adding missing configuration files to an existing project

## Instructions

1. **Ask the user** what kind of project (Node.js, Python, Go, Java, Rust) and the project name
2. **Create the directory structure** following project conventions:
   - `src/` or `lib/` for source code
   - `tests/` or `__tests__/` for tests
   - `docs/` for documentation
   - `scripts/` for automation
3. **Generate config files**:
   - Package manager config (package.json, pyproject.toml, go.mod, Cargo.toml)
   - TypeScript/type config (tsconfig.json, mypy.ini)
   - Linting (eslint, ruff, golangci-lint)
   - Testing framework (vitest, pytest, cargo test)
4. **Initialize version control** — create `.gitignore` and optionally `git init`
5. **Verify** the project compiles and tests pass

## Example output

```
my-project/
├── src/
│   └── index.ts
├── __tests__/
│   └── index.test.ts
├── docs/
│   └── index.md
├── .gitignore
├── package.json
├── tsconfig.json
└── README.md
```

## Edge cases

- Monorepo setups (use workspaces in package.json, pnpm, or Nx)
- Projects with native dependencies (ensure build tools are configured)
- Existing directories (don't overwrite without confirmation)
