# Extension Contract

## Purpose
Enforce the immutability of Phases 1-5 and govern how Phase 8+ modules may interact with the system.

## Rules
- **No modification of canonical records:** Modules must not modify Phase 1-5 outputs.
- **Additive only:** Extensions must read existing files and generate new derivative outputs.
- **Failure isolation:** Errors in new extensions must not bring down the main ingestion pipeline.
- **No external infrastructure:** No Redis, Elasticsearch, databases, or mandatory paid services.

## Approved Extension Points
- Consuming JSON indexes and generating new analysis.
- Adding new pure-static visualizations.

## Forbidden Modifications
- Altering the Phase 1-5 lifecycle (`fetch -> transform -> validate -> save`).
- Modifying atomic persistence utilities (`scripts/lib/file_utils.py`).
- Adding timestamps to non-allowed artifacts.
