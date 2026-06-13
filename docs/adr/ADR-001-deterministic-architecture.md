# ADR 001: Deterministic Architecture

## Status
Accepted

## Context
The AI Intelligence Archive relies on predictable outcomes. Without determinism, duplicate commits are generated, increasing Git repository size and making audits impossible.

## Decision
All generated artifacts must be deterministic. We will use stable sorting, predefined indentation, and utf-8 encoding for all JSON/YAML/Markdown files. Timestamps are forbidden except in specific diagnostic reports.

## Consequences
- Requires custom serialization wrappers (`scripts/lib/serialization.py`).
- Eliminates noise in version control.
