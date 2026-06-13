import os
import json
import hashlib
import time
from typing import Any, Optional
from scripts.lib.logger import setup_logger

logger = setup_logger("cache_manager")

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _get_cache_path(self, source: str, key: str) -> str:
        safe_key = hashlib.md5(key.encode('utf-8')).hexdigest()
        source_dir = os.path.join(self.cache_dir, source)
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)
        return os.path.join(source_dir, f"{safe_key}.json")
            
    def get(self, source: str, key: str, ttl_seconds: int = 86400) -> Optional[Any]:
        path = self._get_cache_path(source, key)
        if not os.path.exists(path):
            return None
            
        # Check TTL
        file_age = time.time() - os.path.getmtime(path)
        if file_age > ttl_seconds:
            logger.debug(f"Cache expired for {source}:{key[:20]} (Age: {file_age:.1f}s > TTL: {ttl_seconds}s)")
            return None
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read cache {path}", exc_info=True)
            return None
            
    def set(self, source: str, key: str, data: Any):
        path = self._get_cache_path(source, key)
        try:
            tmp_path = f"{path}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            os.replace(tmp_path, path)
        except Exception as e:
            logger.warning(f"Failed to write cache {path}", exc_info=True)

    def clear(self):
        for root, dirs, files in os.walk(self.cache_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

# Global CacheManager instance
cache = CacheManager()
