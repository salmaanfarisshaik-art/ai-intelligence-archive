import os
import json
from collections import defaultdict
from typing import Dict, Any, List

from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("entity_indexer")

class EntityIndexer:
    def __init__(self):
        self.processed_dir = os.path.join("data", "processed")
        self.metadata_dir = os.path.join("data", "metadata")
        os.makedirs(self.metadata_dir, exist_ok=True)

    def _atomic_write(self, filepath: str, content: str):
        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        if is_dry_run:
            logger.info(f"DRY RUN: Would have saved index to {filepath}")
            return
            
        tmp_filepath = f"{filepath}.tmp"
        try:
            with open(tmp_filepath, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_filepath, filepath)
            logger.info(f"Successfully saved index {filepath}")
        except Exception as e:
            logger.error(f"Failed atomic write to {filepath}: {e}")
            if os.path.exists(tmp_filepath):
                os.remove(tmp_filepath)

    def generate(self):
        if not config.is_feature_enabled("enable_entity_indexing"):
            logger.info("Entity indexing is disabled in config.")
            return

        logger.info("Generating entity indexes...")
        
        entity_index = []
        category_index = defaultdict(list)
        tag_index = defaultdict(list)
        
        for category_dir in os.listdir(self.processed_dir):
            category_path = os.path.join(self.processed_dir, category_dir)
            if not os.path.isdir(category_path):
                continue
                
            data_file = os.path.join(category_path, "data.json")
            if not os.path.exists(data_file):
                continue
                
            try:
                with open(data_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
                    
                for record in records:
                    unique_id = record.get("unique_id", "")
                    title = record.get("name", "")
                    category = record.get("category", category_dir)
                    source_name = record.get("source_name", "")
                    source_url = record.get("source_url", "")
                    
                    # Extract tags
                    tags = []
                    if "ai_tags" in record:
                        tags.extend(record["ai_tags"])
                    
                    # In some schemas, tags might be in raw_payload or other fields
                    raw_payload = record.get("raw_payload", {})
                    if isinstance(raw_payload, dict) and "tags" in raw_payload:
                        raw_tags = raw_payload["tags"]
                        if isinstance(raw_tags, list):
                            tags.extend([str(t) for t in raw_tags])
                            
                    tags = sorted(list(set(tags)))
                    
                    # Extract links
                    links = record.get("links", {})
                    
                    entry = {
                        "id": unique_id,
                        "title": title,
                        "category": category,
                        "source": source_name,
                        "tags": tags,
                        "links": links,
                        "source_url": source_url,
                        "local_path": f"data/processed/{category_dir}/data.json#{unique_id}"
                    }
                    
                    entity_index.append(entry)
                    category_index[category].append(unique_id)
                    for tag in tags:
                        tag_index[tag].append(unique_id)
                        
            except Exception as e:
                logger.error(f"Error reading {data_file}: {e}")
                
        # Deterministic sorting
        entity_index = sorted(entity_index, key=lambda x: x["id"])
        
        # Sort internal lists deterministically
        for cat in category_index:
            category_index[cat] = sorted(list(set(category_index[cat])))
            
        for tag in tag_index:
            tag_index[tag] = sorted(list(set(tag_index[tag])))
            
        # Sort dictionaries deterministically
        category_index_sorted = {k: category_index[k] for k in sorted(category_index.keys())}
        tag_index_sorted = {k: tag_index[k] for k in sorted(tag_index.keys())}
        
        self._atomic_write(
            os.path.join(self.metadata_dir, "entity_index.json"),
            json.dumps(entity_index, indent=2, ensure_ascii=False)
        )
        
        self._atomic_write(
            os.path.join(self.metadata_dir, "category_index.json"),
            json.dumps(category_index_sorted, indent=2, ensure_ascii=False)
        )
        
        self._atomic_write(
            os.path.join(self.metadata_dir, "tag_index.json"),
            json.dumps(tag_index_sorted, indent=2, ensure_ascii=False)
        )
        logger.info("Entity indexes generated successfully.")

if __name__ == "__main__":
    EntityIndexer().generate()
