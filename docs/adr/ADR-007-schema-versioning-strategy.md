# ADR 007: Schema Versioning Strategy

## Status
Accepted

## Context
As generators evolve, metadata outputs might change in structure, breaking consumers (UI, Graph exporters).

## Decision
All generated metadata files will include a root `schema_version` attribute. Additionally, `docs/SCHEMA_REGISTRY.md` and `data/metadata/schema_registry.json` will act as the single source of truth for all current schema layouts.

## Consequences
- Requires tracking versions explicitly in generators.
- Allows automated compatibility tests in `interface_validator.py`.
