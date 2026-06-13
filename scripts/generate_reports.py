import os
import json
from datetime import datetime, timezone
from scripts.lib.config_loader import config
from scripts.lib.logger import setup_logger

logger = setup_logger("generate_reports")

def generate_report():
    # Only generate if enabled in config
    if not config.features.get("generate_markdown_reports", True) and not config.is_feature_enabled("generate_markdown_reports"):
        logger.info("Markdown report generation disabled in config.")
        return

    health_path = "run_health.json"
    if not os.path.exists(health_path):
        logger.warning(f"Could not find {health_path} to generate report.")
        return

    try:
        with open(health_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, "latest_run.md")
        
        # Atomic write semantics (Phase 3 Atomic Persistence Guarantee)
        tmp_path = report_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(f"# Pipeline Execution Report\n\n")
            f.write(f"**Run ID**: {data.get('run_id')}\n")
            f.write(f"**Status**: {data.get('status')}\n")
            f.write(f"**Execution Time**: {data.get('total_runtime_seconds', 0):.2f}s\n\n")
            f.write(f"## Metrics\n")
            f.write(f"- Records Processed: {data.get('records_processed')}\n")
            f.write(f"- API Calls Made: {data.get('api_calls_made')}\n")
            f.write(f"- Cache Hits: {data.get('cache_hits')}\n")
            f.write(f"- Duplicates Removed: {data.get('duplicates_removed')}\n")
            f.write(f"- External Sources Failed: {data.get('external_sources_failed', [])}\n")
            f.write(f"- Phase 3 Warning Count: {data.get('warning_count', 0)}\n")
            f.write(f"- Phase 3 Error Count: {data.get('error_count', 0)}\n")
        
        os.replace(tmp_path, report_path)
        logger.info(f"Successfully generated {report_path}")
    except Exception as e:
        # Phase 3 Invariant: Report generation failures must never interrupt the ingestion pipeline
        logger.error(f"Failed to generate report: {e}")

if __name__ == "__main__":
    generate_report()
