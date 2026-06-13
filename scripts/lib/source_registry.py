import json
import os

class SourceRegistry:
    def __init__(self, registry_file: str = "sources/registry.json"):
        self.registry_file = registry_file
        self.sources = {}
        if os.path.exists(registry_file):
            with open(registry_file, "r", encoding="utf-8") as f:
                self.sources = json.load(f)

    def is_enabled(self, source: str) -> bool:
        src_conf = self.sources.get(source, {})
        return src_conf.get("enabled", False)

    def get_config(self, source: str) -> dict:
        return self.sources.get(source, {})
