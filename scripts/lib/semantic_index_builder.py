import os
import json
import time
import re
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime

from scripts.lib.base_generator import BaseGenerator, ArtifactResult, BuildContext
from scripts.lib.artifact_utils import atomic_write_json_artifact

class SemanticIndexBuilder(BaseGenerator):
    def __init__(self):
        super().__init__("semantic_index_builder", phase=9, version="1.0.0")
        self.data_dir = os.path.join("data", "processed")
        self.output_file = os.path.join("site", "search_index.json")
        self.schema_path = os.path.join("schemas", "search_index.schema.json")
        
    def tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        # Simple deterministic tokenization: lowercase, keep alphanum, split by whitespace
        text = text.lower()
        tokens = re.findall(r'[a-z0-9]+', text)
        return [t for t in tokens if len(t) >= 2]

    def generate(self, context: BuildContext = None) -> ArtifactResult:
        start_time = time.time()
        result = ArtifactResult(
            generator_name=self.name,
            generator_version=self.version
        )
        
        index = defaultdict(list)
        entities_processed = 0
        
        # We need to process in deterministic order
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
                
                # Tokenize title/name, description, tags
                title_tokens = self.tokenize(entity.get("name", entity.get("technique_name", entity.get("title", ""))))
                desc_tokens = self.tokenize(entity.get("description", ""))
                tag_tokens = []
                for tag in entity.get("tags", []):
                    tag_tokens.extend(self.tokenize(tag))
                    
                category_tokens = self.tokenize(entity.get("category", ""))
                
                # Assign weights (title > tag > category > desc)
                weights = defaultdict(float)
                for t in title_tokens:
                    weights[t] += 2.0
                for t in tag_tokens:
                    weights[t] += 1.5
                for t in category_tokens:
                    weights[t] += 1.2
                for t in desc_tokens:
                    weights[t] += 1.0
                    
                for token, score in weights.items():
                    # Check if token exists for this entity to update or append
                    index[token].append({
                        "entity_id": uid,
                        "score": round(score, 4),
                        "match_type": "exact"
                    })
                    
        # Sort index keys deterministically
        sorted_index = {}
        for token in sorted(index.keys()):
            # Sort occurrences by score descending, then by entity_id ascending for determinism
            occurrences = sorted(index[token], key=lambda x: (-x["score"], x["entity_id"]))
            sorted_index[token] = occurrences
            
        output_data = {
            "schema_version": self.version,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_entities": entities_processed,
            "chunks": [], # To be populated by exporter
            "index": sorted_index
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
            result.warnings.append("Failed to write search index or validation failed.")
            
        result.entities_processed = entities_processed
        result.execution_time_ms = int((time.time() - start_time) * 1000)
        
        return result

if __name__ == "__main__":
    builder = SemanticIndexBuilder()
    builder.generate()
