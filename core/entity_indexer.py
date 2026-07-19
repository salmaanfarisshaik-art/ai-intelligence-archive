import os
import json
from collections import defaultdict
from typing import Dict, Any, List

from core.logger import setup_logger
from core.config_loader import config

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
        
        DOMAINS = ['skills', 'apis', 'benchmarks', 'datasets', 'ide_rules', 'mcps', 'models', 'news', 'prompts', 'tools']
        import glob
        
        for category_dir in DOMAINS:
            # category_dir acts like the domain
            json_files = glob.glob(f"{category_dir}/*/*.json")
            for data_file in json_files:
                try:
                    with open(data_file, "r", encoding="utf-8") as f:
                        record = json.load(f)
                    
                    # We process a single record instead of a list of records
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
                        "local_path": f"{data_file}"
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
