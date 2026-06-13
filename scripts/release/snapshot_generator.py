"""
-------------------------------------------------------
THIS FILE IS AUTO-GENERATED.
DO NOT EDIT MANUALLY.
Changes may be overwritten during the next pipeline run.
-------------------------------------------------------

Snapshot & Versioning Layer.
Generates point-in-time snapshots of the structured data lake.
Snapshots are immutable artifacts representing historical repository state.
"""
import os
import json
import shutil
from datetime import datetime, timezone
from typing import Dict, Any

from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("snapshot_generator")


class SnapshotGenerator:
    """
    Creates immutable snapshots of canonical repository outputs.
    Never modifies existing artifacts in-place.
    """

    def __init__(self):
        self.snapshots_dir = "snapshots"
        self.metadata_dir = os.path.join("data", "metadata")
        self.processed_dir = os.path.join("data", "processed")
        os.makedirs(self.snapshots_dir, exist_ok=True)

    def generate(self):
        if not config.is_feature_enabled("enable_snapshot_generation"):
            logger.info("Snapshot generation disabled in config.")
            return

        logger.info("Generating repository snapshot...")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"snapshot_{timestamp}"
        snapshot_dir = os.path.join(self.snapshots_dir, snapshot_name)

        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        if is_dry_run:
            logger.info(f"DRY RUN: Would have created snapshot at {snapshot_dir}")
            return

        try:
            os.makedirs(snapshot_dir, exist_ok=True)
            
            # Copy canonical data (data.json files from processed)
            target_data_dir = os.path.join(snapshot_dir, "processed")
            os.makedirs(target_data_dir, exist_ok=True)
            
            if os.path.isdir(self.processed_dir):
                for cat in os.listdir(self.processed_dir):
                    cat_path = os.path.join(self.processed_dir, cat)
                    if os.path.isdir(cat_path):
                        data_file = os.path.join(cat_path, "data.json")
                        if os.path.exists(data_file):
                            target_cat_dir = os.path.join(target_data_dir, cat)
                            os.makedirs(target_cat_dir, exist_ok=True)
                            shutil.copy2(data_file, os.path.join(target_cat_dir, "data.json"))

            # Copy metadata indexes
            target_meta_dir = os.path.join(snapshot_dir, "metadata")
            os.makedirs(target_meta_dir, exist_ok=True)
            
            if os.path.isdir(self.metadata_dir):
                for meta_file in os.listdir(self.metadata_dir):
                    if meta_file.endswith(".json"):
                        shutil.copy2(
                            os.path.join(self.metadata_dir, meta_file),
                            os.path.join(target_meta_dir, meta_file)
                        )

            # Generate Snapshot Metadata
            meta = {
                "schema_version": "1.0",
                "snapshot_id": snapshot_name,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "contents": {
                    "processed_data": True,
                    "metadata_indexes": True
                }
            }
            with open(os.path.join(snapshot_dir, "snapshot_metadata.json"), "w", encoding="utf-8") as f:
                json.dumps(meta, f, indent=2, sort_keys=True, ensure_ascii=False)
                
            # Update latest_snapshot.json symlink/pointer
            pointer_path = os.path.join(self.snapshots_dir, "latest_snapshot.json")
            tmp_pointer = f"{pointer_path}.tmp"
            with open(tmp_pointer, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, sort_keys=True, ensure_ascii=False)
            os.replace(tmp_pointer, pointer_path)

            logger.info(f"Successfully generated snapshot: {snapshot_name}")

        except Exception as e:
            logger.error(f"Failed to generate snapshot {snapshot_name}: {e}")
            if os.path.exists(snapshot_dir):
                shutil.rmtree(snapshot_dir)


if __name__ == "__main__":
    SnapshotGenerator().generate()
