# Connectors

This file documents the integrations an agent *may* have access to when running
the incident-response (and related ops) skills. It is a placeholder manifest: a
real deployment populates it with the tools actually wired into the
environment. Skills reference it so they can say "check which tools are
connected" instead of assuming a specific integration.

## How to use

During an incident, the agent should:

1. Read this file to learn which systems are connected (chat, paging, ticketing,
   telemetry, source control, runbooks).
2. Only invoke a connector that is listed here as available.
3. If a needed connector is absent, say so and fall back to the closest
   available channel (or ask the user to connect it).

## Connector slots (fill per environment)

| Connector | Purpose | Status |
|-----------|---------|--------|
| Chat / war-room | Post status updates, coordinate responders | (connected / not) |
| Paging (e.g. PagerDuty, Opsgenie) | Page on-call, escalate | (connected / not) |
| Ticketing (e.g. Jira, Linear) | Open/link incident tickets | (connected / not) |
| Telemetry (e.g. Grafana, Datadog) | Pull dashboards, query metrics/logs | (connected / not) |
| Source control (e.g. GitHub, GitLab) | Open incident PRs, freeze deploys | (connected / not) |
| Runbook store | Link runbook steps | (connected / not) |

## Placeholder note

In this skill library the connector slots are intentionally empty. The skill
logic stays tool-agnostic; the deployment supplies the real bindings. Replace
the `(connected / not)` column with the actual state before relying on a
connector during a live incident.
