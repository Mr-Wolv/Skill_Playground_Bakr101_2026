# Code Review — Security Checklist

A focused, concrete checklist for reviewing **code changes** for security defects. Use this alongside the five-axis review in `SKILL.md` (Axis 4: Security). Every item is a thing you can verify by reading the diff or running a quick check — not a policy doc.

Severity legend: **[Critical]** = blocks merge (RCE, auth bypass, data leak); **[High]** = must fix before merge; **[Med]** = fix soon; **[Low]** = nit / optional.

---

## 1. Authentication & Authorization

- [ ] **[Critical] Every protected endpoint/handler enforces authentication.** No route that returns user-specific or privileged data is reachable without a verified identity. (Search for handlers that read `req.user`/`context.user` only after an `authenticate` middleware runs — a misordered middleware chain silently skips it.)
- [ ] **[Critical] Authorization is checked, not just authentication.** `if (!req.user)` is not enough — verify the user is allowed to act on *this* resource (`task.ownerId === req.user.id`, role checks, tenant scoping). Object-level (not just route-level) access control.
- [ ] **[High] Authorization checks live in the service/data layer, not only the router.** A second caller path (internal job, GraphQL resolver, gRPC) bypassing the router must still be blocked. Don't rely on the HTTP layer as the only gate.
- [ ] **[High] Passwords/sessions use the right primitives.** Password hashing with bcrypt/scrypt/argon2 (cost ≥ 12 for bcrypt); session tokens are `httpOnly`, `secure`, `sameSite`. No plaintext passwords, no JWTs signed with `alg: none`, no symmetric secret committed.
- [ ] **[High] ID/token comparison uses constant-time comparison** (`crypto.timingSafeEqual`) for session IDs, reset tokens, API keys — not `==`/`===`, which leaks via timing.
- [ ] **[Med] Privilege changes require re-authentication or step-up.** Email/password/role changes, especially admin actions, re-verify the actor.
- [ ] **[Med] No insecure direct object references (IDOR).** User-supplied IDs (`?id=`, path params) are not trusted to imply ownership — always re-check ownership server-side.
- [ ] **[Med] CORS is not wildcard-with-credentials.** `Access-Control-Allow-Origin: *` together with `Allow-Credentials: true` is rejected by browsers, but partial wildcards (`https://*.example.com`) or reflect-the-origin are footguns. Confirm the allowed-origin set is explicit.
- [ ] **[Low] Logout/session revocation actually invalidates the session/token** (server-side denylist or short TTL), not just client-side cookie deletion.

## 2. Input Validation & Encoding

- [ ] **[High] All external input is validated at the system boundary** (route handler, form parser, webhook receiver, message consumer) with a schema (zod, joi, pydantic) — type, range, length, allowed values. Not just "is present."
- [ ] **[High] Validation rejects, then parses** — do not trust the raw request body downstream. `safeParse`/explicit guard before use; reject with `422` and structured errors.
- [ ] **[Critical] Output is encoded for its context to prevent XSS.** Framework auto-escaping is left intact; no `innerHTML`/`dangerouslySetInnerHTML`/template HTML with user data unless sanitized (DOMPurify). JSON/attribute/URL contexts each need the right encoding.
- [ ] **[High] File uploads are constrained.** Allowed MIME types, max size, and (for risky cases) magic-byte/extension validation. Uploaded files are served with a safe `Content-Type` and `Content-Disposition`, never executed from an upload path.
- [ ] **[Med] URLs/redirects from user input are allowlisted.** Open redirects (`?next=//evil.com`) and SSRF (server fetches user-supplied URL) are validated against a host/allowlist and reject private/loopback IPs.
- [ ] **[Med] Numbers and IDs are bounds-checked** (pagination `page`/`limit`, `take`/`skip`) to prevent oversized fetches or negative values breaking queries.
- [ ] **[Low] Unicode/normalization attacks are considered** for usernames, emails, file names (NFKC normalization, homoglyphs, path traversal via `../` or encoded variants).

## 3. Injection

- [ ] **[Critical] No string concatenation into SQL/NoSQL/ORM raw queries.** Every query uses parameterized statements or the ORM's typed query builder. Grep for template literals and `+` inside query strings.
- [ ] **[Critical] No `eval`, `Function()`, `new Function`, or `vm` with user data.** No dynamic `require`/`import` from input. No shelling out with interpolated strings (`exec("ls " + dir)`) — use argument arrays (`execFile(cmd, [args])`).
- [ ] **[High] No user input in XPath, LDAP, or template expressions** without parameterization/escaping for that dialect.
- [ ] **[High] Deserialization of untrusted data is avoided or pinned.** `JSON.parse` is fine; `pickle.loads`/`yaml.load`/`unserialize` on untrusted bytes is RCE. Use `yaml.safe_load` and allowlisted classes.
- [ ] **[High] Regex from user input is safe** — bounded, with timeouts, to avoid ReDoS (catastrophic backtracking) on `(a+)+$`-style patterns with attacker-controlled input.
- [ ] **[Med] Format-string / log-injection** — no `printf(userInput)`; user data in format strings or logs is escaped so it can't inject new log lines or control sequences.
- [ ] **[Med] XML/SSRF via parsed documents** — disable external entity resolution (XXE) in XML parsers (`LIBXML_NONET`, `resolveEntity` off); forbid doctype where not needed.
- [ ] **[Med] Command/query builders escape identifiers** — table/column names from config are from a trusted allowlist, never from request data.

