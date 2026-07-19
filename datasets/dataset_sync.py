import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from core.base_sync import BaseSync
from core.normalizer import Normalizer
from core.deduplicator import deduplicator
from scripts.sources.hf_datasets import HFDatasetsFetcher
from core.config_loader import config

class DatasetSync(BaseSync):
    def __init__(self):
        self.schema_version = "1.0"
        super().__init__(
            schema_name="dataset",
            output_dir="datasets"
        )
        self.fetcher = HFDatasetsFetcher(
            endpoint=config.sources.get("huggingface_datasets", {}).get("endpoint", "https://huggingface.co/api/datasets")
        )

    def fetch(self) -> List[Dict[Any, Any]]:
        records = []
        now = datetime.now(timezone.utc).isoformat()

        # Fetch from HF Datasets
        hf_data = self.fetcher.fetch()
        
        # Normalize and build records
        for item in hf_data:
            # Deterministic normalization
            dataset_id = item.get("_id") or item.get("id")
            if not dataset_id:
                continue

            normalized = {
                "unique_id": f"hf_ds_{dataset_id}",
                "schema_version": self.schema_version,
                "name": item.get("id", "Unknown"),
                "description": item.get("description", "No description available"),
                "size": str(item.get("downloads", 0)),
                "source_url": f"https://huggingface.co/datasets/{item.get('id')}",
                "source_name": "HuggingFace Datasets",
                "source_type": "api",
                "category": "dataset",
                "raw_payload": item,
                "retrieval_timestamp": now,
                "last_updated": item.get("lastModified", now)
            }
            records.append(normalized)

        # Deduplicate deterministically
        records, removed = deduplicator.remove_duplicates(records)

        return records

    def transform(self, data: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        from core.link_builder import link_builder
        from core.ai_enrichment import ai_enricher
        
        data = link_builder.build_links(self.schema_name, data)
        data = ai_enricher.enrich(self.schema_name, data)
        return data

