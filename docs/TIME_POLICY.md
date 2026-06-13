# Deterministic Time Policy

## Purpose
Prevent accidental loss of reproducibility.

## Rules
Generated artifacts must not contain:
- `datetime.now()`
- `utcnow()`
- current timestamps
- random UUID timestamps

unless explicitly approved.

## Allowed Artifacts
- `reports/run_manifest.json`
- `reports/audit_report.md`
- release metadata
- snapshot metadata

## Forbidden Artifacts
- `leaderboards.json`
- `knowledge_graph.json`
- `recommendations.json`
- `coverage_metrics.json`
- `repository_intelligence.json`

## Goal
Identical inputs must continue to produce byte-for-byte identical outputs.
