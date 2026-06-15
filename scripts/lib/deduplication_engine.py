import json
from scripts.lib.logger import setup_logger
from scripts.lib.alias_registry import AliasRegistry

logger = setup_logger("deduplication_engine")

class DeduplicationEngine:
    """
    Detects duplicates deterministically using explicit matching hierarchy:
    1. Existing canonical ID
    2. Normalized title + source
    3. Alias table
    (Semantic similarity future extension)
    """
    def __init__(self):
        self.alias_registry = AliasRegistry()
        self.seen_ids = set()
        self.seen_titles = set()
        
    def is_duplicate(self, schema: str, record: dict, source_id: str) -> bool:
        cid = record.get("unique_id")
        if not cid:
            return False
            
        # 1. Existing canonical ID (exact match)
        if cid in self.seen_ids:
            return True
            
        # 2. Alias table lookup
        resolved_id = self.alias_registry.resolve(cid)
        if resolved_id != cid and resolved_id in self.seen_ids:
            return True
            
        # 3. Normalized title + source (basic matching)
        title = record.get("name", record.get("title", ""))
        if title:
            title_key = f"{schema}_{source_id}_{title.lower()}"
            if title_key in self.seen_titles:
                return True
            self.seen_titles.add(title_key)
            
        self.seen_ids.add(cid)
        return False
