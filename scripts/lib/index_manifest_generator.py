import os
import json
import time
from typing import Dict, Any

from scripts.lib.base_generator import BaseGenerator, ArtifactResult, BuildContext
from scripts.lib.artifact_utils import atomic_write_json_artifact

class IndexManifestGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("index_manifest_generator", phase=9, version="1.0.0")
        self.output_file = os.path.join("site", "index_manifest.json")
        
    def generate(self, context: BuildContext = None) -> ArtifactResult:
        start_time = time.time()
        result = ArtifactResult(
            generator_name=self.name,
            generator_version=self.version
        )
        
        # Classification mapping
        classifications = [
            {
                "artifact": "search_index.json",
                "schema_version": "1.0",
                "required": True,
                "consumer": ["/search"]
            },
            {
                "artifact": "search_index_manifest.json",
                "schema_version": "1.0",
                "required": True,
                "consumer": ["/search"]
            },
            {
                "artifact": "timeline.json",
                "schema_version": "1.0",
                "required": False,
                "consumer": ["/timeline"]
            },
            {
                "artifact": "entity_graph.json",
                "schema_version": "1.0",
                "required": False,
                "consumer": ["/graph", "/entity"]
            },
            {
                "artifact": "related_entities.json",
                "schema_version": "1.0",
                "required": False,
                "consumer": ["/entity"]
            },
            {
                "artifact": "entity_links.json",
                "schema_version": "1.0",
                "required": False,
                "consumer": ["/entity"]
            },
            {
                "artifact": "dashboard_metrics.json",
                "schema_version": "1.0",
                "required": True,
                "consumer": ["/", "/statistics"]
            },
            {
                "artifact": "artifact_manifest.json",
                "schema_version": "1.0",
                "required": False,
                "consumer": ["/artifacts"]
            }
        ]
        
        manifest_data = {
            "schema_version": self.version,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "artifacts": classifications
        }
        
        # In a real environment, we would also generate individual manifests like search_index_manifest.json
        # Here we just output the consolidated index_manifest.json
        
        success = atomic_write_json_artifact(
            self.output_file,
            manifest_data,
            schema_path=None, # We don't have an explicit schema for this yet
            is_dry_run=self.is_dry_run
        )
        
        if success:
            result.artifacts_written.append(self.output_file)
        else:
            result.validation_status = False
            
        result.execution_time_ms = int((time.time() - start_time) * 1000)
        return result

if __name__ == "__main__":
    generator = IndexManifestGenerator()
    generator.generate()
