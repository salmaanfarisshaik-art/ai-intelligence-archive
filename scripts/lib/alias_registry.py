import os
import json
from scripts.lib.logger import setup_logger
from scripts.lib.serialization import save_json_deterministic

logger = setup_logger("alias_registry")

class AliasRegistry:
    def __init__(self, registry_file: str = "data/metadata/alias_registry.json"):
        self.registry_file = registry_file
        self.aliases = {}
        self._load()

    def _load(self):
        if os.path.exists(self.registry_file):
            with open(self.registry_file, "r", encoding="utf-8") as f:
                self.aliases = json.load(f)
        else:
            logger.info(f"Alias registry {self.registry_file} not found. Starting fresh.")

    def resolve(self, alias: str) -> str:
        """
        Resolves an alias to its canonical entity ID.
        Returns the original string if no alias is found.
        """
        if not alias:
            return alias
        return self.aliases.get(alias.lower(), alias)

    def add_alias(self, alias: str, canonical_id: str):
        """
        Registers a new alias for a canonical ID.
        """
        if not alias or not canonical_id:
            return
            
        normalized_alias = alias.lower()
        if normalized_alias in self.aliases and self.aliases[normalized_alias] != canonical_id:
            logger.warning(f"Alias collision: '{normalized_alias}' is already mapped to {self.aliases[normalized_alias]}. Re-mapping to {canonical_id}.")
            
        self.aliases[normalized_alias] = canonical_id

    def save(self):
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        save_json_deterministic(self.registry_file, self.aliases)
        logger.debug(f"Alias registry saved to {self.registry_file}")
