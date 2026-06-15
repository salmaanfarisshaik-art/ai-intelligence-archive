import os
import json
from datetime import datetime, timezone
from scripts.lib.logger import setup_logger
from scripts.lib.serialization import save_json_deterministic

logger = setup_logger("provenance_tracker")

class ProvenanceTracker:
    def __init__(self, index_file: str = "data/metadata/provenance_index.json"):
        self.index_file = index_file
        self.provenance_data = {}
        self._load()

    def _load(self):
        if os.path.exists(self.index_file):
            with open(self.index_file, "r", encoding="utf-8") as f:
                self.provenance_data = json.load(f)
        else:
            logger.info(f"Provenance index {self.index_file} not found. Starting fresh.")

    def record_provenance(self, 
                          canonical_id: str, 
                          original_source: str, 
                          source_url: str, 
                          license_type: str, 
                          sync_version: str = "1.0", 
                          normalization_version: str = "1.0"):
        """
        Record the origin of an ingested entity.
        Does not overwrite if it already exists, as canonical entities must not lose provenance.
        """
        if not canonical_id:
            return
            
        if canonical_id not in self.provenance_data:
            self.provenance_data[canonical_id] = {
                "canonical_id": canonical_id,
                "original_source": original_source,
                "source_url": source_url,
                "retrieval_timestamp": datetime.now(timezone.utc).isoformat(),
                "license": license_type,
                "sync_version": sync_version,
                "normalization_version": normalization_version
            }
        else:
            # If it already exists, it might be a merge scenario. We preserve the original retrieval timestamp
            # but might update other metadata if explicitly requested. For now, strict preservation:
            pass

    def get_provenance(self, canonical_id: str) -> dict:
        return self.provenance_data.get(canonical_id, {})

    def save(self):
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        save_json_deterministic(self.index_file, self.provenance_data)
        logger.debug(f"Provenance index saved to {self.index_file}")
