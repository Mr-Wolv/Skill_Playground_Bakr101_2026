---
name: branch-manager
description: Daily git branch operations — create, switch, merge, rebase, delete
---

# Branch Manager

Handles everyday git branch operations with safe workflows.

## When to use

- Starting work on a new feature or fix
- Updating your feature branch with the latest main
- Cleaning up after a merge

## Instructions

1. **Create a new branch** — `git checkout -b feat/my-feature main`
2. **Commit work as you go** — small, focused commits with conventional messages
3. **Keep your branch up to date**:
   - `git fetch origin`
   - `git rebase origin/main` (preferred for clean history)
   - Or `git merge origin/main` (if you prefer merge commits)
4. **Handle conflicts** — if rebase/merge has conflicts:
   - Resolve the conflicting files
   - `git add` the resolved files
   - Continue: `git rebase --continue` or `git commit`
5. **Push** — `git push -u origin feat/my-feature`
6. **Clean up** — after the PR is merged, delete the local branch:
   - `git branch -d feat/my-feature`
   - `git push origin --delete feat/my-feature`

## Naming conventions

| Pattern | Example |
|---------|---------|
| `feat/description` | `feat/add-login-page` |
| `fix/issue-description` | `fix/null-pointer-in-user-service` |
| `chore/description` | `chore/update-dependencies` |
| `refactor/area` | `refactor/extract-auth-middleware` |
| `docs/description` | `docs/update-api-reference` |

## Safety tips

- Never force push to shared branches unless the team agrees
- Rebase before push, not after (changes history on remote)
- Use `git stash` to save uncommitted changes before switching branches
- Check your status with `git status` before any branch operation
- `git branch -d` only deletes if fully merged; use `git branch -D` to force delete
