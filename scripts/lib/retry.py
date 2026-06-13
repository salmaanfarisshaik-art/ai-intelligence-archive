import time
from functools import wraps
from typing import Callable, Any
from scripts.lib.logger import setup_logger, ErrorCategory

logger = setup_logger("retry")

def with_retry(max_retries: int = 5, max_seconds: int = 60) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            backoff = 1
            total_waited = 0
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if retries == max_retries or total_waited >= max_seconds:
                        logger.error(
                            f"Max retries reached or time limit exceeded for {func.__name__}",
                            extra={"error_category": ErrorCategory.NETWORK_ERROR.value},
                            exc_info=True
                        )
                        raise
                    
                    wait_time = min(backoff, max_seconds - total_waited)
                    logger.warning(
                        f"Retry {retries + 1}/{max_retries} for {func.__name__} after {wait_time}s",
                        extra={"error_category": ErrorCategory.NETWORK_ERROR.value}
                    )
                    time.sleep(wait_time)
                    total_waited += wait_time
                    backoff *= 2
                    retries += 1
            return None
        return wrapper
    return decorator
