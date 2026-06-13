import os
from datetime import datetime, timezone
from typing import List, Dict, Any
from scripts.lib.base_sync import BaseSync
from scripts.lib.logger import setup_logger
from scripts.lib.normalizer import Normalizer
from scripts.lib.deduplicator import deduplicator
from scripts.lib.source_metrics import metrics
from scripts.sources.arxiv_fetcher import fetch_arxiv_papers
from scripts.sources.rss_fetcher import fetch_rss_feeds

logger = setup_logger("prompt_sync")

class PromptSync(BaseSync):
    def __init__(self):
        super().__init__(schema_name="prompt", output_dir=os.path.join("data", "processed", "prompts"))

    def fetch(self) -> List[Dict[Any, Any]]:
        """
        Phase 2 flow: fetch -> normalize -> deduplicate -> return clean dataset.
        ArXiv papers on prompt engineering + RSS AI news are the sources.
        """
        logger.info("Fetching prompt engineering data from ArXiv + RSS")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        all_normalized = []

        # Source 1: ArXiv prompt engineering papers
        try:
            raw_papers = fetch_arxiv_papers(max_results=30)
            logger.info(f"Received {len(raw_papers)} raw records from ArXiv for prompts")
            normalized_arxiv = Normalizer.normalize("arxiv", raw_papers)
            all_normalized.extend(normalized_arxiv)
        except Exception as e:
            logger.error("ArXiv fetcher failed for prompts", exc_info=True)
            metrics.record_source_failure("arxiv_prompts")

        # Source 2: RSS AI news feeds
        try:
            raw_rss = fetch_rss_feeds()
            logger.info(f"Received {len(raw_rss)} raw records from RSS feeds")
            normalized_rss = Normalizer.normalize("rss", raw_rss)
            all_normalized.extend(normalized_rss)
        except Exception as e:
            logger.error("RSS fetcher failed for prompts", exc_info=True)
            metrics.record_source_failure("rss_prompts")

        if not all_normalized:
            logger.warning("No external data available for prompts. Returning empty list.")
            return []

        logger.info(f"Total normalized records for prompts: {len(all_normalized)}")

        # Deduplicate across both sources
        deduped, removed = deduplicator.remove_duplicates(all_normalized)
        logger.info(f"Deduplicated prompts: {len(deduped)} kept, {removed} removed")

        # Transform normalized records into prompt schema
        records = []
        for rec in deduped:
            payload = rec.get("raw_payload", {})
            title = payload.get("title", payload.get("name", "Untitled")).strip().replace("\n", " ")[:200]
            description = payload.get("summary", payload.get("description", "")).strip().replace("\n", " ")[:500]
            records.append({
                "unique_id": rec["unique_id"],
                "schema_version": "1.0",
                "technique_name": title,
                "description": description,
                "example": "",
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
