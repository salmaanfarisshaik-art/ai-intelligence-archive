import os
import json
import time
import tempfile
from typing import Dict, Any

from scripts.lib.base_generator import BaseGenerator, ArtifactResult, BuildContext
from scripts.lib.artifact_utils import atomic_write_json_artifact, atomic_directory_swap

class SearchIndexExporter(BaseGenerator):
    def __init__(self):
        super().__init__("search_index_exporter", phase=9, version="1.0.0")
        self.input_file = os.path.join("site", "search_index.json")
        self.output_dir = os.path.join("site", "search")
        self.schema_path = os.path.join("schemas", "search_index.schema.json")
        
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
            search_data = json.load(f)
            
        full_index = search_data.get("index", {})
        
        # Chunking strategy: 1-character prefixes for a-z and 0-9.
        # Fallback to 'other'
        chunks = {}
        for token, occurrences in full_index.items():
            if not token:
                continue
            prefix = token[0].lower()
            if not prefix.isalnum():
                prefix = "other"
                
            if prefix not in chunks:
                chunks[prefix] = {}
            chunks[prefix][token] = occurrences
            
        # Write chunks to a temp directory
        temp_dir = tempfile.mkdtemp(prefix="search_chunks_")
        chunk_names = []
        try:
            for prefix, chunk_data in chunks.items():
                chunk_name = f"chunk_{prefix}.json"
                chunk_names.append(chunk_name)
                chunk_path = os.path.join(temp_dir, chunk_name)
                with open(chunk_path, "w", encoding="utf-8") as f:
                    # Deterministic JSON
                    json.dump(chunk_data, f, indent=2, sort_keys=True, ensure_ascii=False)
                    f.write("\n")
                    
            # Swap directory atomically
            swap_success = atomic_directory_swap(self.output_dir, temp_dir, is_dry_run=self.is_dry_run)
            if not swap_success:
                result.validation_status = False
                result.warnings.append("Atomic directory swap failed.")
            else:
                result.artifacts_written.append(self.output_dir)
                
        except Exception as e:
            result.validation_status = False
            result.warnings.append(str(e))
            self.logger.error("Error during chunk export", exc_info=True)
            
        # Update the main search_index.json to include the chunk names
        search_data["chunks"] = sorted(chunk_names)
        
        # Rewrite the main index file, but remove the monolithic 'index' to save space for frontend
        # Wait, the schema requires "index". Let's keep a small subset or the full index if schema requires.
        # But if the full index is 100MB, we shouldn't send it to the frontend.
        # Actually, our schema for search_index.schema.json requires 'index'. 
        # If we remove it, it fails validation. Let's just keep 'index' empty for the monolithic file, 
        # and update schema to allow empty index. Or we can just leave it as is if it's small.
        # Let's keep it empty to save space and rely on chunks.
        search_data["index"] = {}
        
        success = atomic_write_json_artifact(
            self.input_file,
            search_data,
            schema_path=self.schema_path,
            is_dry_run=self.is_dry_run
        )
        
        if success:
            result.artifacts_written.append(self.input_file)
        else:
            result.validation_status = False
            
        result.entities_processed = search_data.get("total_entities", 0)
        result.execution_time_ms = int((time.time() - start_time) * 1000)
        
        return result

if __name__ == "__main__":
    exporter = SearchIndexExporter()
    exporter.generate()
