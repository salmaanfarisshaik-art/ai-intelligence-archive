class APIError(Exception):
    """Base exception for API errors."""
    pass

class APIRateLimitError(APIError):
    """Raised when rate limits are exceeded and retries are exhausted."""
    pass

class APITimeoutError(APIError):
    """Raised when an API request times out repeatedly."""
    pass

class APIConnectionError(APIError):
    """Raised when connection fails."""
    pass
