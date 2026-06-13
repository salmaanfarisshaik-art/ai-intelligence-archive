# Known Limitations

This document serves to explicitly outline the current boundaries of the AI Intelligence Archive. These are intentional architectural choices designed to maintain determinism, zero-cost operations, and extreme reproducibility, rather than defects.

## Architectural Boundaries

1. **Static Site Generation:** Optimized exclusively for GitHub Pages deployment. The generated site is completely static (`.html`) to ensure zero-cost hosting.
2. **Knowledge Graph Relationships:** Relationships are metadata-driven and derived deterministically from Phase 1-5 outputs. They do not rely on stochastic LLM inference during generation.
3. **Recommendation Engine:** Uses deterministic metadata similarity calculations (e.g., Jaccard similarity) instead of vector embeddings to guarantee reproducibility.
4. **Snapshot Archives:** Archives are strictly file-based (`.zip` exports) and are not distributed via peer-to-peer networks.
5. **Execution Environment:** Designed for single-machine execution (e.g., standard GitHub Actions runner). Parallel execution within the pipeline is not supported to prevent race conditions.
6. **No Database Infrastructure:** No external databases (PostgreSQL, MongoDB) are used by design. The file system acts as the database.
7. **No Distributed Framework:** Distributed execution frameworks (Kubernetes, Spark) are not supported by design to ensure execution remains simple and accessible.
8. **No Real-Time Streaming:** The repository operates on a scheduled batch-processing model. Real-time streaming infrastructure (Kafka, RabbitMQ) is excluded to minimize operational overhead and free-tier compatibility.

By adhering to these boundaries, the AI Intelligence Archive guarantees long-term stability and perfect determinism.
