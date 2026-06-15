# ADR 0004: Read-Only Intelligence Layer

## Status
Accepted

## Context
Phase 9 introduces semantic indexing, entity linking, and knowledge graph generation. These processes must not contaminate the canonical source of truth.

## Decision
Phase 9 operates strictly as a read-only analytics layer. It may read from `data/processed/` and `data/metadata/` but can only write to derived paths (`site/`, `reports/`).

## Consequences
- Canonical data remains immutable during Phase 9 execution.
- Prevents cascading side-effects from derived insights.
