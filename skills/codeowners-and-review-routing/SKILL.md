---
name: codeowners-and-review-routing
description: Define repository ownership boundaries, CODEOWNERS rules, and review routing so changes reach the right reviewers with clear approval expectations.
---

# Codeowners and Review Routing

Use this skill when a repository needs clear ownership, predictable review routing, and enforceable review boundaries.

This skill is about workflow governance around who reviews what, how ownership is mapped to the repository, and how to reduce review ambiguity for critical areas.

## Use when

- setting up or improving `CODEOWNERS`
- defining review ownership by directory, subsystem, or domain
- protecting critical paths with required reviewers
- reducing confusion about who should review which changes
- aligning repo structure with team ownership boundaries
- tightening approval rules for sensitive or high-risk areas

## Do not use when

- you want a qualitative review of code correctness or style — use `code-review` or `code-review-and-quality`
- you want repository history or inferred ownership from past commits — use `repository-archaeology`
- you want branch operations like create/switch/merge — use `branch-manager`

## Core workflow

1. **Map the repository shape**
   - identify stable ownership boundaries
   - prefer meaningful domains or subsystems over superficial folder splits
   - avoid assigning ownership to paths that do not represent a real responsibility boundary

2. **Map the human ownership model**
   - identify teams, maintainers, or responsible engineers
   - distinguish broad ownership from required approval ownership
   - note areas that need security, platform, or architecture review

3. **Design routing rules**
   - assign default owners for broad areas
   - assign narrower owners for critical subpaths
   - keep rules as simple as possible while still routing correctly
   - avoid overlapping patterns that create noisy reviewer assignment

4. **Define protection intent**
   - which paths need strict review gates?
   - which paths need domain-owner approval?
   - which paths should require security/platform/data review?
   - which paths can use broad fallback ownership?

5. **Write or improve `CODEOWNERS`**
   - start broad, then specialize
   - order rules carefully so specific paths override broader ones
   - keep comments explaining non-obvious routing decisions

6. **Validate maintainability**
   - check whether the rule set matches the actual org structure
   - check for orphaned paths
   - check for ownership concentration on one person
   - check whether frequent changes would page too many reviewers

7. **Document the review policy**
   - explain the ownership model
   - explain what approvals are required for sensitive areas
   - explain how to request ownership changes

## Design principles

- prefer durable subsystem boundaries over temporary project phases
- prefer small, understandable rule sets over hyper-detailed routing logic
- keep broad fallback ownership for uncategorized paths
- separate "who knows this area" from "who must approve this area"
- align ownership with real operational responsibility, not just code location

## Good outputs

A good result usually includes:

- a proposed ownership map
- a `CODEOWNERS` file or patch
- notes on risky or ambiguous boundaries
- recommended branch protection / approval rules
- a short explanation of how to maintain the routing model over time

## Review checklist

- Are all important paths owned?
- Are sensitive paths owned by the right specialists?
- Are the most specific rules placed below broader ones as needed by the platform?
- Is the ownership model understandable to a new engineer?
- Would this reduce review latency and ambiguity?
- Would this survive a modest team reorganization?

## Typical trigger phrases

- "set up CODEOWNERS"
- "who should review what in this repo"
- "route reviews automatically"
- "protect critical paths in this repository"
- "assign ownership by directory"
- "define approval rules for sensitive code"
