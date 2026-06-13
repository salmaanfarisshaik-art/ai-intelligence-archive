from typing import List, Dict, Any
from scripts.lib.api_client import api_client

class HFDatasetsFetcher:
    def __init__(self, endpoint: str = "https://huggingface.co/api/datasets"):
        self.endpoint = endpoint

    def fetch(self) -> List[Dict[Any, Any]]:
        # Fetch top datasets deterministically
        params = {"sort": "downloads", "direction": "-1", "limit": 100}
        response = api_client.get("huggingface_datasets", self.endpoint, params=params)
        
        if not response:
            return []
            
        return response
