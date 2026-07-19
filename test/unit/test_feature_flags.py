import pytest
from core.feature_flag_validator import FeatureFlagValidator

def test_feature_flags():
    validator = FeatureFlagValidator()
    metrics = validator.generate()
    assert "records_processed" in metrics
