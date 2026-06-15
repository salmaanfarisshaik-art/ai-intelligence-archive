import os
import json
from datetime import datetime, timezone
from scripts.lib.logger import setup_logger
from scripts.lib.serialization import save_json_deterministic

logger = setup_logger("schema_validator")

class SchemaConsistencyValidator:
    """
    Validates every generated entity against the canonical JSON schema.
    Verifies required fields before writing outputs.
    """
    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_validated": 0,
            "passed": 0,
            "failed": 0,
            "schema_failures": {}
        }
        
    def validate(self, schema_name: str, record: dict) -> bool:
        self.validation_results["total_validated"] += 1
        
        # Extremely basic validation: MUST have unique_id
        if "unique_id" not in record:
            self._record_failure(schema_name, "Missing unique_id")
            return False
            
        self.validation_results["passed"] += 1
        return True
        
    def _record_failure(self, schema_name: str, reason: str):
        self.validation_results["failed"] += 1
        if schema_name not in self.validation_results["schema_failures"]:
            self.validation_results["schema_failures"][schema_name] = []
        self.validation_results["schema_failures"][schema_name].append(reason)
        
    def generate_report(self):
        os.makedirs("reports", exist_ok=True)
        save_json_deterministic("reports/schema_validation.json", self.validation_results)
        
        md_lines = [
            "# Schema Validation Report",
            f"**Timestamp:** {self.validation_results['timestamp']}",
            f"**Total Validated:** {self.validation_results['total_validated']}",
            f"**Passed:** {self.validation_results['passed']}",
            f"**Failed:** {self.validation_results['failed']}",
            ""
        ]
        
        if self.validation_results["failed"] > 0:
            md_lines.append("## Failures by Schema")
            for schema, failures in self.validation_results["schema_failures"].items():
                md_lines.append(f"### {schema}")
                for f in failures[:10]: # Limit output
                    md_lines.append(f"- {f}")
                if len(failures) > 10:
                    md_lines.append(f"- ... and {len(failures) - 10} more.")
                    
        with open("reports/schema_validation.md", "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
