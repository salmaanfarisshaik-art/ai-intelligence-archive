"""
Plugin Discovery — scans the plugins directory for plugin modules.
Discovered plugins are registered in the global PluginRegistry.
Discovery is sandboxed and failures never interrupt the pipeline.
"""
import os
import importlib
import inspect
from scripts.plugins.base_plugin import BasePlugin
from scripts.plugins.plugin_registry import plugin_registry
from scripts.lib.logger import setup_logger

logger = setup_logger("plugin_discovery")

PLUGINS_DIR = os.path.join("scripts", "plugins")


def discover_plugins(plugins_dir: str = PLUGINS_DIR) -> int:
    """
    Scan the plugins directory for Python modules containing BasePlugin subclasses.
    Returns the number of plugins discovered.
    """
    discovered = 0

    if not os.path.isdir(plugins_dir):
        logger.warning(f"Plugins directory not found: {plugins_dir}")
        return 0

    for filename in sorted(os.listdir(plugins_dir)):
        if not filename.endswith(".py"):
            continue
        if filename.startswith("__") or filename in ("base_plugin.py", "plugin_registry.py", "plugin_manager.py", "discovery.py"):
            continue

        module_name = f"scripts.plugins.{filename[:-3]}"

        try:
            module = importlib.import_module(module_name)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    plugin_registry.register(obj)
                    discovered += 1

        except Exception as e:
            logger.error(f"Failed to load plugin module {module_name}: {e}", exc_info=True)

    logger.info(f"Plugin discovery complete. {discovered} plugin(s) found.")
    return discovered
