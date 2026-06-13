import os
import json
from datetime import datetime, timezone
from typing import Dict, Any

from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("generate_dashboard")

class DashboardGenerator:
    def __init__(self):
        self.reports_dir = "reports"
        self.metadata_dir = os.path.join("data", "metadata")
        os.makedirs(self.reports_dir, exist_ok=True)

    def _atomic_write(self, filepath: str, content: str):
        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        if is_dry_run:
            logger.info(f"DRY RUN: Would have saved dashboard to {filepath}")
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
        if not config.is_feature_enabled("enable_dashboard_generation"):
            logger.info("Dashboard generation is disabled in config.")
            return

        logger.info("Generating repository dashboard...")
        
        health_path = "run_health.json"
        analytics_path = os.path.join(self.metadata_dir, "analytics.json")
        
        health_data = {}
        if os.path.exists(health_path):
            try:
                with open(health_path, "r", encoding="utf-8") as f:
                    health_data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read {health_path}: {e}")
                
        analytics_data = {}
        if os.path.exists(analytics_path):
            try:
                with open(analytics_path, "r", encoding="utf-8") as f:
                    analytics_data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read {analytics_path}: {e}")
                
        try:
            # Prepare project status json
            project_status = {
                "latest_sync_time": datetime.now(timezone.utc).isoformat(),
                "status": health_data.get("status", "unknown"),
                "connectors": {
                    "run": health_data.get("modules_run", []),
                    "failed": health_data.get("modules_failed", [])
                },
                "entity_counts": analytics_data.get("total_entities", 0),
                "cache_statistics": {
                    "hits": health_data.get("cache_hits", 0),
                    "misses": health_data.get("cache_misses", 0)
                },
                "warning_count": health_data.get("warning_count", 0),
                "error_count": health_data.get("error_count", 0)
            }
            
            self._atomic_write(
                os.path.join(self.reports_dir, "project_status.json"),
                json.dumps(project_status, indent=2, ensure_ascii=False)
            )
            
            # Prepare dashboard md
            md_lines = [
                "# AI Intelligence Archive Dashboard",
                "",
                f"**Last Updated**: {project_status['latest_sync_time']}",
                f"**Status**: {project_status['status']}",
                "",
                "## Sync Status",
                f"- **Successful Connectors**: {', '.join(project_status['connectors']['run']) if project_status['connectors']['run'] else 'None'}",
                f"- **Failed Connectors**: {', '.join(project_status['connectors']['failed']) if project_status['connectors']['failed'] else 'None'}",
                "",
                "## Statistics",
                f"- **Total Entities**: {project_status['entity_counts']}",
                f"- **Cache Hits**: {project_status['cache_statistics']['hits']}",
                f"- **Cache Misses**: {project_status['cache_statistics']['misses']}",
                f"- **Warnings**: {project_status['warning_count']}",
                f"- **Errors**: {project_status['error_count']}"
            ]
            
            self._atomic_write(
                os.path.join(self.reports_dir, "dashboard.md"),
                "\n".join(md_lines) + "\n"
            )
            
            logger.info("Dashboard generated successfully.")
        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")

if __name__ == "__main__":
    DashboardGenerator().generate()
