import os
import json
import time
from typing import Dict, Any

from scripts.lib.base_generator import BaseGenerator, ArtifactResult, BuildContext
from scripts.lib.artifact_utils import atomic_write_json_artifact
from scripts.lib.archive_stats_generator import ArchiveStatsGenerator

class DashboardDataGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("dashboard_data_generator", phase=9, version="1.0.0")
        self.output_file = os.path.join("site", "dashboard_metrics.json")
        self.graph_file = os.path.join("site", "entity_graph.json")
        
    def generate(self, context: BuildContext = None) -> ArtifactResult:
        start_time = time.time()
        result = ArtifactResult(
            generator_name=self.name,
            generator_version=self.version
        )
        
        # Get base stats from Phase 8.5 logic
        legacy_generator = ArchiveStatsGenerator()
        stats = legacy_generator.generate()
        
        # Get edges count
        edges_count = 0
        if os.path.exists(self.graph_file):
            with open(self.graph_file, "r", encoding="utf-8") as f:
                graph_data = json.load(f)
                edges_count = len(graph_data.get("edges", []))
                
        # Get sources count
        sources_count = 0
        sources_file = os.path.join("data", "metadata", "source_registry.json")
        if os.path.exists(sources_file):
            with open(sources_file, "r", encoding="utf-8") as f:
                sources_data = json.load(f)
                sources_count = len(sources_data)
                
        # Target counts based on user's goal
        targets = {
            "models": 1500,
            "skills": 30000,
            "prompts": 20000,
            "sources": 100
        }
        
        dashboard_metrics = {
            "schema_version": self.version,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "last_successful_sync": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "repository_version": "v1.0.0",
            "metrics": [
                {
                    "metric": "AI Models",
                    "current": stats.get("models", 0),
                    "target": targets["models"]
                },
                {
                    "metric": "AI Skills",
                    "current": stats.get("skills", 0),
                    "target": targets["skills"]
                },
                {
                    "metric": "Prompt Templates",
                    "current": stats.get("prompts", 0),
                    "target": targets["prompts"]
                },
                {
                    "metric": "Sources",
                    "current": sources_count,
                    "target": targets["sources"]
                },
                {
                    "metric": "Knowledge Graph Edges",
                    "current": edges_count,
                    "target": "-"
                }
            ],
            "raw_stats": stats
        }
        
        success = atomic_write_json_artifact(
            self.output_file,
            dashboard_metrics,
            schema_path=None, # no strict schema specified yet
            is_dry_run=self.is_dry_run
        )
        
        if success:
            result.artifacts_written.append(self.output_file)
        else:
            result.validation_status = False
            result.warnings.append("Failed to write dashboard_metrics.json or validation failed.")
            
        result.execution_time_ms = int((time.time() - start_time) * 1000)
        
        return result

if __name__ == "__main__":
    generator = DashboardDataGenerator()
    generator.generate()
