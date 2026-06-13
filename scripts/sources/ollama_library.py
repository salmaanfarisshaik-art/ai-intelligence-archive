from typing import List, Dict, Any
from scripts.lib.api_client import api_client

class OllamaLibraryFetcher:
    def __init__(self, endpoint: str = "https://ollama.com/api"):
        self.endpoint = endpoint

    def fetch(self) -> List[Dict[Any, Any]]:
        # Fetch local model metadata
        url = f"{self.endpoint}/tags"
        response = api_client.get("ollama", url)
        
        if not response or "models" not in response:
            return []
            
        return response["models"]
