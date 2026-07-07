---
name: docker-configurator
description: Generate Dockerfile, docker-compose.yml, .dockerignore for containerized deployments
---

# Docker Configurator

Generates production-ready Docker configuration files for containerized applications.

## When to use

- You need to containerize an application for deployment
- Setting up local development with docker-compose
- Optimizing an existing Dockerfile for smaller images

## Instructions

1. **Identify the runtime** — Node.js, Python, Go, Java, or Rust
2. **Generate a multi-stage Dockerfile**:
   - **Stage 1 (deps)**: Install production dependencies only
   - **Stage 2 (build)**: Compile/transpile source code
   - **Stage 3 (production)**: Copy only what's needed to run, use a smaller base image
3. **Add best practices**:
   - Non-root user
   - HEALTHCHECK instruction
   - `.dockerignore` to exclude unnecessary files
   - Proper `EXPOSE` port
4. **Generate docker-compose.yml** for local development with volumes and environment variables

## Example structure

```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:22-alpine AS production
WORKDIR /app
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
COPY --from=build /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
USER appuser
EXPOSE 3000
HEALTHCHECK --interval=30s CMD wget --spider http://localhost:3000/health
CMD ["node", "dist/index.js"]
```

## Edge cases

- Private npm packages (need auth config in docker build)
- Native dependencies (may need build tools in the deps stage)
- Multi-service apps (use docker-compose with depends_on and healthchecks)
