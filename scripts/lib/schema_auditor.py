import os
import json
from typing import Dict, Any
from scripts.lib.base_generator import BaseGenerator
from scripts.lib.serialization import save_json_deterministic

class SchemaAuditor(BaseGenerator):
    def __init__(self):
        super().__init__("schema_auditor", phase=7)
        
    def generate(self) -> Dict[str, Any]:
        """
        Audits data files to ensure they conform to basic schema requirements.
        """
        findings = []
        
        # Check all data json files for mandatory 'id' field
        for d in ["models", "datasets", "tools", "prompts", "benchmarks"]:
            path = f"data/{d}/data.json"
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            for idx, item in enumerate(data):
                                if "id" not in item:
                                    findings.append({
                                        "severity": "ERROR", 
                                        "issue": f"Missing 'id' in {d} at index {idx}"
                                    })
                    except Exception as e:
                        findings.append({"severity": "ERROR", "issue": f"Failed to parse {path}: {e}"})
        
        os.makedirs("reports", exist_ok=True)
        
        save_json_deterministic("reports/schema_audit.json", findings)
        
        md_content = "# Schema Audit Report\n\n"
        if not findings:
            md_content += "All checked data files conform to schema requirements.\n"
        else:
            for f in findings:
                md_content += f"- **[{f['severity']}]**: {f['issue']}\n"
                
        self.save_markdown("reports/schema_audit.md", md_content)
        
        return {"records_processed": len(findings)}

    def run(self):
        self.generate()
