---
name: dependency-auditor
description: Audit project dependencies for CVEs, outdated packages, and license compliance
---

# Dependency Auditor

Audits project dependencies for security vulnerabilities, outdated versions, and license issues.

## When to use

- Before a production release
- As part of a regular security review cycle
- When a CVE is announced for a package you use

## Instructions

1. **Scan lock files** — `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `requirements.txt`, `Cargo.lock`
2. **Check for CVEs** — run `npm audit`, `pip-audit`, `cargo audit`, or `snyk test`
3. **Check for outdated packages** — run `npm outdated`, `pip list --outdated`, `cargo outdated`
4. **Check licenses** — identify packages with incompatible licenses (GPL, AGPL, custom)
5. **Generate a report** — prioritize by severity (critical, high, medium, low)

## Report prioritization

| Severity | Action | Timeline |
|----------|--------|----------|
| Critical | Update immediately | Within hours |
| High | Update as soon as possible | Within a week |
| Medium | Schedule for next sprint | Within a month |
| Low | Add to backlog | Next opportunity |

## Edge cases

- Transitive dependencies (a package you don't directly import has a CVE — check if it's actually reachable)
- Breaking changes in major version updates (need migration plan)
- Deprecated packages (find alternatives and plan migration)
- License conflicts with corporate policy
