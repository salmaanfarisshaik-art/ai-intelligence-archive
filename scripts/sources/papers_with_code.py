from typing import List, Dict, Any
from scripts.lib.api_client import api_client

class PapersWithCodeFetcher:
    def __init__(self, endpoint: str = "https://paperswithcode.com/api/v1"):
        self.endpoint = endpoint

    def fetch(self) -> List[Dict[Any, Any]]:
        # Fetch top papers
        url = f"{self.endpoint}/papers/"
        response = api_client.get("papers_with_code", url, params={"page": 1, "items_per_page": 50})
        
        if not response or "results" not in response:
            return []
            
        return response["results"]
