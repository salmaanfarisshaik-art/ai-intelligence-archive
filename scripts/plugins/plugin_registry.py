"""
Plugin Registry — thread-safe singleton registry for discovered plugins.
Plugins are registered by type and name for deterministic lookup.
"""
from typing import Dict, List, Optional, Type
from scripts.plugins.base_plugin import BasePlugin
from scripts.lib.logger import setup_logger

logger = setup_logger("plugin_registry")


class PluginRegistry:
    """
    Central registry that holds all discovered and registered plugins.
    The registry is a metadata-only layer — it never executes plugins on its own.
    """

    def __init__(self):
        # Keyed by (plugin_type, plugin_name) for deterministic access
        self._plugins: Dict[str, Dict[str, Type[BasePlugin]]] = {}

    def register(self, plugin_cls: Type[BasePlugin]) -> None:
        """Register a plugin class. Duplicate names within a type are rejected."""
        ptype = getattr(plugin_cls, "plugin_type", "generic")
        pname = getattr(plugin_cls, "plugin_name", "unnamed")
        
        if ptype not in self._plugins:
            self._plugins[ptype] = {}
        
        if pname in self._plugins[ptype]:
            logger.warning(f"Plugin '{pname}' of type '{ptype}' is already registered. Skipping duplicate.")
            return
        
        self._plugins[ptype][pname] = plugin_cls
        logger.info(f"Registered plugin: {pname} (type={ptype})")

    def get_plugin(self, plugin_type: str, plugin_name: str) -> Optional[Type[BasePlugin]]:
        """Retrieve a specific plugin class by type and name."""
        return self._plugins.get(plugin_type, {}).get(plugin_name)

    def get_plugins_by_type(self, plugin_type: str) -> Dict[str, Type[BasePlugin]]:
        """Retrieve all plugins of a given type, deterministically sorted."""
        plugins = self._plugins.get(plugin_type, {})
        return dict(sorted(plugins.items()))

    def list_all(self) -> List[Dict[str, str]]:
        """Return a deterministically sorted list of all registered plugins."""
        result = []
        for ptype in sorted(self._plugins.keys()):
            for pname in sorted(self._plugins[ptype].keys()):
                result.append({
                    "type": ptype,
                    "name": pname,
                    "version": getattr(self._plugins[ptype][pname], "plugin_version", "unknown"),
                })
        return result


# Global singleton
plugin_registry = PluginRegistry()
