import os
from datetime import datetime, timezone
from typing import List, Dict, Any
from scripts.lib.base_sync import BaseSync
from scripts.lib.logger import setup_logger, ErrorCategory
from scripts.lib.normalizer import Normalizer
from scripts.lib.deduplicator import deduplicator
from scripts.lib.source_metrics import metrics
from scripts.sources.arxiv_fetcher import fetch_arxiv_papers

logger = setup_logger("benchmark_sync")

class BenchmarkSync(BaseSync):
    def __init__(self):
        super().__init__(schema_name="benchmark", output_dir=os.path.join("data", "processed", "benchmarks"))

    def fetch(self) -> List[Dict[Any, Any]]:
        """
        Phase 2 flow: fetch -> normalize -> deduplicate -> return clean dataset.
        ArXiv papers with benchmark-related content are used as the source.
        """
        logger.info("Fetching benchmark data from ArXiv")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            raw_papers = fetch_arxiv_papers(max_results=50)
            logger.info(f"Received {len(raw_papers)} raw records from ArXiv")
        except Exception as e:
            logger.error("ArXiv fetcher failed for benchmarks", exc_info=True)
            metrics.record_source_failure("arxiv_benchmarks")
            raw_papers = []

        if not raw_papers:
            logger.warning("No ArXiv data available for benchmarks. Returning empty list.")
            return []

        # Normalize
        normalized = Normalizer.normalize("arxiv", raw_papers)
        logger.info(f"Normalized {len(normalized)} records for benchmarks")

        # Deduplicate
        deduped, removed = deduplicator.remove_duplicates(normalized)
        logger.info(f"Deduplicated benchmarks: {len(deduped)} kept, {removed} removed")

        # Transform normalized records into benchmark schema
        records = []
        for rec in deduped:
            payload = rec.get("raw_payload", {})
            records.append({
                "unique_id": rec["unique_id"],
                "schema_version": "1.0",
                "name": payload.get("title", "").strip().replace("\n", " ")[:200],
                "model": "N/A",
                "score": 0.0,
                "source_url": rec["source_url"],
                "source_name": rec["source_name"],
                "source_type": rec.get("source_type", "unknown"),
                "category": rec.get("category", "unknown"),
                "raw_payload": rec.get("raw_payload", {}),
                "retrieval_timestamp": now,
                "last_updated": rec.get("last_updated", now)
            })

        return records

    def transform(self, data: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        from scripts.lib.link_builder import link_builder
        from scripts.lib.ai_enrichment import ai_enricher
        
        data = link_builder.build_links(self.schema_name, data)
        data = ai_enricher.enrich(self.schema_name, data)
        return data

    # Validate, transform, and save are inherited from BaseSync.
