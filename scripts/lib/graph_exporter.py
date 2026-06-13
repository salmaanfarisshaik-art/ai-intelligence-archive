import os
import json
from typing import Dict, Any, List

from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("graph_exporter")

class GraphExporter:
    def __init__(self):
        self.metadata_dir = os.path.join("data", "metadata")
        os.makedirs(self.metadata_dir, exist_ok=True)
        self.entity_index_path = os.path.join(self.metadata_dir, "entity_index.json")

    def _atomic_write(self, filepath: str, content: str):
        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        if is_dry_run:
            logger.info(f"DRY RUN: Would have saved graph to {filepath}")
            return
            
        tmp_filepath = f"{filepath}.tmp"
        try:
            with open(tmp_filepath, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_filepath, filepath)
            logger.info(f"Successfully saved {filepath}")
        except Exception as e:
            logger.error(f"Failed atomic write to {filepath}: {e}")
            if os.path.exists(tmp_filepath):
                os.remove(tmp_filepath)

    def generate(self):
        if not config.is_feature_enabled("enable_relationship_graph"):
            logger.info("Relationship graph generation is disabled in config.")
            return

        logger.info("Exporting relationship graph...")
        
        if not os.path.exists(self.entity_index_path):
            logger.warning(f"Cannot generate graph. {self.entity_index_path} is missing.")
            return
            
        try:
            with open(self.entity_index_path, "r", encoding="utf-8") as f:
                entities = json.load(f)
                
            nodes = []
            edges = []
            
            # Map deterministic ids or hf/arxiv formats to nodes to ensure valid edges
            for entity in entities:
                nodes.append({
                    "id": entity["id"],
                    "label": entity["title"],
                    "category": entity["category"]
                })
                
                # Extract edges
                links = entity.get("links", {})
                for rel_type, rel_targets in links.items():
                    if not isinstance(rel_targets, list):
                        continue
                    for target in rel_targets:
                        edges.append({
                            "source": entity["id"],
                            "target": str(target),
                            "relationship": rel_type
                        })
                        
            # Deterministic ordering
            nodes = sorted(nodes, key=lambda x: x["id"])
            edges = sorted(edges, key=lambda x: (x["source"], x["target"], x["relationship"]))
            
            graph_data = {
                "nodes": nodes,
                "edges": edges
            }
            
            self._atomic_write(
                os.path.join(self.metadata_dir, "relationship_graph.json"),
                json.dumps(graph_data, indent=2, ensure_ascii=False)
            )
            
            logger.info("Relationship graph exported successfully.")
        except Exception as e:
            logger.error(f"Error exporting relationship graph: {e}")

if __name__ == "__main__":
    GraphExporter().generate()
