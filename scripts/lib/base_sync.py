import json
import os
import hashlib
from typing import List, Dict, Any
from scripts.lib.logger import setup_logger, ErrorCategory
from scripts.lib.validator import RecordValidator

logger = setup_logger("base_sync")

class BaseSync:
    def __init__(self, schema_name: str, output_dir: str):
        self.schema_name = schema_name
        self.output_dir = output_dir
        self.validator = RecordValidator()
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch(self) -> List[Dict[Any, Any]]:
        raise NotImplementedError

    def validate(self, data: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        valid_data = []
        for record in data:
            if self.validator.validate_record(record, self.schema_name):
                valid_data.append(record)
        return valid_data

    def transform(self, data: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        return data

    def _hash_content(self, content: str) -> str:
        data = json.loads(content)
        for record in data:
            record.pop("last_updated", None)
            record.pop("retrieval_timestamp", None)
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()

    def _atomic_write(self, filepath: str, content: str):
        # Atomic write
        tmp_filepath = f"{filepath}.tmp"
        try:
            with open(tmp_filepath, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_filepath, filepath)
            logger.info(f"Successfully saved {filepath}")
        except Exception as e:
            logger.error(f"Failed atomic write to {filepath}", extra={"error_category": ErrorCategory.FILE_WRITE_ERROR.value}, exc_info=True)
            if os.path.exists(tmp_filepath):
                os.remove(tmp_filepath)
            raise

    def save(self, data: List[Dict[Any, Any]]):
        filepath = os.path.join(self.output_dir, "data.json")
        
        # Intelligent merge: preserve existing data and update/append new data
        merged_data_dict = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    for record in existing_data:
                        uid = record.get("unique_id")
                        if uid:
                            merged_data_dict[uid] = record
            except Exception:
                logger.warning(f"Failed to read existing data from {filepath}. Starting fresh.")
                
        # Incoming data overrides existing data with the same unique_id
        for record in data:
            uid = record.get("unique_id")
            if uid:
                merged_data_dict[uid] = record
                
        final_data = list(merged_data_dict.values())
        
        # Deterministic sorting
        sorted_data = sorted(final_data, key=lambda x: (x.get("unique_id", ""), x.get("last_updated", ""), x.get("source_url", "")))
        
        content = json.dumps(sorted_data, indent=2, ensure_ascii=False)
        
        # Idempotency check
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                old_content = f.read()
            if self._hash_content(old_content) == self._hash_content(content):
                logger.info(f"No changes detected for {filepath}. Skipping write.")
                return

        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        if is_dry_run:
            logger.info(f"DRY RUN: Would have saved {len(sorted_data)} records to {self.output_dir}")
            return

        self._atomic_write(filepath, content)

    def run(self):
        try:
            logger.info(f"Starting sync for {self.schema_name}")
            raw_data = self.fetch()
            transformed_data = self.transform(raw_data)
            valid_data = self.validate(transformed_data)
            self.save(valid_data)
            logger.info(f"Completed sync for {self.schema_name}")
            return len(valid_data)
        except Exception as e:
            logger.error(f"Sync failed for {self.schema_name}", exc_info=True)
            raise
