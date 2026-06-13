# AI Intelligence Archive

Build the world's largest free, open-source, continuously updating repository of artificial intelligence knowledge, resources, benchmarks, research, models, datasets, tools, APIs, companies, safety information, and prompt engineering techniques.

The repository functions as a centralized AI intelligence hub where developers, researchers, students, founders, and enthusiasts can discover, compare, learn, and track the AI ecosystem.

## System Architecture Summary (Phase 1 & 2)

The system is powered by a production-grade, deterministic, and fully automated ingestion pipeline designed to be resilient against real-world instability.

### Phase 1: Core Framework & Idempotency Engine
Phase 1 established the rigid foundational infrastructure for data synchronization, ensuring zero data corruption and reproducible executions.
* **Strict Execution Order**: Execution is strictly sequential (`benchmark_sync` → `model_sync` → `prompt_sync`), avoiding race conditions in file writes.
* **Idempotency & Atomic Writes**: The pipeline calculates SHA-256 hashes of payloads (ignoring volatile timestamps). Disk writes only execute via atomic `.tmp` file swaps if the content semantically changes.
* **Safe Execution**: A native `DRY_RUN=true` flag simulates the entire pipeline without modifying disk states.
* **Unified Sync Contract**: `BaseSync` enforces a non-negotiable `fetch -> normalize -> validate -> save` lifecycle.

### Phase 2: Real-World Data Integration
Phase 2 upgraded the mock data pipeline into a live, multi-source ingestion engine capable of handling API failures and data overlaps.
* **Live Ingestion Sources**:
  * **ArXiv API**: Research papers for Benchmarks and Prompt Engineering (`cs.AI`, `cs.CL`, `cs.CV`).
  * **HuggingFace API**: State-of-the-art open-source models and parameters.
  * **RSS Feeds**: OpenAI and BAIR blogs for industry developments.
* **Resilience & Stability**:
  * **Centralized API Client**: All HTTP requests route through `api_client.py`, which handles timeouts and request structuring.
  * **Rate Limiting & Backoff**: Sleep-based throttles (e.g., 3s for ArXiv) and exponential backoff ensure API compliance.
  * **Failure Isolation**: Simulated failures prove that if an endpoint goes offline, the error is caught, logged to `external_sources_failed` in `run_health.json`, and the pipeline continues seamlessly.
* **Optimization & Integrity**:
  * **Intelligent Caching (`cache_manager.py`)**: Disk-based TTL caching intercepts redundant API calls, reducing warm execution times from ~45 seconds to < 1 second.
  * **Semantic Deduplication (`deduplicator.py`)**: Hash-based and case-insensitive title matching automatically squashes duplicates (e.g., identical papers appearing on ArXiv and an RSS feed).
  * **Data Normalization (`normalizer.py`)**: Disparate payloads are unified into a single schema (`source_type`, `category`, `raw_payload`) enforced by `RecordValidator`.

## Features
- **Free & Open Source**
- **Community Driven**
- **Automatically Updated** via GitHub Actions
- **Source Attributed** data
- **Fully Deterministic** ingestion pipeline

## Running Locally

1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
3. Install dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
4. Copy `.env.example` to `.env` and configure your API keys or run mode.
5. Run the orchestrator: `python scripts/main.py`
6. View pipeline execution metrics in `run_health.json`.
