"""
-------------------------------------------------------
THIS FILE IS AUTO-GENERATED.
DO NOT EDIT MANUALLY.
Changes may be overwritten during the next pipeline run.
-------------------------------------------------------

Repository Manifest Generator.
Generates machine-readable manifests for tooling, plugin discovery,
API discovery, release validation, and automation support.
Manifests are descriptive metadata only and never become authoritative over canonical data.
"""
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any

from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("generate_manifests")


class ManifestGenerator:
    """Generates deterministic, machine-readable repository manifests."""

    def __init__(self):
        self.metadata_dir = os.path.join("data", "metadata")
        os.makedirs(self.metadata_dir, exist_ok=True)

    def generate(self):
        if not config.is_feature_enabled("enable_manifest_generation"):
            logger.info("Manifest generation is disabled in config.")
            return

        logger.info("Generating repository manifests...")

        timestamp = datetime.now(timezone.utc).isoformat()
        base_meta = {
            "schema_version": "1.0",
            "generated_by": "AI Intelligence Archive",
            "generator_phase": "phase_5",
            "generated_at": timestamp,
        }

        self._generate_repository_manifest(base_meta)
        self._generate_connector_manifest(base_meta)
        self._generate_feature_manifest(base_meta)
        self._generate_schema_manifest(base_meta)
        self._generate_api_manifest(base_meta)

        logger.info("Manifest generation complete.")

    def _generate_repository_manifest(self, base_meta: Dict[str, Any]):
        """Overview manifest describing the repository structure."""
        processed_dir = os.path.join("data", "processed")
        categories = []
        if os.path.isdir(processed_dir):
            categories = sorted([
                d for d in os.listdir(processed_dir)
                if os.path.isdir(os.path.join(processed_dir, d))
            ])

        manifest = {
            **base_meta,
            "manifest_type": "repository",
            "data_categories": categories,
            "output_directories": {
                "processed_data": "data/processed/",
                "metadata": "data/metadata/",
                "exports_json": "exports/json/",
                "exports_csv": "exports/csv/",
                "exports_markdown": "exports/markdown/",
                "documentation": "docs/",
                "reports": "reports/",
                "site_assets": "site/",
                "graph": "graph/",
                "releases": "releases/",
                "snapshots": "snapshots/",
            },
        }
        self._atomic_write(
            os.path.join(self.metadata_dir, "repository_manifest.json"),
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False)
        )

    def _generate_connector_manifest(self, base_meta: Dict[str, Any]):
        """List of data source connectors."""
        # Read from config sources
        connectors = []
        for src_id, src_config in sorted(config.sources.items()):
            connectors.append({
                "id": src_id,
                "name": src_config.get("name", src_id),
                "type": src_config.get("type", "unknown"),
                "enabled": src_config.get("enabled", True),
            })

        manifest = {
            **base_meta,
            "manifest_type": "connectors",
            "connectors": connectors,
        }
        self._atomic_write(
            os.path.join(self.metadata_dir, "connector_manifest.json"),
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False)
        )

    def _generate_feature_manifest(self, base_meta: Dict[str, Any]):
        """List of all feature flags and their current states."""
        features = {k: v for k, v in sorted(config.features.items())}

        manifest = {
            **base_meta,
            "manifest_type": "features",
            "features": features,
        }
        self._atomic_write(
            os.path.join(self.metadata_dir, "feature_manifest.json"),
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False)
        )

    def _generate_schema_manifest(self, base_meta: Dict[str, Any]):
        """Describes the canonical record schema."""
        manifest = {
            **base_meta,
            "manifest_type": "schema",
            "canonical_record_fields": [
                "unique_id", "name", "category", "source_name", "source_url",
                "description", "retrieved_at", "raw_payload",
                "ai_summary", "ai_tags", "ai_category", "ai_enrichment_provider",
                "links", "hash",
            ],
        }
        self._atomic_write(
            os.path.join(self.metadata_dir, "schema_manifest.json"),
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False)
        )

    def _generate_api_manifest(self, base_meta: Dict[str, Any]):
        """Describes available API endpoints."""
        manifest = {
            **base_meta,
            "manifest_type": "api",
            "api_type": "local_http",
            "read_only": True,
            "endpoints": sorted([
                "/api/models",
                "/api/papers",
                "/api/datasets",
                "/api/tools",
                "/api/news",
                "/api/search",
                "/api/categories",
                "/api/tags",
                "/api/analytics",
                "/api/graph",
                "/api/entity/<id>",
            ]),
        }
        self._atomic_write(
            os.path.join(self.metadata_dir, "api_manifest.json"),
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False)
        )

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
    ManifestGenerator().generate()
