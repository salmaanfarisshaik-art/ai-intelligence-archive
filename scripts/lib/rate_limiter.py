import time
import threading
from scripts.lib.logger import setup_logger

logger = setup_logger("rate_limiter")

class RateLimiter:
    """Sleep-based throttling per source to prevent hitting rate limits."""
    def __init__(self):
        self.source_delays = {
            "arxiv": 3.0,  # 3 seconds between arxiv requests (ArXiv standard)
            "huggingface": 1.0,
            "rss": 1.0
        }
        self.last_request_times = {}
        self.lock = threading.Lock()

    def wait(self, source: str):
        delay = self.source_delays.get(source, 1.0)
        
        with self.lock:
            now = time.time()
            last_time = self.last_request_times.get(source, 0)
            elapsed = now - last_time
            
            if elapsed < delay:
                sleep_time = delay - elapsed
                logger.debug(f"Rate limiting {source}. Sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
                
            self.last_request_times[source] = time.time()

# Global rate limiter instance
limiter = RateLimiter()
