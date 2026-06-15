import os
import json
from scripts.lib.logger import setup_logger
from scripts.lib.entity_id_generator import EntityIDGenerator
from scripts.lib.deduplication_engine import DeduplicationEngine
from scripts.lib.schema_consistency_validator import SchemaConsistencyValidator
from scripts.lib.provenance_tracker import ProvenanceTracker
from scripts.lib.source_registry import SourceRegistry
from scripts.lib.canonical_snapshot_manager import CanonicalSnapshotManager
from scripts.lib.base_sync import BaseSync

logger = setup_logger("repository_expander")

class RepositoryExpander:
    """
    Distributes raw snapshot data into the canonical Phase 1-8 directories.
    Handles ID generation, deduplication, schema validation, and provenance tracking.
    """
    def __init__(self, is_dry_run: bool = False):
        self.is_dry_run = is_dry_run
        self.snapshot_manager = CanonicalSnapshotManager()
        self.dedupe_engine = DeduplicationEngine()
        self.schema_validator = SchemaConsistencyValidator()
        self.provenance = ProvenanceTracker()
        self.registry = SourceRegistry()
        
    def expand_all(self):
        logger.info(f"Starting Repository Expander... (DRY_RUN={self.is_dry_run})")
        
        # Load from latest snapshots
        sources = self.registry.get_enabled_sources()
        for source_id, source_data in sources.items():
            snapshot = self.snapshot_manager.get_latest_snapshot(source_id)
            if not snapshot:
                logger.debug(f"No recent snapshot for {source_id}, skipping.")
                continue
                
            self.process_source(source_id, source_data, snapshot)
            
        # Also process synthetics we made in seed_fetcher
        synth_categories = ["synth_tools", "synth_benchmarks", "synth_mcps", "synth_ide_rules", "synth_api_providers", "synth_news"]
        for cat in synth_categories:
            snapshot = self.snapshot_manager.get_latest_snapshot(cat)
            if snapshot:
                # Mock source data for synthetics
                self.process_source(cat, {"name": cat, "url": "local", "category": cat.replace("synth_", ""), "license": "MIT"}, snapshot)

        self.schema_validator.generate_report()
        if not self.is_dry_run:
            self.provenance.save()

    def process_source(self, source_id: str, source_data: str, snapshot_records: list):
        # Determine target category and schema
        category = source_data.get("category", "")
        if not category:
            return
            
        logger.info(f"Expanding source {source_id} -> {category} ({len(snapshot_records)} records)")
        
        # Map source categories to pipeline schemas and dirs
        schema_map = {
            "models": ("model", "models"),
            "datasets": ("dataset", "datasets"),
            "prompts": ("prompt", "prompts"),
            "tools": ("tool", "tools"),
            "benchmarks": ("benchmark", "benchmarks"),
            "mcps": ("mcp", "mcps"),
            "ide_rules": ("ide_rule", "ide_rules"),
            "api_providers": ("api_provider", "api_providers"),
            "news": ("news", "news"),
            "skills": ("ai_skill", "ai_skills_library")
        }
        
        mapping = schema_map.get(category)
        if not mapping:
            return
            
        schema_name, target_dir = mapping
        base_sync = BaseSync(schema_name, os.path.join("data", "processed", target_dir))
        
        canonical_records = []
        for raw in snapshot_records:
            # 1. Generate Canonical ID
            # Use specific fields based on schema, or fallback to hash
            if schema_name == "model":
                raw_id = raw.get("id", raw.get("name", ""))
                cid = EntityIDGenerator.generate_id("model", raw_id)
                raw["name"] = raw.get("name", raw_id)
            elif schema_name == "dataset":
                raw_id = raw.get("id", raw.get("name", ""))
                cid = EntityIDGenerator.generate_id("dataset", raw_id)
            elif schema_name == "prompt":
                cid = EntityIDGenerator.generate_id("prompt", str(raw.get("instruction", raw.get("id", "")))[:20])
            else:
                cid = EntityIDGenerator.generate_id(schema_name, raw.get("name", raw.get("id", "")))
                
            raw["unique_id"] = cid
            raw["schema_version"] = "1.0"
            
            # 2. Schema Validation
            if not self.schema_validator.validate(schema_name, raw):
                continue
                
            # 3. Deduplication
            if self.dedupe_engine.is_duplicate(schema_name, raw, source_id):
                continue
                
            # 4. Provenance
            if not self.is_dry_run:
                self.provenance.record_provenance(
                    canonical_id=cid,
                    original_source=source_id,
                    source_url=source_data.get("url", ""),
                    license_type=source_data.get("license", "unknown")
                )
                
            canonical_records.append(raw)
            
        if canonical_records and not self.is_dry_run:
            # Save using standard pipeline BaseSync which respects .tmp atomicity
            base_sync.save(canonical_records)
            logger.info(f"Saved {len(canonical_records)} canonical records for {category}")

if __name__ == "__main__":
    RepositoryExpander().expand_all()
