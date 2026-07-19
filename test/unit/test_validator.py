import pytest
from core.validator import RecordValidator

def test_validator_init():
    validator = RecordValidator()
    # It should not crash on init
    assert validator is not None
