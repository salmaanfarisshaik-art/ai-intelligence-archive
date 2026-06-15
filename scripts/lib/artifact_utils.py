import os
import json
import shutil
import tempfile
from typing import Any, Dict, Optional
import jsonschema

from scripts.lib.logger import setup_logger

logger = setup_logger("artifact_utils")

def validate_json_schema(data: Any, schema_path: str) -> bool:
    """
    Validates data against a JSON schema stored in schemas/.
    """
    if not os.path.exists(schema_path):
        logger.error(f"Schema not found at {schema_path}")
        return False
        
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        jsonschema.validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Validation error against {schema_path}: {e.message}")
        return False
    except Exception as e:
        logger.error(f"Failed to load or validate schema {schema_path}: {e}")
        return False

def atomic_write_json_artifact(filepath: str, data: Any, schema_path: Optional[str] = None, is_dry_run: bool = False) -> bool:
    """
    Atomically writes a JSON artifact after optional schema validation.
    """
    if schema_path:
        if not validate_json_schema(data, schema_path):
            logger.error(f"Refusing to write {filepath} due to schema validation failure.")
            return False

    if is_dry_run:
        logger.info(f"DRY RUN: Would have written {filepath} atomically")
        return True

    # Use a secure temp file in the same directory or a temp dir
    target_dir = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(target_dir, exist_ok=True)
    
    # We use a temp file to guarantee atomic replacement
    fd, temp_path = tempfile.mkstemp(dir=target_dir, prefix="tmp_artifact_", suffix=".json")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write("\n") # Trailing newline
            
        os.replace(temp_path, filepath)
        logger.info(f"Successfully wrote {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to write artifact {filepath}", exc_info=True)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def atomic_directory_swap(target_dir: str, source_dir: str, is_dry_run: bool = False) -> bool:
    """
    Atomically swaps a fully generated temporary directory into the target directory.
    Useful for multi-file artifacts like site/search/*.
    """
    if is_dry_run:
        logger.info(f"DRY RUN: Would have atomically swapped {source_dir} -> {target_dir}")
        return True
        
    try:
        parent_dir = os.path.dirname(os.path.abspath(target_dir))
        os.makedirs(parent_dir, exist_ok=True)
        
        # If target doesn't exist, simple rename
        if not os.path.exists(target_dir):
            os.rename(source_dir, target_dir)
            return True
            
        # If it exists, we move it to a backup, rename the new one, then delete backup
        backup_dir = f"{target_dir}.bak"
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
            
        os.rename(target_dir, backup_dir)
        os.rename(source_dir, target_dir)
        shutil.rmtree(backup_dir)
        logger.info(f"Successfully swapped directory {target_dir}")
        return True
    except Exception as e:
        logger.error(f"Failed to swap directory {target_dir}", exc_info=True)
        return False
