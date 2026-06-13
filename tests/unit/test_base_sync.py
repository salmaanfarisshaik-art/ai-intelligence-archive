import pytest
from scripts.lib.base_sync import BaseSync

def test_base_sync_init():
    class DummySync(BaseSync):
        def __init__(self):
            super().__init__("dummy", "data/processed/dummy")
        def fetch(self):
            return []
    
    sync = DummySync()
    assert sync.schema_name == "dummy"
