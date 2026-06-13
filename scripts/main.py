import os
import sys
import json
import time
from datetime import datetime, timezone
import yaml
from scripts.lib.logger import setup_logger
from scripts.lib.source_metrics import metrics
from scripts.sync.benchmark_sync import BenchmarkSync
from scripts.sync.model_sync import ModelSync
from scripts.sync.prompt_sync import PromptSync
from scripts.sync.dataset_sync import DatasetSync
from scripts.sync.tool_sync import ToolSync
from scripts.sync.news_sync import NewsSync
from scripts.generate_indexes import main as generate_indexes_main
from scripts.generate_reports import generate_report
import scripts.commit_changes as commit_changes
from scripts.lib.config_loader import config
from scripts.lib.entity_indexer import EntityIndexer
from scripts.lib.search_index import SearchIndex
from scripts.lib.analytics import AnalyticsGenerator
from scripts.generate_docs import DocsGenerator
from scripts.lib.graph_exporter import GraphExporter
from scripts.exporters.json_exporter import JSONExporter
from scripts.exporters.csv_exporter import CSVExporter
from scripts.exporters.markdown_exporter import MarkdownExporter
from scripts.generate_dashboard import DashboardGenerator
import uuid

# Phase 5 Imports
from scripts.generate_manifests import ManifestGenerator
from scripts.exporters.graph_api_exporter import GraphAPIExporter
from scripts.lib.integrity_checker import IntegrityChecker
from scripts.release.snapshot_generator import SnapshotGenerator
from scripts.release.release_builder import ReleaseBuilder
from scripts.release.package_exporter import PackageExporter
from scripts.plugins.discovery import discover_plugins
from scripts.plugins.plugin_manager import PluginManager

# Phase 6 & Phase 7 Imports
from scripts.lib.interface_validator import InterfaceValidator
from scripts.lib.feature_flag_validator import FeatureFlagValidator
from scripts.site.site_generator import SiteGenerator
from scripts.lib.leaderboard_generator import LeaderboardGenerator
from scripts.lib.advanced_graph import AdvancedGraph
from scripts.lib.recommendation_engine import RecommendationEngine
from scripts.lib.governance_generator import GovernanceGenerator
from scripts.lib.repository_intelligence import RepositoryIntelligence
from scripts.lib.timeline_generator import TimelineGenerator
from scripts.lib.coverage_analysis import CoverageAnalysis
from scripts.lib.repository_auditor import RepositoryAuditor
from scripts.lib.self_documentation import SelfDocumentation
from scripts.lib.serialization import save_json_deterministic

logger = setup_logger("main")
LOCK_FILE = ".run.lock"
HEALTH_FILE = "run_health.json"

def create_lock():
    if os.path.exists(LOCK_FILE):
        logger.error(f"Lock file {LOCK_FILE} exists. Aborting to prevent overlapping runs.")
        sys.exit(1)
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "run_id": "phase2_run"}))

def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def write_health(run_id: str, status: str, modules_run: list, modules_failed: list, execution_time: float, records_processed: int, records_failed: int):
    health_data = {
        "run_id": run_id,
        "status": status,
        "modules_run": modules_run,
        "modules_failed": modules_failed,
        "total_runtime_seconds": execution_time,
        "records_processed": records_processed,
        "records_failed": records_failed,
        # Phase 2 observability metrics
        "api_calls_made": metrics.api_calls_made,
        "cache_hits": metrics.cache_hits,
        "cache_misses": metrics.cache_misses,
        "duplicates_removed": metrics.duplicates_removed,
        "external_sources_failed": metrics.external_sources_failed,
        # Phase 3 observability metrics
        "warning_count": 0,
        "error_count": len(modules_failed),
        "enrichment_statistics": {}
    }
    with open(HEALTH_FILE, "w", encoding="utf-8") as f:
        json.dump(health_data, f, indent=2)

