# GitHub Secrets, Environments & OIDC

How to manage secrets safely in GitHub Actions: repository/org secrets, Environments with
protection rules, and OIDC (no static cloud keys). The `secrets-management` SKILL.md shows the
basic `${{ secrets.X }}` usage; this reference covers the full picture — scoping, rotation,
protection rules, and the OIDC path that removes long-lived credentials entirely.

> **Golden rule:** secrets are injected as environment variables at runtime and are **masked in
> logs**. Never `echo` them, never write them to artifacts, never pass them as plain CLI args that
> show in process listings. Use `::add-mask::` for any dynamically retrieved secret.

---

## 1. Repository & Organization Secrets

1. **Repository secrets** — `Settings → Secrets and variables → Actions → New repository secret`. Available to all workflows in that repo.
2. **Organization secrets** — set at the org level; choose visibility: **All repos**, **Private**, or **Selected repos**. Avoid duplicating the same secret per repo.
3. **Reference in YAML**:
   ```yaml
   env:
     API_KEY: ${{ secrets.API_KEY }}
   ```
4. **Org secrets override nothing** — repo-level secrets with the same name take precedence within that repo. Document the precedence to avoid confusion.
5. **Secret names are case-insensitive and immutable in value** — you update the value; you cannot retrieve it again (GitHub stores a hash).
6. **Limit who can write secrets** — only repo admins / org owners by default; tighten branch protection so secret-using workflows can't be triggered from a forked PR with injected values.

## 2. Environment Secrets & Protection Rules

7. **Create an Environment** — `Settings → Environments → New environment` (e.g. `staging`, `production`).
8. **Environment secrets** — scoped to that environment; `production` secrets are not visible to the `staging` job:
   ```yaml
   deploy:
     environment: production
     env:
       PROD_API_KEY: ${{ secrets.PROD_API_KEY }}
   ```
9. **Required reviewers** — add approvers; the job pauses until a human approves. Essential for prod deploys.
10. **Wait timer** — optional delay before the environment job starts.
11. **Branch/deployment protection** — restrict which branches can deploy to the environment (e.g. only `main`).
12. **Environment must be named in the job** for its secrets to resolve — `environment: production` is what grants access.

## 3. Fork & Pull-Request Safety

13. **PRs from forks cannot read repo secrets** — by default GitHub blocks secret exposure to forked-PR workflows. Good. Don't disable this.
14. **Don't `pull_request_target` with secrets lightly** — `pull_request_target` runs in the *base* repo context and *can* access secrets; a malicious PR could exploit it. Use it only with extreme care, or use `pull_request` + a separate trusted job.
15. **Scope secrets to the job that needs them** — declare under the specific job/`environment`, not globally, to minimize blast radius.

## 4. OIDC — Eliminate Static Cloud Keys

16. **Enable OIDC in the cloud** — configure a federated identity provider (AWS IAM OIDC provider, GCP Workload Identity Federation, or Azure AD app) trusting `https://token.actions.githubusercontent.com`.
17. **GitHub OIDC token** — every job can request a short-lived token via `permissions: id-token: write`; no secret needed:
    ```yaml
    permissions:
      id-token: write   # enables OIDC
      contents: read
    ```
18. **AWS via OIDC** (no static keys):
    ```yaml
    - uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: arn:aws:iam::123456789012:role/github-actions
        aws-region: us-west-2
    # IAM role condition: token claims sub == "repo:org/repo:ref:refs/heads/main"
    ```
19. **GCP via WIF** — map the GitHub subject (`repo:org/repo:ref:refs/heads/main`) to a service account in the workload identity pool.
20. **Vault via OIDC** — `hashicorp/vault-action` with `method: jwt` and a Vault role bound to the GitHub subject claim (see `vault-setup.md`).
21. **Condition the trust on subject + audience** — restrict which repos/branches/environments may assume the role; `repo:*:*` is too broad.

## 22. Secret Retrieval & Masking in Workflows

22. **Mask dynamically fetched secrets** — when you pull a secret via CLI (AWS/GCP/Vault), mask it so it can't print:
    ```bash
    SECRET=$(aws secretsmanager get-secret-value --secret-id x --query SecretString --output text)
    echo "::add-mask::$SECRET"
    echo "DB_PASSWORD=$SECRET" >> "$GITHUB_ENV"
    ```
23. **Don't log the env file** — `$GITHUB_ENV` is readable by later steps; never `cat` it.

## 5. Rotation & Hygiene

24. **Rotate on a schedule** — cloud OIDC creds rotate themselves; for static secrets (DB passwords), rotate quarterly and update the GitHub secret.
25. **Use Vault/AWS Secrets Manager as the source** — GitHub secret holds only a *reference token*; the real secret is fetched at runtime and rotated centrally.
26. **No secrets in workflow YAML** — only `${{ secrets.X }}` references. A literal value in a committed file is a leaked secret.
27. **Secret scanning** — enable GitHub's push-protection / secret scanning; it blocks commits containing detected secrets and alerts on leaks.
28. **Audit secret access** — org audit log shows who changed secrets; review periodically.

## 6. Least Privilege & Separation

29. **Separate secrets per environment** — `STAGING_DB_URL` vs `PROD_DB_URL`; never reuse prod creds in staging.
30. **Minimal IAM/OIDC role** — the assumed cloud role should only permit what the deploy needs (no `*` on S3 or IAM).
31. **Document secret requirements** — a `SECRETS.md` (or repo wiki) lists every secret a workflow expects, who owns it, and its rotation cadence.

## 7. Anti-Patterns

32. **Static cloud keys in secrets** — OIDC exists; a leaked static key is a standing credential.
33. **One mega-secret for everything** — scoping per environment/role limits blast radius.
34. **`pull_request_target` + secrets + untrusted input** — classic supply-chain exploit path.
35. **Printing secrets "for debugging"** — even masked, avoid; and never to artifacts (artifacts are not masked).
36. **Forgetting protection rules on prod** — an Environment without required reviewers is just a named secret bag.

## Quick Start

1. Move cloud creds to OIDC (AWS IAM role / GCP WIF / Azure AD) — delete static keys.
2. Create `staging` and `production` Environments; add required reviewers + branch restrictions.
3. Put env-specific secrets in each Environment, not globally.
4. Add `permissions: id-token: write` to jobs that need cloud access.
5. Enable push-protection / secret scanning.
6. Document every secret; set a rotation calendar.
7. Verify a dry-run deploy resolves secrets without printing them.
