"""
-------------------------------------------------------
THIS FILE IS AUTO-GENERATED.
DO NOT EDIT MANUALLY.
Changes may be overwritten during the next pipeline run.
-------------------------------------------------------

Release Builder.
Packages all derived assets into deterministic release bundles.
"""
import os
import json
import shutil
from datetime import datetime, timezone

from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config
from scripts.release.changelog_generator import ChangelogGenerator

logger = setup_logger("release_builder")


class ReleaseBuilder:
    """Builds deterministic release packages from canonical outputs."""

    def __init__(self):
        self.releases_dir = "releases"
        os.makedirs(self.releases_dir, exist_ok=True)

    def generate(self):
        if not config.is_feature_enabled("enable_release_builder"):
            logger.info("Release builder disabled in config.")
            return

        logger.info("Building release package...")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        release_version = f"v{datetime.now(timezone.utc).strftime('%Y.%m.%d')}.{timestamp}"
        release_dir = os.path.join(self.releases_dir, release_version)

        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        if is_dry_run:
            logger.info(f"DRY RUN: Would have built release at {release_dir}")
            return

        try:
            os.makedirs(release_dir, exist_ok=True)

            # Generate Changelog
            changelog_content = ChangelogGenerator().generate(release_version)
            with open(os.path.join(release_dir, "CHANGELOG.md"), "w", encoding="utf-8") as f:
                f.write(changelog_content)

            # Generate Release Manifest
            manifest = {
                "schema_version": "1.0",
                "release_version": release_version,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "contents": {
                    "changelog": "CHANGELOG.md"
                }
            }
            with open(os.path.join(release_dir, "release_manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, sort_keys=True, ensure_ascii=False)

            # Package exports if available
            exports_dir = "exports"
            if os.path.isdir(exports_dir):
                target_exports = os.path.join(release_dir, "exports")
                shutil.copytree(exports_dir, target_exports, dirs_exist_ok=True)

            # Update latest_release.json symlink/pointer atomically
            pointer_path = os.path.join(self.releases_dir, "latest_release.json")
            tmp_pointer = f"{pointer_path}.tmp"
            with open(tmp_pointer, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, sort_keys=True, ensure_ascii=False)
            os.replace(tmp_pointer, pointer_path)
            
            # Also write generated changelog to root releases/CHANGELOG.generated.md
            changelog_pointer = os.path.join(self.releases_dir, "CHANGELOG.generated.md")
            tmp_changelog = f"{changelog_pointer}.tmp"
            with open(tmp_changelog, "w", encoding="utf-8") as f:
                f.write(changelog_content)
            os.replace(tmp_changelog, changelog_pointer)

            logger.info(f"Successfully built release: {release_version}")

        except Exception as e:
            logger.error(f"Failed to build release {release_version}: {e}")
            if os.path.exists(release_dir):
                shutil.rmtree(release_dir)


if __name__ == "__main__":
    ReleaseBuilder().generate()
