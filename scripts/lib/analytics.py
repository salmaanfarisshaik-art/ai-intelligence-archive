import os
import json
from collections import defaultdict
from typing import Dict, Any

from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("analytics")

class AnalyticsGenerator:
    def __init__(self):
        self.metadata_dir = os.path.join("data", "metadata")
        self.reports_dir = "reports"
        os.makedirs(self.metadata_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        self.entity_index_path = os.path.join(self.metadata_dir, "entity_index.json")

    def _atomic_write(self, filepath: str, content: str):
        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        if is_dry_run:
            logger.info(f"DRY RUN: Would have saved analytics to {filepath}")
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

    def generate(self):
        if not config.is_feature_enabled("enable_analytics"):
            logger.info("Analytics generation is disabled in config.")
            return

        logger.info("Generating ecosystem analytics...")
        
        if not os.path.exists(self.entity_index_path):
            logger.warning(f"Cannot generate analytics. {self.entity_index_path} is missing.")
            return
            
        try:
            with open(self.entity_index_path, "r", encoding="utf-8") as f:
                entities = json.load(f)
                
            total_entities = len(entities)
            category_counts = defaultdict(int)
            source_counts = defaultdict(int)
            tag_counts = defaultdict(int)
            
            for entity in entities:
                cat = entity.get("category", "unknown")
                src = entity.get("source", "unknown")
                category_counts[cat] += 1
                source_counts[src] += 1
                
                for tag in entity.get("tags", []):
                    tag_counts[tag] += 1
                    
            # Sort maps
            category_distribution = {k: category_counts[k] for k in sorted(category_counts.keys(), key=lambda x: (-category_counts[x], x))}
            source_distribution = {k: source_counts[k] for k in sorted(source_counts.keys(), key=lambda x: (-source_counts[x], x))}
            
            # Top tags
            top_tags = sorted(tag_counts.keys(), key=lambda x: (-tag_counts[x], x))[:50]
            tag_distribution = {k: tag_counts[k] for k in top_tags}
            
            analytics_data = {
                "total_entities": total_entities,
                "category_distribution": category_distribution,
                "source_distribution": source_distribution,
                "top_tags": tag_distribution
            }
            
            self._atomic_write(
                os.path.join(self.metadata_dir, "analytics.json"),
                json.dumps(analytics_data, indent=2, ensure_ascii=False)
            )
            
            # Generate markdown report
            md_content = [
                "# AI Ecosystem Analytics",
                "",
                f"**Total Entities Tracked**: {total_entities}",
                "",
                "## Category Distribution",
                ""
            ]
            for cat, count in category_distribution.items():
                md_content.append(f"- **{cat}**: {count}")
                
            md_content.append("")
            md_content.append("## Source Distribution")
            md_content.append("")
            for src, count in source_distribution.items():
                md_content.append(f"- **{src}**: {count}")
                
            md_content.append("")
            md_content.append("## Top Tags")
            md_content.append("")
            for tag, count in tag_distribution.items():
                md_content.append(f"- **{tag}**: {count}")
                
            self._atomic_write(
                os.path.join(self.reports_dir, "analytics.md"),
                "\n".join(md_content) + "\n"
            )
            
            logger.info("Analytics generated successfully.")
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")

if __name__ == "__main__":
    AnalyticsGenerator().generate()
