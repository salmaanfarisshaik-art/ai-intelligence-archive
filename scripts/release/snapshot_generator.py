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

from core.logger import setup_logger
from core.config_loader import config

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
            
            DOMAINS = ['skills', 'apis', 'benchmarks', 'datasets', 'ide_rules', 'mcps', 'models', 'news', 'prompts', 'tools']
            
            # Copy canonical data (sharded json files from domains)
            target_data_dir = os.path.join(snapshot_dir, "processed")
            os.makedirs(target_data_dir, exist_ok=True)
            
            for domain in DOMAINS:
                if os.path.isdir(domain):
                    target_domain_dir = os.path.join(target_data_dir, domain)
                    os.makedirs(target_domain_dir, exist_ok=True)
                    # We copy everything in the domain EXCEPT python files or readmes.
                    # Actually, we can just use shutil.copytree but ignore .py and .md files.
                    def ignore_files(dir_name, files):
                        return [f for f in files if f.endswith('.py') or f.endswith('.md') or f == '__pycache__']
                        
                    # shutil.copytree requires the destination directory to not exist,
                    # but we already created it. So we copy to a temp dir then move or copy contents.
                    # Or simpler:
                    import glob
                    json_files = glob.glob(f"{domain}/*/*.json")
                    for jf in json_files:
                        # jf looks like models/openai/model.json
                        # target should be snapshot/processed/models/openai/model.json
                        rel_path = os.path.relpath(jf, domain)
                        target_path = os.path.join(target_domain_dir, rel_path)
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        shutil.copy2(jf, target_path)

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
