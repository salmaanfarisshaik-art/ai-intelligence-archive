# ADR 0002: Deterministic Entity IDs

## Status
Accepted

## Context
To prevent duplicate ingestion and maintain stable relationships over time, entities require canonical IDs.

## Decision
Canonical IDs are generated deterministically using a SHA256 hash of stable, normalized metadata (e.g., domain + source URL).

## Consequences
- Repeated ingestions of the same data produce identical IDs.
- Graph edges can safely rely on these IDs across pipeline phases.
