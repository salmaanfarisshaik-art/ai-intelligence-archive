import os
import csv
import io
from collections import defaultdict
from scripts.exporters.base_exporter import BaseExporter
from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("csv_exporter")

class CSVExporter(BaseExporter):
    def __init__(self):
        super().__init__(os.path.join("exports", "csv"))

    def export(self):
        if not config.is_feature_enabled("enable_export_generation"):
            logger.info("Export generation is disabled in config.")
            return
            
        logger.info("Generating CSV exports...")
        entities = self.load_entities()
        if not entities:
            return
            
        categories = defaultdict(list)
        for entity in entities:
            categories[entity.get("category", "unknown")].append(entity)
            
        fieldnames = ["id", "title", "category", "source", "tags", "source_url"]
            
        for cat, items in categories.items():
            filepath = os.path.join(self.export_dir, f"{cat}.csv")
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for item in items:
                row = item.copy()
                row["tags"] = "|".join(row.get("tags", []))
                writer.writerow(row)
                
            self._atomic_write(filepath, output.getvalue())
            
        # Full export
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for item in entities:
            row = item.copy()
            row["tags"] = "|".join(row.get("tags", []))
            writer.writerow(row)
            
        self._atomic_write(
            os.path.join(self.export_dir, "all_entities.csv"),
            output.getvalue()
        )
        
        logger.info("CSV exports generated successfully.")

if __name__ == "__main__":
    CSVExporter().export()
