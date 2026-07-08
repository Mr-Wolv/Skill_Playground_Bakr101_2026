# HashiCorp Vault Setup

Step-by-step, production-minded Vault setup: server, auth methods, secrets engines, policies, and
dynamic secrets. The `secrets-management` SKILL.md shows the dev-server one-liner; this reference
covers the path from dev to a hardened, access-controlled deployment. Vault is the centralized store
for secrets, dynamic credentials, encryption-as-a-service, and audit logging.

> **Never use `-dev` mode in production.** Dev mode stores everything in memory, uses a single
> unseal key, and is unauthenticated by default. The steps below move you to a real deployment.

---

## 1. Install & Run the Server

1. **Install Vault** — download the binary or package; verify the SHA256 signature before trusting it.
2. **Create a config file** (`vault.hcl`) — set `storage` (Consul/raft/file), `listener` (TLS), and `api_addr`.
3. **Start in server mode** (not dev):
   ```bash
   vault server -config=vault.hcl
   ```
4. **Initialize** — generates the unseal keys and root token (run once):
   ```bash
   vault operator init
   # Save the 5 unseal keys + root token to a secure location (not VCS, not chat)
   ```
5. **Unseal** — Vault starts sealed; supply threshold keys to unseal (default 3-of-5):
   ```bash
   vault operator unseal <key-1>
   vault operator unseal <key-2>
   vault operator unseal <key-3>
   ```
6. **Authenticate** — `export VAULT_ADDR=https://vault.example.com:8200 && vault login <root-or-token>`.
7. **Enable TLS on the listener** — terminate with a valid cert; never expose Vault over plain HTTP in prod.
8. **Use Raft/integrated storage (or Consul)** — for HA; file storage is single-node only.

## 2. Seal/Unseal & Operational Safety

9. **Auto-unseal (recommended)** — use AWS KMS / GCP KMS / Transit auto-unseal so nodes recover without manual key entry.
10. **Disable root token after setup** — generate a periodic admin token via a auth method instead of using root.
11. **Seal manually when compromised** — `vault operator seal` instantly blocks all access during an incident.

## 3. Enable Secrets Engines

12. **KV v2 (versioned secrets)** — the general-purpose store:
    ```bash
    vault secrets enable -path=secret kv-v2
    vault kv put secret/database/config username=admin password='$STRONG'
    vault kv get secret/database/config
    ```
13. **Cubbyhole / transient** — per-token private storage, auto-deleted when the token expires.
14. **Transit (encryption-as-a-service)** — encrypt app data without storing it:
    ```bash
    vault secrets enable transit
    vault write -f transit/keys/app-key
    vault write transit/encrypt/app-key plaintext=$(base64 <<<"secret")
    ```
15. **PKI (dynamic certs)** — issue and rotate TLS certificates automatically:
    ```bash
    vault secrets enable pki
    vault write pki/root/generate/internal common_name=example.com
    vault write pki/roles/example allowed_domains=example.com ttl=72h
    ```
16. **Database dynamic secrets** — Vault creates short-lived DB credentials on demand (see §5).
17. **SSH / AWS / GCP / Azure engines** — issue temporary cloud/SSH credentials instead of static keys.

## 4. Configure Authentication Methods

18. **Enable an auth method**: `vault auth enable github` (or `kubernetes`, `oidc`, `aws`, `approle`).
19. **GitHub auth** (human developers) — map GitHub teams to Vault policies:
    ```bash
    vault auth enable github
    vault write auth/github/config organization=my-org
    vault write auth/github/map/teams/platform policies=platform-read
    ```
20. **Kubernetes auth** (workloads) — Vault validates the pod's service account token:
    ```bash
    vault auth enable kubernetes
    vault write auth/kubernetes/config kubernetes_host=https://k8s.example.com
    vault write auth/kubernetes/role/app bound_service_account_names=app-sa \
      bound_service_account_namespaces=production policies=app-read ttl=15m
    ```
