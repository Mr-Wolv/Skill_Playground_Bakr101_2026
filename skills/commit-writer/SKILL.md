---
name: commit-writer
description: Write conventional commit messages from staged changes
---

# Commit Writer

Generates structured commit messages following the Conventional Commits specification.

## When to use

- You've made changes and need to commit them
- You want consistent, well-formatted commit messages
- Preparing for automated changelog generation

## Instructions

1. **Read the staged changes** — `git diff --cached` to understand what changed
2. **Categorize the change**:
   - `feat`: a new feature
   - `fix`: a bug fix
   - `chore`: maintenance, tooling, configuration
   - `docs`: documentation only
   - `refactor`: code change that neither fixes nor adds
   - `test`: adding or updating tests
   - `perf`: performance improvement
   - `style`: formatting, missing semicolons, etc. (no code change)
3. **Format the message**:
   ```
   <type>(<scope>): <short summary>
   
   <body (optional)>
   
   <footer (optional)>
   ```
4. **Follow guidelines**:
   - Subject: < 72 chars, imperative mood, no period
   - Body: wrap at 72 chars, explain what and why (not how)
   - Footer: `BREAKING CHANGE: description` or `Closes #123`

## Examples

```
feat(api): add rate limiting to shorten endpoint

Adds express-rate-limit middleware to the POST /shorten route
(30 req/min per IP) to prevent abuse.

Closes #42
```

```
fix(store): resolve race condition in click count increment

Changed from read-then-write to SQL-level atomic increment:
SET click_count = click_count + 1
```

```
refactor(auth): extract JWT validation into middleware

BREAKING CHANGE: auth middleware now requires `JWT_SECRET` env var
instead of reading from config file.
```

## Anti-patterns

- Vague messages like "fix stuff" or "update"
- Messages that only describe what (the diff shows what) without explaining why
- Mixing multiple unrelated changes in one commit
- Using `-m` for complex commits (write the body in an editor)
