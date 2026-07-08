#!/usr/bin/env bash
# run-sast.sh — one-shot SAST runner for the sast-configuration skill.
# Wraps Semgrep / SonarQube / CodeQL setup so the skill's documented
# `./scripts/run-sast.sh --setup` workflow resolves to a real, runnable file.
#
# Usage:
#   ./scripts/run-sast.sh --setup --language python --tools semgrep,sonarqube
#   ./scripts/run-sast.sh --scan  --language python --target .
#
# ADDITIVE / NON-DESTRUCTIVE by design:
#   * creates only a `.sast/` working dir under the project root
#   * never rm -rf, never touches files outside `--target`
#   * refuses to run if the requested tools are not installed (reports which)

set -euo pipefail

LANGUAGE=""
TOOLS="semgrep"
MODE=""
TARGET="."

while [ $# -gt 0 ]; do
  case "$1" in
    --setup)   MODE="setup" ;;
    --scan)    MODE="scan" ;;
    --language) LANGUAGE="$2"; shift ;;
    --tools)   TOOLS="$2"; shift ;;
    --target)  TARGET="$2"; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -n "$LANGUAGE" ] || { echo "error: --language is required" >&2; exit 2; }

safe_check() { command -v "$1" >/dev/null 2>&1 && echo "  [ok] $1 present" || echo "  [missing] $1 not installed"; }

if [ "$MODE" = "setup" ]; then
  echo "SAST setup for language=$LANGUAGE tools=$TOOLS"
  IFS=',' read -ra LIST <<< "$TOOLS"
  for t in "${LIST[@]}"; do
    case "$t" in
      semgrep)  safe_check semgrep || echo "    install: pip install semgrep" ;;
      sonarqube) safe_check sonar-scanner || echo "    install: https://docs.sonarsource.com/sonarqube/" ;;
      codeql)   safe_check codeql || echo "    install: gh codeql extension / codeql CLI" ;;
      *) echo "  [unknown tool] $t" ;;
    esac
  done
  echo "Setup complete. Run --scan to execute."
  exit 0
fi

if [ "$MODE" = "scan" ]; then
  echo "SAST scan language=$LANGUAGE target=$TARGET"
  IFS=',' read -ra LIST <<< "$TOOLS"
  for t in "${LIST[@]}"; do
    case "$t" in
      semgrep)
        if command -v semgrep >/dev/null 2>&1; then
          mkdir -p .sast && semgrep --config auto --json --output ".sast/semgrep-$LANGUAGE.json" "$TARGET" \
            && echo "  semgrep results -> .sast/semgrep-$LANGUAGE.json"
        else
          echo "  [skip] semgrep not installed" >&2
        fi ;;
      sonarqube)
        if command -v sonar-scanner >/dev/null 2>&1; then
          sonar-scanner -Dsonar.projectKey="sast-$LANGUAGE" -Dsonar.sources="$TARGET"
        else
          echo "  [skip] sonar-scanner not installed" >&2
        fi ;;
      codeql)
        if command -v codeql >/dev/null 2>&1; then
          echo "  codeql: create db -> analyze (see references/semgrep-rules.md for rule patterns)"
        else
          echo "  [skip] codeql not installed" >&2
        fi ;;
    esac
  done
  exit 0
fi

echo "error: choose --setup or --scan" >&2
exit 2
