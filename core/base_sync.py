import json
import os
import hashlib
from typing import List, Dict, Any
from core.logger import setup_logger, ErrorCategory
from core.validator import RecordValidator

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

    def _hash_record(self, content: str) -> str:
        record = json.loads(content)
        record.pop("last_updated", None)
        record.pop("retrieval_timestamp", None)
        return hashlib.sha256(json.dumps(record, sort_keys=True).encode("utf-8")).hexdigest()

    def _get_organization(self, record: dict) -> str:
        import re
        name = record.get("name", "")
        if "/" in name:
            org = name.split("/")[0].strip()
            if org:
                org = str(org).strip().lower()
                org = re.sub(r'[^\w\s-]', '', org)
                return re.sub(r'[-\s]+', '-', org)
        
        source_name = record.get("source_name", "unknown")
        if source_name:
            org = str(source_name).strip().lower()
            org = re.sub(r'[^\w\s-]', '', org)
            return re.sub(r'[-\s]+', '-', org)
            
        return "unknown"
        
    def _get_filename(self, record: dict) -> str:
        import re
        uid = record.get("unique_id", "unknown")
        uid = re.sub(r'[<>:"/\\|?*]', '_', str(uid))
        return f"{uid}.json"

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
        saved_count = 0
        for record in data:
            org = self._get_organization(record)
            filename = self._get_filename(record)
            target_dir = os.path.join(self.output_dir, org)
            os.makedirs(target_dir, exist_ok=True)
            filepath = os.path.join(target_dir, filename)
            
            content = json.dumps(record, indent=2, ensure_ascii=False)
            
            # Idempotency check
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    old_content = f.read()
                if self._hash_record(old_content) == self._hash_record(content):
                    continue
                    
            is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
            if is_dry_run:
                saved_count += 1
                continue
                
            self._atomic_write(filepath, content)
            saved_count += 1
            
        if saved_count > 0:
            logger.info(f"Saved {saved_count} new/updated records to {self.output_dir}")

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
