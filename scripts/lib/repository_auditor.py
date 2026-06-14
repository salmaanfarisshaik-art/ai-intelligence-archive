import os
from typing import Dict, Any
from scripts.lib.base_generator import BaseGenerator
from scripts.lib.serialization import save_json_deterministic

class RepositoryAuditor(BaseGenerator):
    def __init__(self):
        super().__init__("repository_auditor", phase=7)
        
    def generate(self) -> Dict[str, Any]:
        """
        Scans repository and reports health issues with severity levels.
        """
        findings = []
        
        # Check for stale .tmp files
        for root, _, files in os.walk("."):
            if ".git" in root or "venv" in root:
                continue
            for f in files:
                if f.endswith(".tmp"):
                    findings.append({"severity": "WARNING", "issue": f"Stale .tmp file found: {os.path.join(root, f)}"})
        
        # Check for missing crucial directories
        for d in ["data", "exports", "reports", "schemas"]:
            if not os.path.exists(d):
                findings.append({"severity": "ERROR", "issue": f"Missing critical directory: {d}"})
            
        os.makedirs("reports", exist_ok=True)
        save_json_deterministic("reports/repository_health.json", findings)
        
        md_content = "# Repository Audit Report\n\n"
        if not findings:
            md_content += "No issues found. Repository is healthy.\n"
        else:
            for f in findings:
                md_content += f"- **[{f['severity']}]**: {f['issue']}\n"
            
        self.save_markdown("reports/repository_audit.md", md_content)
        
        return {"records_processed": len(findings)}

    def run(self):
        self.generate()
