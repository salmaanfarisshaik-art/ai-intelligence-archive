import os
import json
import requests
from datetime import datetime, timezone
from scripts.lib.logger import setup_logger
from scripts.lib.serialization import save_json_deterministic
from scripts.lib.base_generator import BaseGenerator

logger = setup_logger("source_validator")

class SourceValidator(BaseGenerator):
    def __init__(self):
        super().__init__("source_validator", phase=8.5)
        self.registry_path = os.path.join("data", "metadata", "source_registry.json")

    def run(self, is_dry_run: bool = False):
        logger.info(f"Running SourceValidator (DRY_RUN={is_dry_run})")
        
        if not os.path.exists(self.registry_path):
            logger.warning(f"No source registry found at {self.registry_path}")
            return {"status": "skipped", "reason": "no_registry"}
            
        with open(self.registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        validation_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sources_validated": 0,
            "sources_passed": 0,
            "sources_failed": 0,
            "details": []
        }

        unique_urls = set()
        
        for source_id, source_data in registry.items():
            if not source_data.get("enabled", True):
                continue
                
            validation_results["sources_validated"] += 1
            url = source_data.get("url", "")
            
            detail = {
                "source_id": source_id,
                "name": source_data.get("name"),
                "url": url,
                "passed": False,
                "errors": [],
                "warnings": []
            }
            
            # Uniqueness check
            if url in unique_urls:
                detail["errors"].append("Duplicate URL detected")
            else:
                unique_urls.add(url)
                
            # Basic reachability check (skip in dry run or implement mock)
            if not is_dry_run:
                try:
                    # Simple HEAD request to check if it's reachable. Some repos might reject HEAD, fallback to GET
                    resp = requests.head(url, timeout=10, allow_redirects=True)
                    if resp.status_code >= 400:
                        resp = requests.get(url, timeout=10, stream=True)
                        if resp.status_code >= 400:
                            detail["errors"].append(f"Unreachable URL: HTTP {resp.status_code}")
                except Exception as e:
                    detail["errors"].append(f"Connection error: {str(e)}")
            else:
                detail["warnings"].append("Reachability check skipped (DRY_RUN)")
                
            # License check
            license_val = source_data.get("license", "").lower()
            if not license_val or license_val == "unknown":
                detail["warnings"].append("Missing or unknown license")
                
            if len(detail["errors"]) == 0:
                detail["passed"] = True
                validation_results["sources_passed"] += 1
            else:
                validation_results["sources_failed"] += 1
                
            validation_results["details"].append(detail)
            
            # Record last validation timestamp
            source_data["last_validation"] = validation_results["timestamp"]
            
        # Quarantine policy: If a source repeatedly fails (e.g. we would track consecutive failures), disable it.
        # For now, we will flag it if it failed this run.
        for detail in validation_results["details"]:
            if not detail["passed"]:
                logger.warning(f"Source {detail['source_id']} failed validation: {detail['errors']}")
                
        # Generate Reports
        os.makedirs("reports", exist_ok=True)
        save_json_deterministic("reports/source_validation.json", validation_results)
        
        # Markdown Report
        md_lines = [
            "# Source Validation Report",
            "",
            f"**Timestamp:** {validation_results['timestamp']}",
            f"**Total Validated:** {validation_results['sources_validated']}",
            f"**Passed:** {validation_results['sources_passed']}",
            f"**Failed:** {validation_results['sources_failed']}",
            "",
            "## Details",
            ""
        ]
        
        for d in validation_results["details"]:
            status = "✅ PASS" if d["passed"] else "❌ FAIL"
            md_lines.append(f"### {d['name']} ({status})")
            md_lines.append(f"- **URL:** {d['url']}")
            if d["errors"]:
                md_lines.append("- **Errors:**")
                for e in d["errors"]:
                    md_lines.append(f"  - {e}")
            if d["warnings"]:
                md_lines.append("- **Warnings:**")
                for w in d["warnings"]:
                    md_lines.append(f"  - {w}")
            md_lines.append("")
            
        self.save_markdown("reports/source_validation.md", "\n".join(md_lines))
        
        # Save updated registry if not dry run
        if not is_dry_run:
            save_json_deterministic(self.registry_path, registry)
            
        return validation_results
