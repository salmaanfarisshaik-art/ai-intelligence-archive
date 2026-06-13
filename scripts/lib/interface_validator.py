import os
import json
from typing import Dict, Any
from scripts.lib.base_generator import BaseGenerator

class InterfaceValidator(BaseGenerator):
    def __init__(self):
        super().__init__("interface_validator", phase=6)
        
    def generate(self) -> Dict[str, Any]:
        """
        Validates Phase 1-5 outputs and contracts.
        """
        errors = []
        warnings = []
        
        # 1. Directory Checks
        required_dirs = ["data/models", "data/papers", "data/datasets", "data/tools"]
        for d in required_dirs:
            if not os.path.isdir(d):
                errors.append(f"Missing required directory: {d}")
                
        # 2. Contract Checks
        contract_path = "data/metadata/repository_contract.json"
        if os.path.exists(contract_path):
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
                if contract.get("phase1_schema_version") != "1.0.0":
                    errors.append("Contract violation: Phase 1 schema version mismatch.")
        else:
            warnings.append("repository_contract.json not found.")

        # 3. Dependency Checks
        dep_path = "data/metadata/dependency_manifest.json"
        if os.path.exists(dep_path):
            with open(dep_path, "r", encoding="utf-8") as f:
                deps = json.load(f)
                for generator, info in deps.items():
                    for req_file in info.get("depends_on", []):
                        if not os.path.exists(req_file):
                            # It's a warning because some modules might be disabled or not run yet
                            warnings.append(f"{generator} dependency missing: {req_file}")
        else:
            warnings.append("dependency_manifest.json not found.")
            
        validation_data = {
            "status": "pass" if not errors else "fail",
            "warnings": warnings,
            "errors": errors
        }
        
        os.makedirs("reports", exist_ok=True)
        os.makedirs("data/metadata", exist_ok=True)
        
        self.save_json("data/metadata/interface_validation.json", validation_data)
        
        md_content = "# Interface Validation Report\n\n"
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
            md_content += "No interface issues found.\n"
            
        self.save_markdown("reports/interface_validation.md", md_content)
        
        return {"errors": len(errors)}
