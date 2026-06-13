import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from scripts.lib.api_client import api_client
from scripts.lib.logger import setup_logger

logger = setup_logger("arxiv_fetcher")

def fetch_arxiv_papers(max_results: int = 50) -> List[Dict[Any, Any]]:
    """Fetches latest AI/ML papers from ArXiv API."""
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": "cat:cs.AI OR cat:cs.CL OR cat:cs.CV",
        "sortBy": "lastUpdatedDate",
        "sortOrder": "descending",
        "max_results": max_results
    }
    
    response = api_client.get("arxiv", url, params=params, ttl_seconds=3600)
    
    raw_text = response.get("raw_text", "")
    if not raw_text:
        return []
        
    try:
        root = ET.fromstring(raw_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = []
        for entry in root.findall("atom:entry", ns):
            paper = {
                "id": entry.find("atom:id", ns).text if entry.find("atom:id", ns) is not None else "",
                "updated": entry.find("atom:updated", ns).text if entry.find("atom:updated", ns) is not None else "",
                "published": entry.find("atom:published", ns).text if entry.find("atom:published", ns) is not None else "",
                "title": entry.find("atom:title", ns).text if entry.find("atom:title", ns) is not None else "",
                "summary": entry.find("atom:summary", ns).text if entry.find("atom:summary", ns) is not None else "",
                "primary_category": "cs.AI" # default simplified
            }
            primary_cat = entry.find("{http://arxiv.org/schemas/atom}primary_category")
            if primary_cat is not None:
                paper["primary_category"] = primary_cat.attrib.get("term", "cs.AI")
            entries.append(paper)
        return entries
    except Exception as e:
        logger.error(f"Failed to parse ArXiv XML: {e}")
        return []
