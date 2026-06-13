from typing import List, Dict, Any
from scripts.lib.api_client import api_client
from scripts.lib.logger import setup_logger

logger = setup_logger("huggingface_fetcher")

def fetch_hf_models(limit: int = 50) -> List[Dict[Any, Any]]:
    """Fetches latest popular text-generation models from Hugging Face."""
    url = "https://huggingface.co/api/models"
    params = {
        "filter": "text-generation",
        "sort": "downloads",
        "direction": "-1",
        "limit": limit
    }
    
    # TTL is 6 hours for HF
    response = api_client.get("huggingface", url, params=params, ttl_seconds=21600)
    
    # Since HF returns JSON list natively, api_client gives us a list directly
    if isinstance(response, list):
        return response
    elif isinstance(response, dict) and "raw_text" in response:
        # Just in case API format changed or parsing failed
        import json
        try:
            return json.loads(response["raw_text"])
        except json.JSONDecodeError:
            pass
            
    logger.warning("HuggingFace fetcher received unexpected format")
    return []
