import os
import json
from typing import List, Dict, Any
from scripts.lib.logger import setup_logger

logger = setup_logger("base_exporter")

class BaseExporter:
    def __init__(self, export_dir: str):
        self.export_dir = export_dir
        self.metadata_dir = os.path.join("data", "metadata")
        self.entity_index_path = os.path.join(self.metadata_dir, "entity_index.json")
        os.makedirs(self.export_dir, exist_ok=True)

    def _atomic_write(self, filepath: str, content: str):
        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        if is_dry_run:
            logger.info(f"DRY RUN: Would have saved export to {filepath}")
            return
            
        tmp_filepath = f"{filepath}.tmp"
        try:
            with open(tmp_filepath, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_filepath, filepath)
            logger.info(f"Successfully saved {filepath}")
        except Exception as e:
            logger.error(f"Failed atomic write to {filepath}: {e}")
            if os.path.exists(tmp_filepath):
                os.remove(tmp_filepath)

    def load_entities(self) -> List[Dict[Any, Any]]:
        if not os.path.exists(self.entity_index_path):
            logger.warning(f"Cannot load entities. {self.entity_index_path} is missing.")
            return []
            
        try:
            with open(self.entity_index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading entity index: {e}")
            return []

    def export(self):
        raise NotImplementedError
