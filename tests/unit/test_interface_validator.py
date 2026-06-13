import pytest
from scripts.lib.interface_validator import InterfaceValidator
import os

def test_interface_validator_dry_run():
    os.environ["DRY_RUN"] = "true"
    validator = InterfaceValidator()
    metrics = validator.run()
    assert "errors" in metrics
    os.environ["DRY_RUN"] = "false"

def test_interface_validator_generation():
    validator = InterfaceValidator()
    metrics = validator.generate()
    # It might fail if no directories exist yet, but it shouldn't crash
    assert "errors" in metrics
