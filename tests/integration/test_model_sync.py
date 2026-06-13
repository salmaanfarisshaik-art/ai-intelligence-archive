import pytest
from scripts.sync.model_sync import ModelSync

def test_model_sync_fetch():
    sync = ModelSync()
    data = sync.fetch()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "unique_id" in data[0]
