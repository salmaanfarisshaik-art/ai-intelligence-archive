import os
import yaml
from scripts.lib.logger import setup_logger

logger = setup_logger("config_loader")

class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.sources = {}
        self.categories = {}
        self.sync_pipeline = {}
        self.features = {}
        self.load_all()

    def _load_yaml(self, filename: str) -> dict:
        filepath = os.path.join(self.config_dir, filename)
        if not os.path.exists(filepath):
            logger.warning(f"Config file {filepath} not found.")
            return {}
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to parse {filepath}: {e}")
            return {}

    def load_all(self):
        # Load sources
        src_data = self._load_yaml("sources.yaml")
        for src in src_data.get("sources", []):
            self.sources[src["id"]] = src

        # Load categories
        cat_data = self._load_yaml("categories.yaml")
        for cat in cat_data.get("categories", []):
            self.categories[cat["id"]] = cat

        # Load sync pipeline configs and features
        sync_data = self._load_yaml("sync_config.yaml")
        self.sync_pipeline = sync_data.get("sync_pipeline", {})
        self.features = sync_data.get("features", {})
        
        # Merge settings.yaml if it exists (for backward compatibility)
        settings_data = self._load_yaml("settings.yaml")
        if "features" in settings_data:
            self.features.update(settings_data["features"])

    def is_sync_enabled(self, sync_name: str) -> bool:
        """Check if a specific sync module is enabled in the pipeline."""
        sync_cfg = self.sync_pipeline.get(sync_name, {})
        return sync_cfg.get("enabled", True)

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a specific phase 3 feature is enabled."""
        return self.features.get(feature_name, False)

# Global singleton
config = ConfigLoader()
