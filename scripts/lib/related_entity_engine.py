import os
import json
import time
from typing import Dict, Any
from collections import defaultdict

from scripts.lib.base_generator import BaseGenerator, ArtifactResult, BuildContext
from scripts.lib.artifact_utils import atomic_write_json_artifact

class RelatedEntityEngine(BaseGenerator):
    def __init__(self):
        super().__init__("related_entity_engine", phase=9, version="1.0.0")
        self.input_file = os.path.join("site", "entity_links.json")
        self.output_file = os.path.join("site", "related_entities.json")
        self.schema_path = os.path.join("schemas", "related_entities.schema.json")
        
    def generate(self, context: BuildContext = None) -> ArtifactResult:
        start_time = time.time()
        result = ArtifactResult(
            generator_name=self.name,
            generator_version=self.version
        )
        
        if not os.path.exists(self.input_file):
            result.warnings.append(f"Input file {self.input_file} not found.")
            result.validation_status = False
            return result
            
        with open(self.input_file, "r", encoding="utf-8") as f:
            links_data = json.load(f)
            
        # Adjacency list: entity_id -> list of related entity_ids
        adj = defaultdict(set)
        
        links = links_data.get("links", [])
        for link in links:
            src = link.get("source_id")
            tgt = link.get("target_id")
            if src and tgt:
                adj[src].add(tgt)
                adj[tgt].add(src)
                
        # Sort values for determinism
        related = {}
        for k in sorted(adj.keys()):
            related[k] = sorted(list(adj[k]))
            
        output_data = {
            "schema_version": self.version,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "related": related
        }
        
        success = atomic_write_json_artifact(
            self.output_file,
            output_data,
            schema_path=self.schema_path,
            is_dry_run=self.is_dry_run
        )
        
        result.validation_status = success
        if success:
            result.artifacts_written.append(self.output_file)
        else:
            result.warnings.append("Failed to write related_entities.json or validation failed.")
            
        result.entities_processed = len(related)
        result.execution_time_ms = int((time.time() - start_time) * 1000)
        
        return result

if __name__ == "__main__":
    engine = RelatedEntityEngine()
    engine.generate()
