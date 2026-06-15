import os
import json
import time
from typing import Dict, Any, List

from scripts.lib.base_generator import BaseGenerator, ArtifactResult, BuildContext
from scripts.lib.artifact_utils import atomic_write_json_artifact

class EntityLinker(BaseGenerator):
    def __init__(self):
        super().__init__("entity_linker", phase=9, version="1.0.0")
        self.data_dir = os.path.join("data", "processed")
        self.output_file = os.path.join("site", "entity_links.json")
        self.schema_path = os.path.join("schemas", "entity_links.schema.json")
        
    def generate(self, context: BuildContext = None) -> ArtifactResult:
        start_time = time.time()
        result = ArtifactResult(
            generator_name=self.name,
            generator_version=self.version
        )
        
        links = []
        entities_processed = 0
        
        # We need a map of canonical IDs or names to link properly.
        # But for now we can just emit links based on tags, even if the target is external or missing.
        # It's better to verify if target exists, but we can resolve that in graph builder.
        
        domains = sorted(os.listdir(self.data_dir))
        for domain in domains:
            domain_dir = os.path.join(self.data_dir, domain)
            if not os.path.isdir(domain_dir):
                continue
                
            data_file = os.path.join(domain_dir, "data.json")
            if not os.path.exists(data_file):
                continue
                
            with open(data_file, "r", encoding="utf-8") as f:
                entities = json.load(f)
                
            # Entities must be sorted by canonical_id
            entities = sorted(entities, key=lambda x: x.get("unique_id", ""))
            
            for entity in entities:
                uid = entity.get("unique_id")
                if not uid:
                    continue
                    
                entities_processed += 1
                
                # Check tags for 'dataset:' or 'base_model:'
                # Many entities have tags either at top level or inside raw_payload
                tags = entity.get("tags", [])
                if not tags and "raw_payload" in entity:
                    tags = entity["raw_payload"].get("tags", [])
                    
                if not isinstance(tags, list):
                    continue
                    
                for tag in tags:
                    if not isinstance(tag, str):
                        continue
                    if tag.startswith("dataset:"):
                        target = "hf_" + tag.split(":", 1)[1].replace("/", "_")
                        links.append({
                            "source_id": uid,
                            "target_id": target,
                            "type": "trained_on"
                        })
                    elif tag.startswith("base_model:") or tag.startswith("base_model:quantized:"):
                        # Extract the actual model path
                        parts = tag.split(":")
                        target = "hf_" + parts[-1].replace("/", "_")
                        links.append({
                            "source_id": uid,
                            "target_id": target,
                            "type": "derived_from"
                        })
                        
        # Sort links for determinism
        links = sorted(links, key=lambda x: (x["source_id"], x["target_id"], x["type"]))
        
        # Deduplicate links
        unique_links = []
        seen = set()
        for link in links:
            tup = (link["source_id"], link["target_id"], link["type"])
            if tup not in seen:
                seen.add(tup)
                unique_links.append(link)
                
        output_data = {
            "schema_version": self.version,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "links": unique_links
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
            result.warnings.append("Failed to write entity_links.json or validation failed.")
            
        result.entities_processed = entities_processed
        result.execution_time_ms = int((time.time() - start_time) * 1000)
        
        return result

if __name__ == "__main__":
    linker = EntityLinker()
    linker.generate()
