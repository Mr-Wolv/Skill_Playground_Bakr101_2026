# Semgrep custom rule examples (companion to the sast-configuration skill)

These rules illustrate the `Custom Rule Development` section of the skill.
Drop them in a `rules/` dir and run:

```bash
semgrep --config rules/ --json --output .sast/custom.json .
```

## Hardcoded JWT secret

```yaml
rules:
  - id: hardcoded-jwt-secret
    languages: [python, javascript, typescript, go, java]
    severity: ERROR
    message: JWT secret should not be hardcoded
    pattern: jwt.encode($DATA, "...", ...)
```

## Dangerous deserialization

```yaml
rules:
  - id: unsafe-pickle
    languages: [python]
    severity: ERROR
    message: Avoid pickle.loads on untrusted input
    pattern: pickle.loads($X)
```

## SQL string concatenation (injection surface)

```yaml
rules:
  - id: sql-concat
    languages: [python]
    severity: WARNING
    message: Use parameterized queries instead of string formatting
    patterns:
      - pattern-either:
          - pattern: $CURSOR.execute("..." % $X, ...)
          - pattern: $CURSOR.execute(f"..." , ...)
```

## Reusing the skill's runner

The skill documents `./scripts/run-sast.sh --setup --language python --tools semgrep,sonarqube`
to verify tooling is present before scanning. Point `--config` at a folder of
rules like the ones above.
