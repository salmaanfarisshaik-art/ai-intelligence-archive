"""
Base Plugin abstract class for the AI Intelligence Archive.
Plugins operate exclusively through officially exposed extension points.
Plugins must never modify BaseSync behavior, alter synchronization ordering,
bypass validation, bypass deduplication, write directly to canonical data outputs,
or interfere with atomic persistence.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from scripts.lib.logger import setup_logger

logger = setup_logger("base_plugin")


class BasePlugin(ABC):
    """
    Abstract base class for all plugins.
    Plugins are sandboxed read-only consumers of the structured data lake.
    """
    
    plugin_name: str = "unnamed_plugin"
    plugin_version: str = "1.0.0"
    plugin_type: str = "generic"  # e.g., "exporter", "connector", "analytics", "ai_provider"

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration. Must not modify canonical data."""
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute the plugin logic.
        context contains read-only references to indexes and metadata.
        Must return results without mutating any canonical data.
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata for manifest generation."""
        return {
            "name": self.plugin_name,
            "version": self.plugin_version,
            "type": self.plugin_type,
        }
