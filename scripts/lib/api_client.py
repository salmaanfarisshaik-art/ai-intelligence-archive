import requests
import json
from scripts.lib.logger import setup_logger, ErrorCategory
from scripts.lib.rate_limiter import limiter
from scripts.lib.cache_manager import cache
from scripts.lib.source_metrics import metrics
from scripts.lib.retry import with_retry
from scripts.lib.api_exceptions import APIError, APITimeoutError, APIRateLimitError

logger = setup_logger("api_client")

class APIClient:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def _generate_cache_key(self, url: str, params: dict) -> str:
        if not params:
            return url
        param_str = json.dumps(params, sort_keys=True)
        return f"{url}_{param_str}"

    @with_retry(max_retries=3, max_seconds=30)
    def _make_request(self, method: str, source_id: str, url: str, **kwargs) -> dict:
        limiter.wait(source_id)
        metrics.record_api_call()
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            if response.status_code == 429:
                logger.warning(f"Rate limited by {source_id} on {url}")
                raise APIRateLimitError(f"429 Rate Limit from {source_id}")
            response.raise_for_status()
            
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            else:
                # E.g. RSS feeds return XML
                return {"raw_text": response.text}
                
        except requests.exceptions.Timeout:
            raise APITimeoutError(f"Timeout connecting to {url}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"HTTP request failed: {e}")

    def get(self, source_id: str, url: str, params: dict = None, headers: dict = None, ttl_seconds: int = 86400) -> dict:
        cache_key = self._generate_cache_key(url, params)
        cached_response = cache.get(source_id, cache_key, ttl_seconds=ttl_seconds)
        
        if cached_response is not None:
            logger.debug(f"Cache hit for {source_id}: {url}")
            metrics.record_cache_hit()
            return cached_response
            
        metrics.record_cache_miss()
        logger.info(f"Fetching from {source_id}: {url}")
        
        try:
            response_data = self._make_request("GET", source_id, url, params=params, headers=headers)
            cache.set(source_id, cache_key, response_data)
            return response_data
        except Exception as e:
            logger.error(f"API get failed for {source_id}", extra={"error_category": ErrorCategory.NETWORK_ERROR.value}, exc_info=True)
            metrics.record_source_failure(source_id)
            # Graceful fallback: Check if we have ANY expired cache for this to return as fallback
            stale_response = cache.get(source_id, cache_key, ttl_seconds=9999999)
            if stale_response is not None:
                logger.warning(f"Falling back to stale cache for {source_id}")
                return stale_response
            raise

api_client = APIClient()
