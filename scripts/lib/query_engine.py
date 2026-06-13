import os
import json
from typing import List, Dict, Any, Optional
from scripts.lib.logger import setup_logger

logger = setup_logger("query_engine")

class QueryEngine:
    """
    Deterministic Query Engine for Phase 5.
    Operates strictly as a read-only consumer of generated metadata indexes.
    All sorting and ranking must be deterministic.
    """
    def __init__(self, metadata_dir: str = "data/metadata"):
        self.metadata_dir = metadata_dir
        
        # entity_index.json is a list of objects with "id" as the key field
        raw_entities = self._load_json("entity_index.json")
        if isinstance(raw_entities, list):
            self.entity_index = {e.get("id", ""): e for e in raw_entities}
        else:
            self.entity_index = raw_entities
        
        self.category_index = self._load_json("category_index.json")
        self.tag_index = self._load_json("tag_index.json")
        
        # Load relationship graph if available
        self.relationship_graph = self._load_json("relationship_graph.json")

    def _load_json(self, filename: str):
        filepath = os.path.join(self.metadata_dir, filename)
        if not os.path.exists(filepath):
            logger.warning(f"Metadata file {filename} not found.")
            return {}
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to parse {filename}: {e}")
            return {}

    def get_entity(self, unique_id: str) -> Optional[Dict[str, Any]]:
        """Exact lookup by unique_id."""
        return self.entity_index.get(unique_id)

    def search(
        self,
        query: str = "",
        category: Optional[str] = None,
        tag: Optional[str] = None,
        source: Optional[str] = None,
        sort_by: str = "title",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Deterministic search.
        Given identical indexes and identical query parameters, this always produces identical ordered results.
        Search ranking does not depend on AI scores or volatile data.
        """
        results = []
        query_normalized = query.lower().strip()

        for unique_id, entity in self.entity_index.items():
            # Filters
            if category and entity.get("category") != category:
                continue
            if source and entity.get("source") != source:
                continue
            if tag and tag not in entity.get("tags", []):
                continue
            
            # Text Match
            if query_normalized:
                title = entity.get("title", "").lower()
                desc = entity.get("description", "").lower()
                # Exact or substring match in title/description
                if query_normalized not in title and query_normalized not in desc:
                    continue
            
            results.append(entity)

        # Deterministic sorting
        # Supported sort_by: "title", "date_added", "unique_id"
        reverse = (sort_order == "desc")
        
        if sort_by == "title":
            results.sort(key=lambda x: (x.get("title", "").lower(), x.get("unique_id", "")), reverse=reverse)
        elif sort_by == "date_added":
            results.sort(key=lambda x: (x.get("retrieved_at", ""), x.get("unique_id", "")), reverse=reverse)
        else:
            # Default to unique_id to guarantee determinism
            results.sort(key=lambda x: x.get("unique_id", ""), reverse=reverse)

        # Pagination
        total = len(results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated = results[start_idx:end_idx]

        return {
            "query": query,
            "filters": {
                "category": category,
                "tag": tag,
                "source": source
            },
            "total_results": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
            "results": paginated
        }

    def get_related(self, unique_id: str) -> List[Dict[str, Any]]:
        """Traverse relationship graph deterministically."""
        related_ids = []
        edges = self.relationship_graph.get("edges", [])
        
        for edge in edges:
            if edge.get("source") == unique_id:
                related_ids.append(edge.get("target"))
            elif edge.get("target") == unique_id:
                related_ids.append(edge.get("source"))

        # Deterministic sorting of IDs
        related_ids = sorted(list(set(related_ids)))
        
        results = []
        for rid in related_ids:
            ent = self.get_entity(rid)
            if ent:
                results.append(ent)
                
        return results

    def get_categories(self) -> Dict[str, Any]:
        """Return deterministic category breakdown."""
        return self.category_index

    def get_tags(self) -> Dict[str, Any]:
        """Return deterministic tag breakdown."""
        return self.tag_index
