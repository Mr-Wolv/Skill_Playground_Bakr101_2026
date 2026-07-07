---
name: env-configurator
description: Set up .env files, environment variables, and multi-environment configuration
---

# Environment Configurator

Sets up environment configuration for applications across development, staging, and production.

## When to use

- A project needs environment variable management
- Setting up deployment configs for multiple environments
- Documenting required environment variables for a project

## Instructions

1. **Examine the codebase** — find all `process.env.*` or equivalent references
2. **Create a `.env.example`** with all required variables, their types, and descriptions
3. **Create environment-specific files**:
   - `.env.development` — defaults for local dev
   - `.env.staging` — staging overrides
   - `.env.production` — production overrides (values as placeholders)
4. **Add validation** — create a startup check that verifies all required env vars are set
5. **Update `.gitignore`** to exclude actual `.env` files (keep `.env.example` only)

## Example

```bash
# .env.example
# ──────────────────────
# Database
DATABASE_URL=postgres://user:pass@localhost:5432/myapp
DATABASE_POOL_SIZE=10

# Authentication
JWT_SECRET=change-me-in-production
JWT_EXPIRES_IN=3600

# API
PORT=3000
NODE_ENV=development
LOG_LEVEL=debug
```

## Best practices

- Never commit real secrets to version control
- Use a secrets manager (Vault, AWS Secrets Manager) for production
- Validate required vars at startup, not on first use
- Document what each variable controls
- Use typed config objects (e.g., pydantic-settings, env-var) for runtime access
