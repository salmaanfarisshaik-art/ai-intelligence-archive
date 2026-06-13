import os
import json
from typing import List, Dict, Any

from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("search_index")

class SearchIndex:
    def __init__(self):
        self.metadata_dir = os.path.join("data", "metadata")
        self.site_dir = "site"
        os.makedirs(self.site_dir, exist_ok=True)
        self.entity_index_path = os.path.join(self.metadata_dir, "entity_index.json")

    def _atomic_write(self, filepath: str, content: str):
        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        if is_dry_run:
            logger.info(f"DRY RUN: Would have saved search index to {filepath}")
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

    def search(self, query: str, category: str = None, tag: str = None, exact: bool = False) -> List[Dict[Any, Any]]:
        """Lightweight search abstraction for local usage if needed."""
        if not os.path.exists(self.entity_index_path):
            logger.warning("Entity index not found for search.")
            return []
            
        with open(self.entity_index_path, "r", encoding="utf-8") as f:
            entities = json.load(f)
            
        results = []
        q_lower = query.lower() if query else ""
        
        for entity in entities:
            # Filters
            if category and entity.get("category") != category:
                continue
            if tag and tag not in entity.get("tags", []):
                continue
                
            # Query match
            if q_lower:
                title = entity.get("title", "").lower()
                source = entity.get("source", "").lower()
                id_val = entity.get("id", "").lower()
                
                if exact:
                    if q_lower not in [title, source, id_val]:
                        continue
                else:
                    if q_lower not in title and q_lower not in source and q_lower not in id_val:
                        # try tag match as fallback
                        tags_lower = [t.lower() for t in entity.get("tags", [])]
                        if not any(q_lower in t for t in tags_lower):
                            continue
                            
            results.append(entity)
            
        return results

    def generate(self):
        """Generates static JSON assets for the frontend portal."""
        if not config.is_feature_enabled("enable_search_indexing"):
            logger.info("Search indexing is disabled in config.")
            return

        logger.info("Generating search indexes for static portal...")
        
        if not os.path.exists(self.entity_index_path):
            logger.warning(f"Cannot generate search index. {self.entity_index_path} is missing.")
            return
            
        try:
            with open(self.entity_index_path, "r", encoding="utf-8") as f:
                entities = json.load(f)
                
            # 1. Search Index (Optimized for frontend consumption, removing unnecessary fields if any)
            search_index = []
            categories_set = set()
            for entity in entities:
                search_index.append({
                    "id": entity["id"],
                    "title": entity["title"],
                    "category": entity["category"],
                    "source": entity["source"],
                    "tags": entity["tags"],
                    "url": entity.get("source_url", "")
                })
                categories_set.add(entity["category"])
                
            self._atomic_write(
                os.path.join(self.site_dir, "search_index.json"),
                json.dumps(search_index, indent=2, ensure_ascii=False)
            )
            
            # 2. Site Index (Summary metadata for the portal home)
            site_index = {
                "total_entities": len(entities),
                "categories": sorted(list(categories_set)),
                "last_updated": os.getenv("CURRENT_TIMESTAMP", ""),
            }
            self._atomic_write(
                os.path.join(self.site_dir, "index.json"),
                json.dumps(site_index, indent=2, ensure_ascii=False)
            )
            
            # 3. Navigation
            navigation = {
                "main": [
                    {"label": "Home", "path": "/"},
                    {"label": "Search", "path": "/search"},
                ],
                "categories": [{"label": c.title().replace("_", " "), "path": f"/category/{c}"} for c in sorted(list(categories_set))]
            }
            self._atomic_write(
                os.path.join(self.site_dir, "navigation.json"),
                json.dumps(navigation, indent=2, ensure_ascii=False)
            )
            
            logger.info("Static portal search indexes generated successfully.")
        except Exception as e:
            logger.error(f"Error generating search index: {e}")

if __name__ == "__main__":
    SearchIndex().generate()
