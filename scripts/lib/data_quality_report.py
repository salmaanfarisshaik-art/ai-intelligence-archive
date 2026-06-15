import os
from datetime import datetime, timezone
from scripts.lib.serialization import save_json_deterministic
from scripts.lib.logger import setup_logger

logger = setup_logger("data_quality_report")

class DataQualityReport:
    def __init__(self):
        self.metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "records_missing_description": 0,
            "records_missing_license": 0,
            "records_missing_provenance": 0,
            "duplicate_aliases_detected": 0,
            "invalid_schema_count": 0,
            "category_coverage_percentages": {}
        }
        
    def generate_report(self):
        os.makedirs("reports", exist_ok=True)
        save_json_deterministic("reports/data_quality_report.json", self.metrics)
        
        md_lines = [
            "# Data Quality Report",
            f"**Timestamp:** {self.metrics['timestamp']}",
            f"**Missing Description:** {self.metrics['records_missing_description']}",
            f"**Missing License:** {self.metrics['records_missing_license']}",
            f"**Missing Provenance:** {self.metrics['records_missing_provenance']}",
            f"**Duplicate Aliases:** {self.metrics['duplicate_aliases_detected']}",
            f"**Invalid Schemas:** {self.metrics['invalid_schema_count']}",
            "",
            "## Category Coverage"
        ]
        for cat, cov in self.metrics["category_coverage_percentages"].items():
            md_lines.append(f"- **{cat}:** {cov}%")
            
        with open("reports/data_quality_report.md", "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        logger.info("Data quality report generated.")
