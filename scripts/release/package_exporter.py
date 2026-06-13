"""
-------------------------------------------------------
THIS FILE IS AUTO-GENERATED.
DO NOT EDIT MANUALLY.
Changes may be overwritten during the next pipeline run.
-------------------------------------------------------

Package Exporter.
Compresses deterministic release bundles into archive formats (e.g. zip).
"""
import os
import shutil
from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("package_exporter")

class PackageExporter:
    def __init__(self):
        self.releases_dir = "releases"

    def export(self):
        if not config.is_feature_enabled("enable_release_builder"):
            return

        latest_release = os.path.join(self.releases_dir, "latest_release.json")
        if not os.path.exists(latest_release):
            return

        try:
            import json
            with open(latest_release, "r", encoding="utf-8") as f:
                meta = json.load(f)
            
            release_version = meta.get("release_version")
            if not release_version:
                return

            release_dir = os.path.join(self.releases_dir, release_version)
            if not os.path.exists(release_dir):
                return
            
            is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
            if is_dry_run:
                logger.info(f"DRY RUN: Would have archived {release_dir}")
                return

            archive_name = os.path.join(self.releases_dir, release_version)
            shutil.make_archive(archive_name, 'zip', release_dir)
            logger.info(f"Successfully created archive: {archive_name}.zip")

        except Exception as e:
            logger.error(f"Failed to export release package: {e}")

if __name__ == "__main__":
    PackageExporter().export()
