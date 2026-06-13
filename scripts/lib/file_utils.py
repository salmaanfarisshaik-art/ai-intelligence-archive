import os
import logging
from scripts.lib.logger import setup_logger, ErrorCategory

logger = setup_logger("file_utils")

def atomic_write(filepath: str, content: str, is_dry_run: bool = False):
    """
    Writes content to a file atomically by first writing to a temporary file
    and then replacing the target file.
    """
    if is_dry_run:
        logger.info(f"DRY RUN: Would have written atomically to {filepath}")
        return

    tmp_filepath = f"{filepath}.tmp"
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(tmp_filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Atomic replace
        os.replace(tmp_filepath, filepath)
        logger.debug(f"Successfully saved {filepath} atomically.")
    except Exception as e:
        logger.error(
            f"Failed atomic write to {filepath}",
            extra={"error_category": ErrorCategory.FILE_WRITE_ERROR.value},
            exc_info=True
        )
        if os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)
        raise
