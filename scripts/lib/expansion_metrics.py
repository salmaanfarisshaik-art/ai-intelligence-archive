import os
from datetime import datetime, timezone
from scripts.lib.serialization import save_json_deterministic
from scripts.lib.logger import setup_logger

logger = setup_logger("expansion_metrics")

class ExpansionMetrics:
    def __init__(self):
        self.metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sources_processed": 0,
            "new_entities_added": 0,
            "duplicates_removed": 0,
            "runtime_seconds": 0.0,
            "growth_by_category": {}
        }
        
    def generate_report(self):
        os.makedirs("reports", exist_ok=True)
        save_json_deterministic("reports/expansion_metrics.json", self.metrics)
        
        md_lines = [
            "# Expansion Metrics Report",
            f"**Timestamp:** {self.metrics['timestamp']}",
            f"**Sources Processed:** {self.metrics['sources_processed']}",
            f"**New Entities Added:** {self.metrics['new_entities_added']}",
            f"**Duplicates Removed:** {self.metrics['duplicates_removed']}",
            f"**Runtime (s):** {self.metrics['runtime_seconds']:.2f}",
            "",
            "## Growth By Category"
        ]
        for cat, growth in self.metrics["growth_by_category"].items():
            md_lines.append(f"- **{cat}:** +{growth}")
            
        with open("reports/expansion_metrics.md", "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        logger.info("Expansion metrics report generated.")
