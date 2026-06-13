"""
Plugin Manager — orchestrates plugin execution in isolated error boundaries.
Plugin failures are logged but never interrupt the main pipeline.
"""
from typing import Dict, Any, List
from scripts.plugins.plugin_registry import plugin_registry
from scripts.plugins.base_plugin import BasePlugin
from scripts.lib.logger import setup_logger

logger = setup_logger("plugin_manager")


class PluginManager:
    """
    Executes registered plugins in deterministic order.
    Each plugin runs inside its own try-except isolation block.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def execute_all(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute all registered plugins deterministically.
        Returns a list of execution results/statuses.
        """
        results = []
        all_plugins = plugin_registry.list_all()

        for plugin_meta in all_plugins:
            ptype = plugin_meta["type"]
            pname = plugin_meta["name"]
            
            plugin_cls = plugin_registry.get_plugin(ptype, pname)
            if plugin_cls is None:
                continue

            try:
                logger.info(f"Executing plugin: {pname} (type={ptype})")
                instance = plugin_cls()
                instance.initialize(self.config)
                result = instance.execute(context)
                results.append({
                    "plugin": pname,
                    "type": ptype,
                    "status": "success",
                    "result": result,
                })
                logger.info(f"Plugin {pname} completed successfully.")
            except Exception as e:
                logger.error(f"Plugin {pname} failed: {e}", exc_info=True)
                results.append({
                    "plugin": pname,
                    "type": ptype,
                    "status": "failed",
                    "error": str(e),
                })

        return results

    def execute_by_type(self, plugin_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute all plugins of a specific type."""
        results = []
        plugins = plugin_registry.get_plugins_by_type(plugin_type)

        for pname, plugin_cls in plugins.items():
            try:
                logger.info(f"Executing plugin: {pname} (type={plugin_type})")
                instance = plugin_cls()
                instance.initialize(self.config)
                result = instance.execute(context)
                results.append({
                    "plugin": pname,
                    "type": plugin_type,
                    "status": "success",
                    "result": result,
                })
            except Exception as e:
                logger.error(f"Plugin {pname} failed: {e}", exc_info=True)
                results.append({
                    "plugin": pname,
                    "type": plugin_type,
                    "status": "failed",
                    "error": str(e),
                })

        return results
