import os
import json
from datetime import datetime, timezone
from scripts.lib.logger import setup_logger

logger = setup_logger("canonical_snapshot_manager")

class CanonicalSnapshotManager:
    """
    Manages cached upstream snapshots to ensure deterministic ingestion.
    Raw source snapshots are stored under approved cache locations.
    Normalization and expansion always operate against the stored snapshot.
    """
    def __init__(self, cache_dir: str = "data/cache/snapshots"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def store_snapshot(self, source_id: str, data: dict) -> str:
        """
        Stores a fresh snapshot from a live upstream source.
        Returns the path to the snapshot.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"{source_id}_{timestamp}.json"
        filepath = os.path.join(self.cache_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Stored canonical snapshot for {source_id} at {filepath}")
        
        # Also maintain a 'latest' symlink or just a file
        latest_path = os.path.join(self.cache_dir, f"{source_id}_latest.json")
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        return latest_path
        
    def get_latest_snapshot(self, source_id: str) -> dict:
        """
        Loads the latest canonical snapshot for ingestion to process deterministically.
        """
        latest_path = os.path.join(self.cache_dir, f"{source_id}_latest.json")
        if os.path.exists(latest_path):
            with open(latest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
