# Global Agent Instructions

Use this family of documents as a cross-project always-on instruction layer for agents.

The goal is to improve skill usage, engineering discipline, and long-term coherence without importing repository-specific maintenance rules into unrelated projects.

## Recommended Default

If you want one concise default for personal/global instructions, use:

- [Global Agent Instructions — Personal Copy-Paste Block](./GLOBAL-AGENT-INSTRUCTIONS-PERSONAL-COPYPASTE.md)

## Available Variants

- [Global Agent Instructions — Minimal](./GLOBAL-AGENT-INSTRUCTIONS-MINIMAL.md)
  - best when you want lightweight guidance with minimal standing instruction weight
- [Global Agent Instructions — Strict](./GLOBAL-AGENT-INSTRUCTIONS-STRICT.md)
  - best when you want stronger discipline around skill usage, anti-duplication behavior, and workflow quality
- [Global Agent Instructions — Personal Copy-Paste Block](./GLOBAL-AGENT-INSTRUCTIONS-PERSONAL-COPYPASTE.md)
  - best when you want a single block to paste directly into a personal/global instruction field

## Design Principles

A good global instruction layer should:

- shape defaults without overfitting to one repository
- improve consistency across projects
- increase the likelihood that relevant skills are actually used
- reduce duplication and ad hoc workflow invention
- stay short enough to avoid drowning out task-specific context

## Scope Boundary

Keep project-specific rules in repository-local `AGENTS.md` files.

Use global instructions for:

- default skill-usage behavior
- anti-duplication posture
- cross-project engineering discipline
- decision heuristics that are broadly useful everywhere

Do not use global instructions for:

- repository-specific paths
- mirror/sync rules tied to one repo
- file inventories or catalog counts
- local release or maintenance procedures specific to one project
