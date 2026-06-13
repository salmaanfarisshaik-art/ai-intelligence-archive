import os
import time
from typing import Any, Dict
from scripts.lib.logger import setup_logger
from scripts.lib.serialization import save_json_deterministic, save_yaml_deterministic, save_markdown_deterministic

class BaseGenerator:
    """
    Base class for Phase 6 and Phase 7 generators.
    Provides shared functionality for logging, error reporting, metrics, and persistence.
    """
    def __init__(self, name: str, phase: int, version: str = "1.0.0"):
        self.name = name
        self.phase = phase
        self.version = version
        self.logger = setup_logger(self.name)
        self.is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        self.metrics: Dict[str, Any] = {
            "execution_time_seconds": 0.0,
            "records_processed": 0,
            "errors": 0
        }

    def _add_metadata(self, data: Any) -> Any:
        """
        Wraps data in standard metadata envelope if it's a dict.
        """
        if isinstance(data, dict):
            return {
                "schema_version": self.version,
                "generator": self.name,
                "generated_by_phase": self.phase,
                "data": data
            }
        return data

    def save_json(self, filepath: str, data: Any):
        if self.is_dry_run:
            self.logger.info(f"DRY RUN: Would have saved JSON to {filepath}")
            return
        wrapped_data = self._add_metadata(data)
        save_json_deterministic(filepath, wrapped_data)

    def save_yaml(self, filepath: str, data: Any):
        if self.is_dry_run:
            self.logger.info(f"DRY RUN: Would have saved YAML to {filepath}")
            return
        wrapped_data = self._add_metadata(data)
        save_yaml_deterministic(filepath, wrapped_data)

    def save_markdown(self, filepath: str, content: str):
        if self.is_dry_run:
            self.logger.info(f"DRY RUN: Would have saved Markdown to {filepath}")
            return
        save_markdown_deterministic(filepath, content)

    def generate(self) -> Dict[str, Any]:
        """
        Main execution method to be implemented by subclasses.
        Must return metrics dict.
        """
        raise NotImplementedError

    def run(self) -> Dict[str, Any]:
        """
        Standard execution flow with telemetry.
        """
        start_time = time.time()
        self.logger.info(f"Starting generator: {self.name} (Phase {self.phase})")
        
        try:
            custom_metrics = self.generate()
            if custom_metrics:
                self.metrics.update(custom_metrics)
        except Exception as e:
            self.logger.error(f"Generator {self.name} failed.", exc_info=True)
            self.metrics["errors"] += 1
            # We don't raise here, we fail soft per ADR-005.
        finally:
            self.metrics["execution_time_seconds"] = round(time.time() - start_time, 2)
            self.logger.info(f"Completed generator: {self.name} in {self.metrics['execution_time_seconds']}s")
            
        return self.metrics
