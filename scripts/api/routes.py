"""
-------------------------------------------------------
THIS FILE IS AUTO-GENERATED.
DO NOT EDIT MANUALLY.
Changes may be overwritten during the next pipeline run.
-------------------------------------------------------

Local Knowledge API Routes.
Read-only convenience layer built on top of generated indexes.
Operates entirely via the deterministic QueryEngine.
"""
import json
from urllib.parse import urlparse, parse_qs
from scripts.lib.query_engine import QueryEngine
from scripts.lib.logger import setup_logger
from scripts.api.serializers import serialize_response

logger = setup_logger("api_routes")

# Lazy-loaded singleton
_query_engine = None

def _get_engine() -> QueryEngine:
    global _query_engine
    if _query_engine is None:
        _query_engine = QueryEngine()
    return _query_engine


def handle_request(path: str, query_params: dict) -> dict:
    """
    Route dispatcher for the read-only Knowledge API.
    Returns a dict that the server serializes to JSON.
    All operations are deterministic and read-only.
    """
    engine = _get_engine()

    if path == "/api/models":
        return engine.search(category="model", **_pagination_params(query_params))

    elif path == "/api/papers":
        return engine.search(category="paper", **_pagination_params(query_params))

    elif path == "/api/datasets":
        return engine.search(category="dataset", **_pagination_params(query_params))

    elif path == "/api/tools":
        return engine.search(category="tool", **_pagination_params(query_params))

    elif path == "/api/news":
        return engine.search(category="news", **_pagination_params(query_params))

    elif path == "/api/search":
        q = query_params.get("q", [""])[0]
        cat = query_params.get("category", [None])[0]
        t = query_params.get("tag", [None])[0]
        src = query_params.get("source", [None])[0]
        sort = query_params.get("sort_by", ["title"])[0]
        order = query_params.get("sort_order", ["asc"])[0]
        page = int(query_params.get("page", ["1"])[0])
        page_size = int(query_params.get("page_size", ["20"])[0])
        return engine.search(
            query=q, category=cat, tag=t, source=src,
            sort_by=sort, sort_order=order, page=page, page_size=page_size
        )

    elif path == "/api/categories":
        return engine.get_categories()

    elif path == "/api/tags":
        return engine.get_tags()

    elif path == "/api/analytics":
        return _load_json_file("data/metadata/analytics.json")

    elif path == "/api/graph":
        return _load_json_file("data/metadata/relationship_graph.json")

    elif path.startswith("/api/entity/"):
        entity_id = path[len("/api/entity/"):]
        result = engine.get_entity(entity_id)
        if result is None:
            return {"error": "Entity not found", "id": entity_id}
        return result

    else:
        return {"error": "Unknown endpoint", "path": path}


def _pagination_params(query_params: dict) -> dict:
    """Extract pagination parameters from query string."""
    return {
        "page": int(query_params.get("page", ["1"])[0]),
        "page_size": int(query_params.get("page_size", ["20"])[0]),
        "sort_by": query_params.get("sort_by", ["title"])[0],
        "sort_order": query_params.get("sort_order", ["asc"])[0],
    }


def _load_json_file(filepath: str) -> dict:
    """Load a JSON file. Read-only convenience helper."""
    import os
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")
        return {"error": str(e)}