## 4. Secrets Management

- [ ] **[Critical] No secrets in source, config, or commit history.** API keys, tokens, passwords, PEM files, `.env` live outside VCS (use `.gitignore`). Run `git diff --cached | grep -iE "password|secret|api_key|token|-----BEGIN"` before merge.
- [ ] **[High] Secrets come from the environment / secret manager**, never hardcoded or templated into source. Access fails fast if unset (`if (!SECRET) throw`).
- [ ] **[High] No secret in logs, errors, or responses.** Stack traces, serialized request objects, and API error bodies must not echo tokens, passwords, or full credentials.
- [ ] **[High] `.env.example` is committed with placeholders only**; real `.env` and `*.local` are git-ignored. The ignore list covers `*.pem`, `*.key`, `credentials.json`.
- [ ] **[Med] If a secret was ever committed, it is rotated, not just deleted.** Deleting the line doesn't revoke a leaked key — revoke/rotate first, then purge history.
- [ ] **[Low] Secrets have appropriate scope and expiry** (short-lived tokens over long-lived, per-environment secrets, not one global key).

## 5. Dependency & Supply-Chain Review

- [ ] **[High] `npm audit` / `pip-audit` / `govulncheck` shows no critical/high reachable vulnerabilities** on the changed dependency set. Run in CI; block on critical.
- [ ] **[Med] New dependencies are justified** — does the stack already solve this? Check maintenance, download counts, license compatibility, and `postinstall` scripts in unfamiliar packages (arbitrary code at install).
- [ ] **[Med] Lockfile is committed and CI installs with `npm ci` / `pip install -r requirements.lock`** — no silent version drift; reproducible builds.
- [ ] **[Med] Watch for typosquats and transpoles** (`cross-env` vs `crossenv`, `react-dom` vs `reactdom`). Pin to exact/known package names.
- [ ] **[Low] Dev-only advisories are triaged separately** from runtime-reachable ones (see the audit decision tree in `security-and-hardening`).

## 6. Logging, Audit & Error Handling

- [ ] **[High] Security-relevant events are audited**: auth success/failure, privilege changes, data export, admin actions — with who/what/when and a correlation ID, durable enough to support non-repudiation.
- [ ] **[High] Errors are generic to users, detailed for operators.** Responses return `4xx/5xx` with safe messages; stack traces, SQL, internal paths, and framework versions stay server-side.
- [ ] **[High] No sensitive data in logs** — passwords, tokens, full PAN/PII, or unredacted bodies. Allowlist fields; never `logger.info(req.body)`.
- [ ] **[Med] Logs are structured (JSON) with stable event names and a correlation/request ID** on every line, so a single request can be reconstructed from interleaved output.
- [ ] **[Med] Failures fail safe, not open.** Auth/validation errors default to deny; a misconfigured auth provider or missing claim denies access rather than granting it.
- [ ] **[Med] Error handling doesn't swallow security signals** — empty `catch` blocks, `catch (e) {}`, or falling back to "allow" on exception hide attacks and bugs.
- [ ] **[Low] Rate limiting / lockout present on auth and sensitive endpoints** to blunt brute force and credential stuffing.

## 7. Cross-Cutting Review Notes

- [ ] **[High] Untrusted data sources are treated as hostile everywhere** — not just the HTTP body. Webhooks, message queues, uploaded files, third-party API responses, and **LLM/model output** are all untrusted input (no `eval`/SQL/DOM/shell with model output).
- [ ] **[Med] Security headers present**: CSP, HSTS, `X-Frame-Options`/`frame-ancestors`, `X-Content-Type-Options: nosniff`. (Confirm in the response, not just the code.)
- [ ] **[Med] Concurrency/race conditions in security checks**: TOCTOU between "is this allowed" and "do the action" under parallel requests; use DB constraints / atomic checks / row locks where ownership or balance is involved.

---

### How to use this list
- Walk the diff against each section; mark every finding **Critical / High / Med / Low**.
- Lead with security and correctness findings; quantify when possible ("this N+1 adds ~50ms per row").
- One Critical finding *is* the review — don't bury it under nits.
- Do not modify `SKILL.md`. This file is the supporting reference for Axis 4 (Security) and the `security-and-hardening` skill.
