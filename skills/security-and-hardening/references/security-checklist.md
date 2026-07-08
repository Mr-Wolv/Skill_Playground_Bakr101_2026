# Security & Hardening — Checklist

A hardening checklist for **building and shipping secure systems**. Complements `SKILL.md`: start every feature with a threat model, then apply these controls. Items are concrete and verifiable; use them as a pre-commit / pre-release gate.

Severity legend: **[Critical]** = must be done / blocks release; **[High]** = required for production; **[Med]** = strong recommendation; **[Low]** = hardening / nice-to-have.

---

## 0. OWASP Top 10 (2021) Quick Reference

| # | Category | Primary defenses to apply below |
|---|----------|--------------------------------|
| A01 | Broken Access Control | Authz at object + route level, deny-by-default, IDOR checks |
| A02 | Cryptographic Failures | TLS everywhere, strong ciphers, encrypt at rest, no secrets in logs |
| A03 | Injection | Parameterized queries, output encoding, no `eval`/concat |
| A04 | Insecure Design | Threat model, abuse cases, least privilege by design |
| A05 | Security Misconfiguration | Hardened defaults, headers, no debug in prod, no default creds |
| A06 | Vulnerable & Outdated Components | Lockfile, `npm audit`, supply-chain review |
| A07 | Identification & Auth Failures | Strong hashing, MFA, rate-limit, lockout, session hygiene |
| A08 | Software & Data Integrity Failures | Signed deps/artifacts, no `postinstall` surprises, CI provenance |
| A09 | Security Logging & Monitoring Failures | Audit log, alerting, no secret leakage in telemetry |
| A10 | SSRF | Allowlist outbound URLs, block private/metadata IPs |

---

## 1. Threat Model First

- [ ] **[Critical] Trust boundaries are mapped** for every feature — where untrusted data enters (HTTP, uploads, webhooks, queues, third-party APIs, **LLM output**). Each boundary is attack surface.
- [ ] **[Critical] Assets are named** — credentials, PII, payment data, admin actions, money movement. You can't protect what you haven't listed.
- [ ] **[High] STRIDE run over each boundary** — Spoofing, Tampering, Repudiation, Information disclosure, DoS, Elevation of privilege — with a mitigation noted for each.
- [ ] **[High] Abuse cases written next to use cases** — for each feature, "how would I misuse this?" becomes the first test. Closes OWASP A04 (Insecure Design).

## 2. Least Privilege

- [ ] **[Critical] Services run with least privilege** — non-root containers, no `privileged`, drop capabilities, read-only root FS where possible.
- [ ] **[Critical] Database/users scoped per service** — app DB user has only the grants it needs (no superuser, no `GRANT ALL`); separate read vs write roles if feasible.
- [ ] **[High] IAM roles are per-service and least-privilege** — no wildcard `*` actions; scoping by resource ARN; no long-lived static keys where instance/ workload identity works.
- [ ] **[High] Authorization is object-level, not just route-level** — `task.ownerId === user.id` checked wherever the resource is accessed, in the data/service layer.
- [ ] **[Med] Admin/escalated actions require explicit role verification + re-auth** (step-up) and are audited.
- [ ] **[Med] File/system permissions are minimal** — secrets/files readable only by the owning user/service; `0700`/`0600` where appropriate.

## 3. Secrets Management

- [ ] **[Critical] No secrets in VCS** — `.env`, `*.pem`, `*.key`, `credentials.json` git-ignored; `.env.example` carries placeholders only. Pre-commit scan for `password|secret|api_key|token|-----BEGIN`.
- [ ] **[Critical] Secrets sourced from env / secret manager** (Vault, AWS Secrets Manager, etc.), never hardcoded; app fails fast if a required secret is unset.
- [ ] **[High] Lockfile committed; CI installs with `npm ci`/`pip install -r lock`** — reproducible, no silent drift.
- [ ] **[High] If a secret leaks, rotate first then purge** — deleting the line is not enough; assume compromised the moment it reaches a remote.
- [ ] **[Med] Short-lived, scoped tokens over long-lived keys**; per-environment secrets; rotation policy defined.
- [ ] **[Low] Secret access is logged** (who read what, when) for audit.

## 4. Transport Security (TLS)

- [ ] **[Critical] HTTPS/TLS for all external communication** — no plaintext HTTP for anything sensitive; redirect HTTP→HTTPS.
- [ ] **[High] HSTS enabled** with a reasonable `max-age` and `includeSubDomains` where applicable.
- [ ] **[High] TLS config is modern** — TLS 1.2+ (prefer 1.3), strong cipher suites, no SSLv3/TLS1.0/1.1; certs auto-renewed (ACME) with expiry alerting.
- [ ] **[Med] Certificate transparency / expiry monitoring** — alert before certs expire; pin or monitor CA where high-risk.
- [ ] **[Low] Internal service-to-service traffic also encrypted** (mTLS / service mesh) in zero-trust networks.

## 5. Security Headers

