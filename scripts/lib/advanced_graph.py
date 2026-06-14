import os
import json
from typing import Dict, Any
from scripts.lib.base_generator import BaseGenerator
from scripts.lib.serialization import save_json_deterministic
from scripts.lib.logger import setup_logger

logger = setup_logger("advanced_graph")

class AdvancedGraph(BaseGenerator):
    def __init__(self):
        super().__init__("advanced_graph", phase=6)
        
    def generate(self) -> Dict[str, Any]:
        """
        Generates deeper deterministic relationships.
        """
        graph = {
            "nodes": [],
            "edges": []
        }
        
        # Optional dependency example
        try:
            import networkx as nx
            nx_graph = nx.Graph()
        except ImportError:
            logger.info("networkx not installed, skipping advanced metrics")
            nx_graph = None

        # Deterministic generation
        models_path = "data/models/data.json"
        if os.path.exists(models_path):
            with open(models_path, "r", encoding="utf-8") as f:
                models = json.load(f)
                for m in models:
                    graph["nodes"].append({"id": m.get("id"), "type": "model"})
                    if nx_graph is not None:
                        nx_graph.add_node(m.get("id"))
                    
        os.makedirs("data/metadata", exist_ok=True)
        os.makedirs("exports/graph", exist_ok=True)
        
        # Sort to ensure deterministic output
        graph["nodes"] = sorted(graph["nodes"], key=lambda x: x["id"])
        graph["edges"] = sorted(graph["edges"], key=lambda x: (x.get("source", ""), x.get("target", "")))
        
        save_json_deterministic("data/metadata/knowledge_graph.json", graph)
        save_json_deterministic("exports/graph/knowledge_graph.json", graph)
        
        return {"records_processed": len(graph["nodes"])}

    def run(self):
        self.generate()
