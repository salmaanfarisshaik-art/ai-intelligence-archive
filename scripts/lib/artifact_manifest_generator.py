import os
import json
import time
import hashlib
from typing import Dict, Any

from scripts.lib.base_generator import BaseGenerator, ArtifactResult, BuildContext
from scripts.lib.artifact_utils import atomic_write_json_artifact

class ArtifactManifestGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("artifact_manifest_generator", phase=9, version="1.0.0")
        self.output_file = os.path.join("site", "artifact_manifest.json")
        self.schema_path = os.path.join("schemas", "artifact_manifest.schema.json")
        self.site_dir = "site"
        
    def generate(self, context: BuildContext = None) -> ArtifactResult:
        start_time = time.time()
        result = ArtifactResult(
            generator_name=self.name,
            generator_version=self.version
        )
        
        # We need to hash all files in site/ (except artifact_manifest.json and reports/build_manifest.json)
        artifacts = []
        
        for root, dirs, files in os.walk(self.site_dir):
            for file in sorted(files):
                if file == "artifact_manifest.json":
                    continue
                    
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, self.site_dir)
                # Convert backslashes to forward slashes for cross-platform determinism
                rel_path = rel_path.replace("\\", "/")
                
                with open(filepath, "rb") as f:
                    content = f.read()
                    file_hash = hashlib.sha256(content).hexdigest()
                    
                artifacts.append({
                    "artifact_path": rel_path,
                    "sha256": file_hash,
                    "size_bytes": len(content),
                    "schema_version": self.version # added to match schema definition
                })
                
        # Sort deterministically
        artifacts = sorted(artifacts, key=lambda x: x["artifact_path"])
        
        manifest_data = {
            "schema_version": self.version,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "artifacts": artifacts
        }
        
        success = atomic_write_json_artifact(
            self.output_file,
            manifest_data,
            schema_path=self.schema_path,
            is_dry_run=self.is_dry_run
        )
        
        result.validation_status = success
        if success:
            result.artifacts_written.append(self.output_file)
        else:
            result.warnings.append("Failed to write artifact_manifest.json or validation failed.")
            
        result.entities_processed = len(artifacts)
        result.execution_time_ms = int((time.time() - start_time) * 1000)
        
        return result

if __name__ == "__main__":
    generator = ArtifactManifestGenerator()
    generator.generate()
