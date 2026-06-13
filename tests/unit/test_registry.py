import pytest
from scripts.lib.source_registry import SourceRegistry

def test_source_registry_init():
    registry = SourceRegistry()
    assert isinstance(registry.sources, dict)