- [ ] **[High] Content-Security-Policy (CSP)** set — `default-src 'self'`, tighten `script-src`/`connect-src`; no `'unsafe-inline'` if avoidable.
- [ ] **[High] `X-Content-Type-Options: nosniff`** — prevents MIME sniffing.
- [ ] **[High] `X-Frame-Options: DENY` / `frame-ancestors 'none'`** — clickjacking protection.
- [ ] **[High] Referrer-Policy + Permissions-Policy** set sensibly (limit `camera`/`mic`/`geolocation`).
- [ ] **[Med] Headers verified in the live response** (DevTools), not just in code — a misconfigured proxy can strip them.

## 6. Dependency Scanning & Supply Chain

- [ ] **[Critical] `npm audit` / `pip-audit` / `govulncheck` clean of critical/high reachable vulns** in CI; block release on critical.
- [ ] **[High] New deps reviewed before adding** — maintenance, downloads, license, `postinstall` scripts (arbitrary install-time code). Watch typosquats.
- [ ] **[High] Signed/verified artifacts & dependencies** where the ecosystem supports it (npm provenance, sigstore, SLSA) — defeats A08.
- [ ] **[Med] Automated dependency updates** (Dependabot/Renovate) with tests gating the bump; stale deps tracked.
- [ ] **[Med] SBOM generated** for the release; triage advisories by reachability (dev-only vs runtime-reachable).
- [ ] **[Low] Private registry / proxy mirrors trusted sources**; block install from untrusted registries.

## 7. Patching & Lifecycle

- [ ] **[Critical] OS / base image patched** — start from a minimal, current base image; rebuild on a cadence; scan the image (`trivy`/`grype`).
- [ ] **[High] Known CVEs triaged on a schedule** — critical within days, high within the release cycle; deferred items get a documented reason + review date.
- [ ] **[High] No end-of-life runtimes/frameworks** in production (e.g. EOL Node/Python/TLS libs).
- [ ] **[Med] Patch window defined and tested** — can you roll a security fix fast? Dry-run the path.
- [ ] **[Low] Inventory of components/versions maintained** so a new CVE can be answered in minutes, not days.

## 8. Input Validation & Injection Defense

- [ ] **[Critical] All input validated at the boundary** with a schema (zod/joi/pydantic): type, length, range, enum.
- [ ] **[Critical] All queries parameterized** — no string concatenation into SQL/NoSQL/ORM raw.
- [ ] **[Critical] Output encoded to context** — framework auto-escaping intact; sanitize before any `innerHTML`.
- [ ] **[High] SSRF defense** — allowlist outbound URL scheme+host; reject private/loopback/metadata IPs (`169.254.169.254`); forbid redirects; pin resolved IP for high-risk surfaces.
- [ ] **[High] File upload constraints** — MIME, size, magic-byte check; safe serving (never executable from upload path).

## 9. Authentication & Session Hardening

- [ ] **[Critical] Passwords hashed (bcrypt/scrypt/argon2, cost ≥ 12)**; never plaintext; never reused across users.
- [ ] **[High] Session cookies `httpOnly`, `secure`, `sameSite`**; appropriate `maxAge`; tokens stored server-side or in HttpOnly cookie, never `localStorage` for auth.
- [ ] **[High] Rate limiting + lockout on auth endpoints** — blunt brute force / credential stuffing.
- [ ] **[High] Password reset / magic links expire and are single-use.**
- [ ] **[Med] MFA offered/enforced** for privileged accounts.
- [ ] **[Med] Generic auth error messages** — don't reveal whether the email or password was wrong.

## 10. Logging, Audit & Error Handling

- [ ] **[High] Security events audited** — auth success/failure, privilege changes, data export, admin actions (who/what/when, correlation ID).
- [ ] **[High] Error responses generic; details stay server-side** — no stack traces, SQL, or internal paths to users.
- [ ] **[High] No secrets/PII in logs or telemetry** — allowlist fields; never log whole bodies or tokens.
- [ ] **[Med] Monitoring + alerting on security signals** — spike in 401/403, repeated failures, unusual export volume.
- [ ] **[Med] Fail closed** — auth/validation errors deny by default, never allow on exception.

## 11. AI / LLM Surface (if applicable)

- [ ] **[High] Model output treated as untrusted** — no `eval`/SQL/DOM/shell with LLM output; validate + encode like raw user input.
- [ ] **[High] Secrets & other users' data kept out of prompts** — anything in context can be echoed back.
- [ ] **[High] Tool/agent permissions scoped** — minimum scope; destructive/irreversible actions require confirmation; every tool arg validated.
- [ ] **[Med] Prompt-injection assumed** — enforce permissions in code, not in the system prompt; isolate RAG retrieval per tenant.
- [ ] **[Med] Consumption bounded** — cap tokens, request rate, and recursion depth (LLM10: Unbounded Consumption).

---

### How to use this list
- Walk each section before release; the OWASP table at top maps categories → defenses.
- "Ask First" items in `SKILL.md` (new auth flows, CORS changes, file uploads, elevated perms) require human approval.
- "Never Do" items are hard blocks — committing secrets, disabling headers, `eval`/`innerHTML` with user data, client-side auth tokens.
- Do not modify `SKILL.md`. This file is the supporting reference for `security-and-hardening`.
