import json
import logging
import os
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

class ErrorCategory(Enum):
    API_ERROR = "API_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    FILE_WRITE_ERROR = "FILE_WRITE_ERROR"
    SCHEMA_ERROR = "SCHEMA_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "error_category"):
            log_record["error_category"] = record.error_category # type: ignore
        if record.exc_info:
            log_record["stacktrace"] = self.formatException(record.exc_info)
        
        # Add extra fields if passed
        if hasattr(record, "extra_fields"):
            log_record.update(record.extra_fields) # type: ignore
            
        return json.dumps(log_record)

def setup_logger(name: str, log_file: str = "logs/sync.log") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JsonFormatter())
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger
