# ADR 003: Phase Freeze Policy

## Status
Accepted

## Context
As the platform grows, modifying core ingestion logic (Phases 1-5) risks breaking downstream consumers.

## Decision
Phases 1-5 are locked and immutable. Phase 6+ modules must act purely as additive consumers.

## Consequences
- Protects historical data integrity.
- Forces a strict read-only boundary for new extensions.
