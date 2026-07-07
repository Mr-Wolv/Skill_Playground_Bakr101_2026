---
name: pr-writer
description: Write structured pull request descriptions from git diff and branch context
---

# PR Writer

Generates well-structured pull request descriptions from code changes and branch context.

## When to use

- You've made changes and need to open a PR
- You need to describe your changes clearly for reviewers
- You want a consistent PR format across the team

## Instructions

1. **Analyze the changes** — read the git diff to understand what files changed and why
2. **Identify the change type** — feature, fix, refactor, chore, docs, test
3. **Structure the description**:
   - **Summary**: one-line description of what this PR does
   - **Motivation**: why this change was needed (link to issue if applicable)
   - **Changes**: bullet list of specific changes grouped by area
   - **Testing**: how the changes were verified
   - **Review notes**: any areas where reviewer attention is needed
4. **Follow conventional commit format** for the title

## Example

```markdown
## feat: add atomic click count increment to URL shortener

### Motivation
The previous implementation used a read-then-write pattern
that could lose click counts under concurrent access.

### Changes
- Replaced `updateClickCount(code, count)` with `incrementClickCount(code)`
- SqliteStore now uses SQL: `SET click_count = click_count + 1`
- InMemoryStore uses `+= 1` (atomic for single-threaded Node.js)

### Testing
- Added concurrent increment test (10 parallel visits)
- All 17 existing tests pass

### Review notes
The SQLite atomic increment runs in a transaction — no explicit
locking needed for sql.js (single-connection, synchronous driver).
```

## Guidelines

- Keep the title under 72 characters
- Reference related issues with `Closes #123` or `Relates to #456`
- Include screenshots for UI changes
- Call out any breaking changes with a `BREAKING CHANGE:` footer
