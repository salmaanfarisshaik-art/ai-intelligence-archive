import os
import json
import time
from typing import Dict, Any, List

from scripts.lib.base_generator import BaseGenerator, ArtifactResult, BuildContext
from scripts.lib.artifact_utils import atomic_write_json_artifact
from scripts.lib.serialization import save_markdown_deterministic

class KnowledgeGraphBuilder(BaseGenerator):
    def __init__(self):
        super().__init__("knowledge_graph_builder", phase=9, version="1.0.0")
        self.data_dir = os.path.join("data", "processed")
        self.input_file = os.path.join("site", "entity_links.json")
        self.output_file = os.path.join("site", "entity_graph.json")
        self.schema_path = os.path.join("schemas", "entity_graph.schema.json")
        self.report_file = os.path.join("reports", "knowledge_graph_report.md")
        
    def generate(self, context: BuildContext = None) -> ArtifactResult:
        start_time = time.time()
        result = ArtifactResult(
            generator_name=self.name,
            generator_version=self.version
        )
        
        nodes = []
        node_ids = set()
        
        # Build Nodes from all canonical entities
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
                
            entities = sorted(entities, key=lambda x: x.get("unique_id", ""))
            
            for entity in entities:
                uid = entity.get("unique_id")
                if not uid:
                    continue
                
                title = entity.get("name", entity.get("technique_name", entity.get("title", "Unknown")))
                
                nodes.append({
                    "canonical_id": uid,
                    "entity_type": domain,
                    "title": title,
                    "category": entity.get("category", "Unknown"),
                    "tags": entity.get("tags", []),
                    "provenance_reference": entity.get("source_url", "")
                })
                node_ids.add(uid)
                
        # Build Edges
        edges = []
        if os.path.exists(self.input_file):
            with open(self.input_file, "r", encoding="utf-8") as f:
                links_data = json.load(f)
                
            for link in links_data.get("links", []):
                # Ensure target node actually exists, otherwise it's a dangling edge
                if link["target_id"] in node_ids and link["source_id"] in node_ids:
                    edges.append({
                        "source_id": link["source_id"],
                        "target_id": link["target_id"],
                        "relationship_type": link["type"],
                        "confidence_score": 1.0,
                        "generation_method": "deterministic_tag_parsing"
                    })
        else:
            result.warnings.append(f"Entity links file not found: {self.input_file}")
            
        nodes = sorted(nodes, key=lambda x: x["canonical_id"])
        edges = sorted(edges, key=lambda x: (x["source_id"], x["target_id"], x["relationship_type"]))
        
        graph_data = {
            "graph_schema_version": self.version,
            "relationship_schema_version": self.version,
            "node_schema_version": self.version,
            "nodes": nodes,
            "edges": edges
        }
        
        success = atomic_write_json_artifact(
            self.output_file,
            graph_data,
            schema_path=self.schema_path,
            is_dry_run=self.is_dry_run
        )
        
        if success:
            result.artifacts_written.append(self.output_file)
        else:
            result.validation_status = False
            result.warnings.append("Failed to write entity_graph.json or validation failed.")
            
        # Write Report
        report_content = f"""# Knowledge Graph Report
        
Generated at: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}

## Graph Statistics
- Total Nodes: {len(nodes)}
- Total Edges: {len(edges)}

## Node Types
"""
        type_counts = {}
        for n in nodes:
            t = n["entity_type"]
            type_counts[t] = type_counts.get(t, 0) + 1
            
        for t, c in sorted(type_counts.items()):
            report_content += f"- {t}: {c}\n"
            
        if not self.is_dry_run:
            save_markdown_deterministic(self.report_file, report_content)
            result.artifacts_written.append(self.report_file)
            
        result.entities_processed = len(nodes)
        result.execution_time_ms = int((time.time() - start_time) * 1000)
        
        return result

if __name__ == "__main__":
    builder = KnowledgeGraphBuilder()
    builder.generate()
