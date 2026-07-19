import pytest
from core.source_registry import SourceRegistry

def test_source_registry_init():
    registry = SourceRegistry()
    assert isinstance(registry.sources, dict)