21. **AppRole** (machines without a native auth) — role_id + secret_id, short-lived; pair with a secure secret_id delivery.
22. **OIDC** (SSO users) — federate with your identity provider; map groups to policies.
23. **AWS/GCP auth** (cloud workloads) — use instance/role identity, never static keys.

## 5. Dynamic Database Secrets (example)

24. **Enable the database secrets engine**: `vault secrets enable database`.
25. **Configure the DB plugin** and a rotation statement:
    ```bash
    vault write database/config/postgres \
      plugin_name=postgresql-database-plugin \
      connection_url="postgresql://{{username}}:{{password}}@db:5432/app" \
      username=vault-admin password="$ADMIN_PW"
    ```
26. **Define a role** that creates short-lived creds:
    ```bash
    vault write database/roles/app-db \
      db_name=postgres \
      creation_statements="CREATE ROLE \"{{name}}\" LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT app TO \"{{name}}\";" \
      default_ttl=1h max_ttl=24h
    ```
27. **Read dynamic creds** — each read returns fresh, auto-expiring credentials:
    ```bash
    vault read database/creds/app-db
    ```

## 6. Write Policies (least privilege)

28. **Policy language (HCL)** — grant only the paths a role needs:
    ```hcl
    path "secret/data/database/*" { capabilities = ["read"] }
    path "database/creds/app-db"  { capabilities = ["read"] }
    ```
29. **Create the policy**: `vault policy write app-read app-read.hcl`.
30. **Attach policies to roles/auth mappings** — never grant `*` broadly; scope per service.
31. **Separate read vs write** — apps usually need `read` on secrets, not `create`/`delete`.

## 7. Audit & Rotate

32. **Enable audit logging** — mandatory for forensics:
    ```bash
    vault audit enable file file_path=/var/log/vault/audit.log
    ```
33. **Rotate the root token**: `vault token rotate` (and revoke the initial root after initial setup).
34. **Rotate encrypt/encryption keys**: `vault write -f transit/keys/app-key/rotate`.
35. **Rotate KV secrets** on a schedule; use versioning to roll back a bad value.
36. **Lease renewal/revocation** — dynamic secrets auto-expire; Vault revokes on lease end.

## 8. CI/CD Integration (GitHub Actions)

37. **Pull secrets into a pipeline** via `hashicorp/vault-action` (token from OIDC or a stored token):
    ```yaml
    - uses: hashicorp/vault-action@v2
      with:
        url: https://vault.example.com:8200
        method: jwt
        role: github-actions
        secrets: |
          secret/data/database username | DB_USERNAME ;
          secret/data/database password | DB_PASSWORD
    ```
38. **Prefer OIDC over static tokens** — the GitHub Actions OIDC token authenticates to Vault per-run; no long-lived secret to leak.

## 9. Kubernetes via External Secrets Operator

39. **External Secrets Operator** syncs Vault secrets into K8s `Secret` objects (the SKILL.md shows the `SecretStore` + `ExternalSecret` manifest). Set `refreshInterval` so rotation propagates.

## 10. Hardening Checklist

40. **TLS only**, strong cipher suite, valid certs.
41. **HA + auto-unseal** for production resilience.
42. **Audit device enabled** and shipped to tamper-evident storage.
43. **Root token revoked** post-bootstrap; daily admin via mapped auth.
44. **Policies least-privilege**, reviewed quarterly.
45. **Secret scanning + Vault audit** cross-checked for anomalies.
46. **Backups of encrypted storage** (Raft snapshots) stored securely; test restore.

## Quick Start (dev → prod)

1. `vault server -dev` to learn the CLI (local only).
2. Move to `vault server -config=vault.hcl` with TLS + storage.
3. `operator init` → record keys → `operator unseal` (or auto-unseal).
4. Enable KV v2 + the engines you need (transit, pki, database).
5. Enable auth (kubernetes/oidc/github) and map to policies.
6. Write least-privilege policies; attach to roles.
7. Enable audit device; revoke root; automate rotation.
8. Integrate CI/CD via OIDC; verify secrets resolve in a dry run.
