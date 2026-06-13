"""
-------------------------------------------------------
THIS FILE IS AUTO-GENERATED.
DO NOT EDIT MANUALLY.
Changes may be overwritten during the next pipeline run.
-------------------------------------------------------

Graph API Exporter.
Generates graph/nodes.json, graph/edges.json, and graph/graph_api.json
from the deterministic relationship_graph.json.
AI-inferred relationships never become authoritative graph edges.
"""
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any

from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("graph_api_exporter")


class GraphAPIExporter:
    """Exports relationship graph data into separate node and edge files."""

    def __init__(self):
        self.graph_dir = "graph"
        self.metadata_dir = os.path.join("data", "metadata")
        os.makedirs(self.graph_dir, exist_ok=True)

    def generate(self):
        if not config.is_feature_enabled("enable_graph_api_exports"):
            logger.info("Graph API exports disabled in config.")
            return

        logger.info("Generating Graph API exports...")

        graph_path = os.path.join(self.metadata_dir, "relationship_graph.json")
        if not os.path.exists(graph_path):
            logger.warning("relationship_graph.json not found. Skipping graph API export.")
            return

        with open(graph_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

        timestamp = datetime.now(timezone.utc).isoformat()
        base_meta = {
            "schema_version": "1.0",
            "generated_by": "AI Intelligence Archive",
            "generator_phase": "phase_5",
            "generated_at": timestamp,
        }

        nodes = sorted(graph_data.get("nodes", []), key=lambda n: n.get("id", ""))
        edges = sorted(
            graph_data.get("edges", []),
            key=lambda e: (e.get("source", ""), e.get("target", ""))
        )

        nodes_output = {**base_meta, "total_nodes": len(nodes), "nodes": nodes}
        edges_output = {**base_meta, "total_edges": len(edges), "edges": edges}
        graph_api_output = {
            **base_meta,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes": nodes,
            "edges": edges,
        }

        self._atomic_write(
            os.path.join(self.graph_dir, "nodes.json"),
            json.dumps(nodes_output, indent=2, sort_keys=True, ensure_ascii=False)
        )
        self._atomic_write(
            os.path.join(self.graph_dir, "edges.json"),
            json.dumps(edges_output, indent=2, sort_keys=True, ensure_ascii=False)
        )
        self._atomic_write(
            os.path.join(self.graph_dir, "graph_api.json"),
            json.dumps(graph_api_output, indent=2, sort_keys=True, ensure_ascii=False)
        )

        logger.info("Graph API exports generated successfully.")

    def _atomic_write(self, filepath: str, content: str):
        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        if is_dry_run:
            logger.info(f"DRY RUN: Would have saved {filepath}")
            return
        tmp = f"{filepath}.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp, filepath)
            logger.info(f"Successfully saved {filepath}")
        except Exception as e:
            logger.error(f"Failed atomic write to {filepath}: {e}")
            if os.path.exists(tmp):
                os.remove(tmp)


if __name__ == "__main__":
    GraphAPIExporter().generate()
