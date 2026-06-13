import os
from collections import defaultdict
from scripts.exporters.base_exporter import BaseExporter
from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("markdown_exporter")

class MarkdownExporter(BaseExporter):
    def __init__(self):
        super().__init__(os.path.join("exports", "markdown"))

    def export(self):
        if not config.is_feature_enabled("enable_export_generation"):
            logger.info("Export generation is disabled in config.")
            return
            
        logger.info("Generating Markdown exports...")
        entities = self.load_entities()
        if not entities:
            return
            
        categories = defaultdict(list)
        for entity in entities:
            categories[entity.get("category", "unknown")].append(entity)
            
        for cat, items in categories.items():
            filepath = os.path.join(self.export_dir, f"{cat}.md")
            
            md_lines = [f"# {cat.title().replace('_', ' ')} Export", ""]
            
            for item in items:
                md_lines.append(f"## {item.get('title', 'Unknown')}")
                md_lines.append(f"- **ID**: {item.get('id')}")
                md_lines.append(f"- **Source**: {item.get('source')}")
                if item.get('source_url'):
                    md_lines.append(f"- **URL**: [{item.get('source_url')}]({item.get('source_url')})")
                if item.get('tags'):
                    md_lines.append(f"- **Tags**: {', '.join(item.get('tags'))}")
                md_lines.append("")
                
            self._atomic_write(filepath, "\n".join(md_lines) + "\n")
            
        logger.info("Markdown exports generated successfully.")

if __name__ == "__main__":
    MarkdownExporter().export()
