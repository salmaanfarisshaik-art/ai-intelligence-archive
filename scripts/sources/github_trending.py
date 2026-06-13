from typing import List, Dict, Any
from scripts.lib.api_client import api_client

class GitHubTrendingFetcher:
    def __init__(self, endpoint: str = "https://api.github.com/search/repositories"):
        self.endpoint = endpoint

    def fetch(self) -> List[Dict[Any, Any]]:
        # Fetch trending AI repos deterministically
        params = {"q": "topic:ai", "sort": "stars", "order": "desc", "per_page": 50}
        
        # GitHub requires User-Agent
        headers = {"User-Agent": "AI-Intelligence-Archive-Bot"}
        response = api_client.get("github_trending", self.endpoint, params=params, headers=headers)
        
        if not response or "items" not in response:
            return []
            
        return response["items"]
