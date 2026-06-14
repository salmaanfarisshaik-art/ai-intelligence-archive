import os
from typing import Dict, Any
from scripts.lib.base_generator import BaseGenerator

class DependencyReport(BaseGenerator):
    def __init__(self):
        super().__init__("dependency_report", phase=7)
        
    def generate(self) -> Dict[str, Any]:
        """
        Analyzes requirements.txt and python files to report dependencies.
        """
        req_path = "requirements.txt"
        dev_req_path = "requirements-dev.txt"
        
        dependencies = []
        if os.path.exists(req_path):
            with open(req_path, "r", encoding="utf-8") as f:
                dependencies.extend([line.strip() for line in f if line.strip() and not line.startswith("#")])
                
        dev_dependencies = []
        if os.path.exists(dev_req_path):
            with open(dev_req_path, "r", encoding="utf-8") as f:
                dev_dependencies.extend([line.strip() for line in f if line.strip() and not line.startswith("#")])
                
        md_content = "# Dependency Report\n\n"
        md_content += "## Core Dependencies\n"
        for d in dependencies:
            md_content += f"- `{d}`\n"
            
        md_content += "\n## Development Dependencies\n"
        for d in dev_dependencies:
            md_content += f"- `{d}`\n"
            
        os.makedirs("reports", exist_ok=True)
        self.save_markdown("reports/dependency_report.md", md_content)
        
        return {"records_processed": len(dependencies) + len(dev_dependencies)}

    def run(self):
        self.generate()
