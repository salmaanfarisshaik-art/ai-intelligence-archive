# ADR 0001: No Database Architecture

## Status
Accepted

## Context
The repository needs to be cloned and built anywhere without external runtime dependencies, maximizing resilience and reproducibility.

## Decision
We will use a purely file-based architecture (`data/processed/`, `data/metadata/`, `site/`). No SQL, NoSQL, or vector databases will be used for canonical storage or retrieval.

## Consequences
- Requires full regeneration or deterministic incremental builds.
- File system acts as the database.
- Guarantees 100% clone-and-run portability.