def main():
    start_time = time.time()
    run_id = f"run_{int(start_time)}"
    create_lock()
    
    modules_run = []
    modules_failed = []
    total_records = 0
    total_failed = 0
    
    is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    logger.info(f"Starting pipeline. DRY_RUN={is_dry_run}")
    
    try:
        # Pre-flight / Load config
        if not os.path.exists("config/settings.yaml"):
            logger.error("Missing config/settings.yaml")
            raise Exception("Missing config")
            
        with open("config/settings.yaml", "r") as f:
            yaml.safe_load(f)
            
        # 1. Benchmark
        if config.is_sync_enabled("benchmark"):
            try:
                logger.info("Running benchmark_sync")
                sync = BenchmarkSync()
                records = sync.run()
                total_records += records
                modules_run.append("benchmark")
            except Exception as e:
                logger.error("benchmark_sync failed", exc_info=True)
                modules_failed.append("benchmark")
        else:
            logger.info("Skipping benchmark_sync (disabled in config)")
            
        # 2. Model
        if config.is_sync_enabled("model"):
            try:
                logger.info("Running model_sync")
                sync = ModelSync()
                records = sync.run()
                total_records += records
                modules_run.append("model")
            except Exception as e:
                logger.error("model_sync failed", exc_info=True)
                modules_failed.append("model")
        else:
            logger.info("Skipping model_sync (disabled in config)")
            
        # 3. Prompt
        if config.is_sync_enabled("prompt"):
            try:
                logger.info("Running prompt_sync")
                sync = PromptSync()
                records = sync.run()
                total_records += records
                modules_run.append("prompt")
            except Exception as e:
                logger.error("prompt_sync failed", exc_info=True)
                modules_failed.append("prompt")
        else:
            logger.info("Skipping prompt_sync (disabled in config)")
            
        # 4. Dataset
        if config.is_sync_enabled("dataset"):
            try:
                logger.info("Running dataset_sync")
                sync = DatasetSync()
                records = sync.run()
                total_records += records
                modules_run.append("dataset")
            except Exception as e:
                logger.error("dataset_sync failed", exc_info=True)
                modules_failed.append("dataset")
        else:
            logger.info("Skipping dataset_sync (disabled in config)")

        # 5. Tool
        if config.is_sync_enabled("tool"):
            try:
                logger.info("Running tool_sync")
                sync = ToolSync()
                records = sync.run()
                total_records += records
                modules_run.append("tool")
            except Exception as e:
                logger.error("tool_sync failed", exc_info=True)
                modules_failed.append("tool")
        else:
            logger.info("Skipping tool_sync (disabled in config)")

        # 6. News
        if config.is_sync_enabled("news"):
            try:
                logger.info("Running news_sync")
                sync = NewsSync()
                records = sync.run()
                total_records += records
                modules_run.append("news")
            except Exception as e:
                logger.error("news_sync failed", exc_info=True)
                modules_failed.append("news")
        else:
            logger.info("Skipping news_sync (disabled in config)")
            
        # Generate indexes
        try:
            logger.info("Running generate_indexes (legacy)")
            generate_indexes_main()
            modules_run.append("indexes_legacy")
        except Exception as e:
            logger.error("generate_indexes failed", exc_info=True)
            modules_failed.append("indexes_legacy")

        # Phase 4 - Post-Processing Pipeline
        
        # 8. Entity Indexing
        try:
            logger.info("Running EntityIndexer")
            EntityIndexer().generate()
            modules_run.append("entity_indexer")
        except Exception as e:
            logger.error("EntityIndexer failed", exc_info=True)
            modules_failed.append("entity_indexer")
            
        # 9. Search Indexing
        try:
            logger.info("Running SearchIndex")
            SearchIndex().generate()
            modules_run.append("search_index")
        except Exception as e:
            logger.error("SearchIndex failed", exc_info=True)
            modules_failed.append("search_index")

        # 10. Analytics Generation
        try:
            logger.info("Running AnalyticsGenerator")
            AnalyticsGenerator().generate()
            modules_run.append("analytics")
        except Exception as e:
            logger.error("AnalyticsGenerator failed", exc_info=True)
            modules_failed.append("analytics")

        # 11. Documentation Generation
        try:
            logger.info("Running DocsGenerator")
            DocsGenerator().generate()
            modules_run.append("docs")
        except Exception as e:
            logger.error("DocsGenerator failed", exc_info=True)
            modules_failed.append("docs")
            
        # 12. Relationship Graph Export
        try:
            logger.info("Running GraphExporter")
            GraphExporter().generate()
            modules_run.append("graph_exporter")
        except Exception as e:
            logger.error("GraphExporter failed", exc_info=True)
            modules_failed.append("graph_exporter")
            
        # 13. Multi-Format Data Export
        try:
            logger.info("Running Exporters")
            JSONExporter().export()
            CSVExporter().export()
            MarkdownExporter().export()
            modules_run.append("exporters")
        except Exception as e:
            logger.error("Exporters failed", exc_info=True)
            modules_failed.append("exporters")
        # 14. Generate Reports (Phase 3 Legacy)
        try:
            logger.info("Running generate_report")
            generate_report()
            modules_run.append("report_legacy")
        except Exception as e:
            logger.error("generate_report failed", exc_info=True)
            modules_failed.append("report_legacy")

        # 15. Dashboard Generation
        try:
            logger.info("Running DashboardGenerator")
            DashboardGenerator().generate()
            modules_run.append("dashboard")
        except Exception as e:
            logger.error("DashboardGenerator failed", exc_info=True)
            modules_failed.append("dashboard")
            
        # Phase 5 - Automation & Ecosystem Layer

        # 16. Plugin Discovery & Execution
        try:
            logger.info("Running Plugin Discovery & Execution")
            if config.is_feature_enabled("enable_plugin_system"):
                discover_plugins()
                pm = PluginManager(config.features)
                pm.execute_all({})
                modules_run.append("plugins")
            else:
                logger.info("Plugin system disabled in config")
        except Exception as e:
            logger.error("PluginManager failed", exc_info=True)
            modules_failed.append("plugins")

        # 17. Manifest Generation
        try:
            logger.info("Running ManifestGenerator")
            ManifestGenerator().generate()
            modules_run.append("manifests")
        except Exception as e:
            logger.error("ManifestGenerator failed", exc_info=True)
            modules_failed.append("manifests")

        # 18. Graph API Export
        try:
            logger.info("Running GraphAPIExporter")
            GraphAPIExporter().generate()
            modules_run.append("graph_api")
        except Exception as e:
            logger.error("GraphAPIExporter failed", exc_info=True)
            modules_failed.append("graph_api")

        # 19. Repository Integrity Check
        try:
            logger.info("Running IntegrityChecker")
            IntegrityChecker().check_all()
            modules_run.append("integrity_checker")
        except Exception as e:
            logger.error("IntegrityChecker failed", exc_info=True)
            modules_failed.append("integrity_checker")

        # 20. Snapshot Generation
        try:
            logger.info("Running SnapshotGenerator")
            SnapshotGenerator().generate()
            modules_run.append("snapshot_generator")
        except Exception as e:
            logger.error("SnapshotGenerator failed", exc_info=True)
            modules_failed.append("snapshot_generator")

        # 21. Release Packaging
        try:
            logger.info("Running ReleaseBuilder & PackageExporter")
            ReleaseBuilder().generate()
            PackageExporter().export()
            modules_run.append("release_builder")
        except Exception as e:
            logger.error("ReleaseBuilder/PackageExporter failed", exc_info=True)
            modules_failed.append("release_builder")

        # --- Phase 6 & Phase 7 Execution Block ---
        
        # 1. Validation Layer
        try:
            logger.info("Running InterfaceValidator")
            InterfaceValidator().run()
            modules_run.append("interface_validator")
        except Exception:
            logger.error("InterfaceValidator failed", exc_info=True)
            modules_failed.append("interface_validator")

        try:
            logger.info("Running FeatureFlagValidator")
            FeatureFlagValidator().run()
            modules_run.append("feature_flag_validator")
        except Exception:
            logger.error("FeatureFlagValidator failed", exc_info=True)
            modules_failed.append("feature_flag_validator")

        # 2. Phase 6: Ecosystem Layer
        if config.is_feature_enabled("enable_static_site"):
            try:
                SiteGenerator().run()
                modules_run.append("site_generator")
            except Exception:
                logger.error("SiteGenerator failed", exc_info=True)
                modules_failed.append("site_generator")
                
        if config.is_feature_enabled("enable_leaderboards"):
            try:
                LeaderboardGenerator().run()
                modules_run.append("leaderboard_generator")
            except Exception:
                logger.error("LeaderboardGenerator failed", exc_info=True)
                modules_failed.append("leaderboard_generator")

        if config.is_feature_enabled("enable_knowledge_graph"):
            try:
                AdvancedGraph().run()
                modules_run.append("advanced_graph")
            except Exception:
                logger.error("AdvancedGraph failed", exc_info=True)
                modules_failed.append("advanced_graph")

        if config.is_feature_enabled("enable_recommendations"):
            try:
                RecommendationEngine().run()
                modules_run.append("recommendation_engine")
            except Exception:
                logger.error("RecommendationEngine failed", exc_info=True)
                modules_failed.append("recommendation_engine")

        if config.is_feature_enabled("enable_governance_docs"):
            try:
                GovernanceGenerator().run()
                modules_run.append("governance_generator")
            except Exception:
                logger.error("GovernanceGenerator failed", exc_info=True)
                modules_failed.append("governance_generator")

        # 3. Phase 7: Intelligence & Governance Layer
        if config.is_feature_enabled("enable_repository_intelligence"):
            try:
                RepositoryIntelligence().run()
                modules_run.append("repository_intelligence")
            except Exception:
                logger.error("RepositoryIntelligence failed", exc_info=True)
                modules_failed.append("repository_intelligence")

        if config.is_feature_enabled("enable_timeline_generation"):
            try:
                TimelineGenerator().run()
                modules_run.append("timeline_generator")
            except Exception:
                logger.error("TimelineGenerator failed", exc_info=True)
                modules_failed.append("timeline_generator")

        if config.is_feature_enabled("enable_coverage_analysis"):
            try:
                CoverageAnalysis().run()
                modules_run.append("coverage_analysis")
            except Exception:
                logger.error("CoverageAnalysis failed", exc_info=True)
                modules_failed.append("coverage_analysis")

        if config.is_feature_enabled("enable_self_documentation"):
            try:
                SelfDocumentation().run()
                modules_run.append("self_documentation")
            except Exception:
                logger.error("SelfDocumentation failed", exc_info=True)
                modules_failed.append("self_documentation")

        # 4. Repository Auditor (Runs last to audit all newly generated files)
        if config.is_feature_enabled("enable_repository_audit"):
            try:
                RepositoryAuditor().run()
                modules_run.append("repository_auditor")
            except Exception:
                logger.error("RepositoryAuditor failed", exc_info=True)
                modules_failed.append("repository_auditor")

        # 5. Run Manifest Generation
        try:
            manifest_data = {
                "run_id": run_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "modules_run": modules_run,
                "modules_failed": modules_failed,
                "dry_run": is_dry_run
            }
            save_json_deterministic("reports/run_manifest.json", manifest_data)
        except Exception:
            logger.error("Failed to generate run_manifest", exc_info=True)


        # Validate outputs & Commit changes
        if not is_dry_run:
            try:
                logger.info("Running commit_changes")
                commit_changes.main()
                modules_run.append("commit")
            except Exception as e:
                logger.error("commit_changes failed", exc_info=True)
                modules_failed.append("commit")
        else:
            logger.info("DRY_RUN=true: Skipping commit_changes")

    finally:
        remove_lock()
        execution_time = time.time() - start_time
        status = "success"
        if len(modules_failed) > 0:
            status = "partial_failure" if len(modules_run) > 0 else "failed"
            
        write_health(run_id, status, modules_run, modules_failed, execution_time, total_records, total_failed)
        logger.info(f"Pipeline completed with status: {status} in {execution_time:.2f}s")

if __name__ == "__main__":
    main()
