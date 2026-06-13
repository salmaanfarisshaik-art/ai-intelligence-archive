import os
from datetime import datetime, timezone
from typing import List, Dict, Any
from scripts.lib.base_sync import BaseSync
from scripts.lib.logger import setup_logger
from scripts.lib.normalizer import Normalizer
from scripts.lib.deduplicator import deduplicator
from scripts.lib.source_metrics import metrics
from scripts.sources.huggingface_fetcher import fetch_hf_models

logger = setup_logger("model_sync")

class ModelSync(BaseSync):
    def __init__(self):
        super().__init__(schema_name="model", output_dir=os.path.join("data", "processed", "models"))

    def fetch(self) -> List[Dict[Any, Any]]:
        """
        Phase 2 flow: fetch -> normalize -> deduplicate -> return clean dataset.
        HuggingFace models API is the primary source.
        """
        logger.info("Fetching model data from HuggingFace")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            raw_models = fetch_hf_models(limit=50)
            logger.info(f"Received {len(raw_models)} raw records from HuggingFace")
        except Exception as e:
            logger.error("HuggingFace fetcher failed for models", exc_info=True)
            metrics.record_source_failure("huggingface_models")
            raw_models = []

        if not raw_models:
            logger.warning("No HuggingFace data available for models. Returning empty list.")
            return []

        # Normalize
        normalized = Normalizer.normalize("huggingface", raw_models)
        logger.info(f"Normalized {len(normalized)} records for models")

        # Deduplicate
        deduped, removed = deduplicator.remove_duplicates(normalized)
        logger.info(f"Deduplicated models: {len(deduped)} kept, {removed} removed")

        # Transform normalized records into model schema
        records = []
        for rec in deduped:
            payload = rec.get("raw_payload", {})
            model_id = payload.get("id", "")
            records.append({
                "unique_id": rec["unique_id"],
                "schema_version": "1.0",
                "name": model_id,
                "parameters": str(payload.get("safetensors", {}).get("total", "Unknown")),
                "license": payload.get("cardData", {}).get("license", "Unknown") if isinstance(payload.get("cardData"), dict) else "Unknown",
                "context_window": 0,
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
