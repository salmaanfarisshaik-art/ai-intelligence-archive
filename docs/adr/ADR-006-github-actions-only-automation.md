# ADR 006: GitHub Actions Only Automation

## Status
Accepted

## Context
Automating cron jobs, releases, and artifact generation requires compute. We want to avoid paid VMs or external CI/CD platforms.

## Decision
All automation relies entirely on GitHub Actions, utilizing the free runner tier. The repository must be executable from a fresh clone within minutes.

## Consequences
- No vendor lock-in beyond GitHub.
- Execution boundaries are limited to runner max time, requiring efficient, incremental, and idempotent processing.
