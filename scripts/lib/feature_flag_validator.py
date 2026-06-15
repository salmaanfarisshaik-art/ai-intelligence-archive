import os
import json
from typing import Dict, Any
from scripts.lib.base_generator import BaseGenerator

class FeatureFlagValidator(BaseGenerator):
    def __init__(self):
        super().__init__("feature_flag_validator", phase=6)
        
    def generate(self) -> Dict[str, Any]:
        """
        Validates feature flags in config/settings.yaml
        """
        import yaml
        
        settings_path = "config/settings.yaml"
        if not os.path.exists(settings_path):
            self.logger.error("Missing config/settings.yaml")
            return {"errors": 1}
            
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = yaml.safe_load(f) or {}
            
        features = settings.get("features", {})
        
        # Define expected flags
        expected_flags = [
            "enable_ai_enrichment", "default_enrichment_provider", "enable_cross_linking",
            "enable_entity_indexing", "enable_search_indexing", "enable_analytics",
            "enable_doc_generation", "enable_export_generation", "enable_dashboard_generation",
            "enable_relationship_graph", "enable_local_api", "enable_query_engine",
            "enable_plugin_system", "enable_release_builder", "enable_integrity_checker",
            "enable_snapshot_generation", "enable_manifest_generation", "enable_graph_api_exports",
            # Phase 6 & 7 Feature Flags
            "enable_recommendation_engine", "enable_leaderboards", "enable_timeline_generation",
            "enable_trend_analysis", "enable_advanced_graph", "enable_site_generation",
            "enable_repository_auditor", "enable_coverage_analysis", "enable_schema_auditor",
            "enable_self_documentation", "enable_dependency_reports", "enable_repository_metrics",
            # Phase 8 Feature Flags
            "enable_change_detection", "enable_pipeline_decision_engine", "enable_auto_site_publish",
            "enable_run_manifest_extensions", "enable_auto_commit", "enable_auto_push",
            # Phase 8.5 Feature Flags
            "enable_massive_seed_fetcher", "enable_repository_expansion", "enable_archive_statistics",
            "enable_public_api_ingestion", "enable_skill_library_ingestion", "enable_prompt_library_ingestion",
            "enable_ide_rules_ingestion", "enable_system_prompt_ingestion", "enable_mcp_ingestion",
            # Phase 9 Feature Flags
            "enable_semantic_index_builder", "enable_entity_linker", "enable_related_entity_engine",
            "enable_knowledge_graph_builder", "enable_search_index_exporter", "enable_dashboard_data_generator",
            "enable_timeline_generator", "enable_index_manifest_generator", "enable_artifact_manifest_generator",
            "enable_phase9_reports"
        ]
        
        warnings = []
        errors = []
        
        # Check for unknown flags
        for flag in features.keys():
            if flag not in expected_flags:
                warnings.append(f"Unknown feature flag: {flag}")
                self.logger.warning(f"Unknown feature flag: {flag}")
                
        # Check for missing required flags
        for flag in expected_flags:
            if flag not in features:
                warnings.append(f"Missing feature flag: {flag} (assuming false)")
                
        validation_data = {
            "status": "pass" if not errors else "fail",
            "warnings": warnings,
            "errors": errors
        }
        
        # Ensure directories exist
        os.makedirs("reports", exist_ok=True)
        os.makedirs("data/metadata", exist_ok=True)
        
        self.save_json("data/metadata/feature_flag_validation.json", validation_data)
        
        # Generate markdown report
        md_content = "# Feature Flag Validation Report\n\n"
        md_content += f"**Status:** {validation_data['status']}\n\n"
        if errors:
            md_content += "## Errors\n"
            for e in errors:
                md_content += f"- {e}\n"
        if warnings:
            md_content += "## Warnings\n"
            for w in warnings:
                md_content += f"- {w}\n"
                
        if not errors and not warnings:
            md_content += "No issues found.\n"
            
        self.save_markdown("reports/feature_flag_validation.md", md_content)
        
        return {"records_processed": len(features), "errors": len(errors)}
