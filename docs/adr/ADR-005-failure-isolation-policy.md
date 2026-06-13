# ADR 005: Failure Isolation Policy

## Status
Accepted

## Context
Adding experimental or ecosystem-level generators (like leaderboards and recommendations) shouldn't crash the core ingestion loop.

## Decision
All Phase 6+ modules execute sequentially inside independent `try-except` blocks. A failure in one simply logs the error and continues to the next module. Soft failures are reported via `run_health.json` and `run_manifest.json`.

## Consequences
- High resilience.
- Ensures core data is always ingested even if a downstream visualization fails.
