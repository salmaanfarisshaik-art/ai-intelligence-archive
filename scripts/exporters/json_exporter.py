import os
import json
from collections import defaultdict
from scripts.exporters.base_exporter import BaseExporter
from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("json_exporter")

class JSONExporter(BaseExporter):
    def __init__(self):
        super().__init__(os.path.join("exports", "json"))

    def export(self):
        if not config.is_feature_enabled("enable_export_generation"):
            logger.info("Export generation is disabled in config.")
            return
            
        logger.info("Generating JSON exports...")
        entities = self.load_entities()
        if not entities:
            return
            
        categories = defaultdict(list)
        for entity in entities:
            categories[entity.get("category", "unknown")].append(entity)
            
        for cat, items in categories.items():
            filepath = os.path.join(self.export_dir, f"{cat}.json")
            self._atomic_write(
                filepath,
                json.dumps(items, indent=2, ensure_ascii=False)
            )
            
        # Full export
        self._atomic_write(
            os.path.join(self.export_dir, "all_entities.json"),
            json.dumps(entities, indent=2, ensure_ascii=False)
        )
        
        logger.info("JSON exports generated successfully.")

if __name__ == "__main__":
    JSONExporter().export()
