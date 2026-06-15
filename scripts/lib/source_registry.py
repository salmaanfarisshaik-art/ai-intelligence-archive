import json
import os
from scripts.lib.serialization import save_json_deterministic
from scripts.lib.logger import setup_logger

logger = setup_logger("source_registry")

class SourceRegistry:
    def __init__(self, registry_file: str = "data/metadata/source_registry.json"):
        self.registry_file = registry_file
        self.sources = {}
        self._load()

    def _load(self):
        if os.path.exists(self.registry_file):
            with open(self.registry_file, "r", encoding="utf-8") as f:
                self.sources = json.load(f)
        else:
            logger.warning(f"Source registry {self.registry_file} not found. Starting fresh.")

    def is_enabled(self, source_id: str) -> bool:
        src_conf = self.sources.get(source_id, {})
        return src_conf.get("enabled", False)

    def get_config(self, source_id: str) -> dict:
        return self.sources.get(source_id, {})
        
    def get_all_sources(self) -> dict:
        return self.sources
        
    def get_enabled_sources(self) -> dict:
        return {k: v for k, v in self.sources.items() if v.get("enabled", False)}

    def update_source(self, source_id: str, data: dict):
        """
        Updates a source in the registry. 
        Note: Only SourceValidator and administrative workflows should modify this.
        """
        if source_id not in self.sources:
            self.sources[source_id] = {}
        self.sources[source_id].update(data)
        
    def disable_source(self, source_id: str, reason: str):
        if source_id in self.sources:
            self.sources[source_id]["enabled"] = False
            self.sources[source_id]["disabled_reason"] = reason
            logger.info(f"Source {source_id} disabled: {reason}")
            
    def save(self):
        """Serialize registry updates deterministically."""
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        save_json_deterministic(self.registry_file, self.sources)
        logger.debug(f"Source registry saved to {self.registry_file}")
