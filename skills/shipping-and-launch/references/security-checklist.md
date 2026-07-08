# Launch Security Checklist

Run this checklist as part of the pre-launch gate for every production deployment. It is the
security subsection of the launch Definition of Done, expanded with concrete, verifiable items.
Pair it with the performance and accessibility checklists before exposing users to the change.

## Secrets & Credentials

- [ ] **No secrets in source or VCS** — grep the repo and history (`git log -p | grep -iE 'password|secret|token|api_key'`); use secret scanning (TruffleHog/GitGuardian) in CI.
- [ ] **No secrets in logs** — error reporting and structured logs never serialize credentials, tokens, or PII.
- [ ] **Secrets sourced from a store** — Vault / AWS Secrets Manager / platform secret store, never env files committed to the repo.
- [ ] **Per-environment secrets** — dev/staging/prod use distinct credentials; prod secrets are not reused in lower environments.
- [ ] **Short-lived tokens** — where possible, use OIDC/assume-role instead of long-lived static keys.
- [ ] **Secret rotation enabled** — rotation mechanism exists and is tested; rotation does not require a redeploy.
- [ ] **`.env` and keys git-ignored** — `.gitignore` covers `.env`, `*.pem`, `credentials.json`, etc.

## Dependency & Supply Chain

- [ ] **Dependency audit clean** — `npm audit` / `pip-audit` / `cargo audit` show no critical/high (fix or formally accept with rationale).
- [ ] **Locked versions** — lockfiles committed (`package-lock.json`, `poetry.lock`, `go.sum`); no unpinned `latest`.
- [ ] **No abandoned packages** — critical deps are maintained; no known-unmaintained libraries in the path.
- [ ] **SBOM available** — a software bill of materials exists for audit and incident response.
- [ ] **CI secret scanning** — every push is scanned; the job fails closed on a detected secret.

## Authentication & Authorization

- [ ] **Auth on every protected route** — no endpoint relies on "nobody will guess it."
- [ ] **Authorization checked server-side** — client-side gating is UX only; the server re-checks the principal's permissions.
- [ ] **No IDOR** — object access uses the authenticated principal, not a user-supplied ID alone (`/api/orders/{id}` checks ownership).
- [ ] **Rate limiting on auth endpoints** — login, signup, password-reset throttled to blunt credential stuffing.
- [ ] **Account lockout / backoff** — brute-force protection with exponential backoff or CAPTCHA after N failures.
- [ ] **Session management safe** — httpOnly, Secure, SameSite cookies; server-side session invalidation on logout.
- [ ] **Password hashing** — bcrypt/scrypt/argon2 with per-user salt; no plaintext or fast hashes (MD5/SHA1).

## Input Handling

- [ ] **Input validation on all user-facing endpoints** — schema-validated at the boundary (zod, pydantic, javax validation).
- [ ] **Output encoding** — HTML/JS/CSS context-aware encoding to prevent XSS.
- [ ] **SQL parameterized** — no string-built queries; ORMs use bound parameters.
- [ ] **CSP configured** — Content-Security-Policy restricts script/style sources (no `'unsafe-inline'` where avoidable).
- [ ] **File upload sanitized** — type/size validated, stored outside web root or served via signed URL, names not trusted.

## Transport & Headers

- [ ] **HTTPS enforced** — HSTS set (`Strict-Transport-Security: max-age=31536000; includeSubDomains`).
- [ ] **TLS current** — TLS 1.2+ only; weak ciphers disabled; cert valid and auto-renewing.
- [ ] **Security headers present** — CSP, X-Content-Type-Options: nosniff, X-Frame-Options: DENY/SAMEORIGIN, Referrer-Policy.
- [ ] **CORS scoped** — explicit origin allowlist; no `Access-Control-Allow-Origin: *` with credentials.
- [ ] **Cookies flagged** — Secure + httpOnly + SameSite on all sensitive cookies.

## Infrastructure & Runtime

- [ ] **Least privilege** — the app runs as non-root; IAM/role permissions are minimal for the task.
- [ ] **Network exposure minimized** — only required ports open; admin interfaces not public.
- [ ] **WAF / edge protection** — optional but recommended for public apps (rate limit, common-attack rules).
- [ ] **Audit logging** — security-relevant events (auth, privilege changes, secret access) are logged and tamper-evident.
- [ ] **Secrets access logged** — Vault/store audit log captures who read what and when.

## Data Protection

- [ ] **PII minimized** — collect only what's needed; unnecessary personal data not stored.
- [ ] **Encryption at rest** — databases and object storage encrypted (KMS-managed keys).
- [ ] **Encryption in transit** — all service-to-service traffic TLS/mTLS where applicable.
- [ ] **Retention & deletion** — a defined retention policy; user deletion request honored.

## Incident Readiness

- [ ] **Security contact** — a named owner / on-call for security issues.
- [ ] **Rollback does not leak** — rollback/migration steps do not expose secrets in logs or temp files.
- [ ] **Breach runbook** — a documented response plan exists (rotate, contain, notify).

## Using the Checklist

This is binary: any unchecked item that applies to your service is a launch blocker. "We'll add it
later" is the most common cause of a post-launch incident — security configured after exposure is
security that was never really there.
