import os
from typing import Dict, Any
from scripts.lib.base_generator import BaseGenerator
from scripts.lib.serialization import save_json_deterministic

class RepositoryMetrics(BaseGenerator):
    def __init__(self):
        super().__init__("repository_metrics", phase=7)
        
    def generate(self) -> Dict[str, Any]:
        """
        Calculates and stores metrics about the repository itself.
        """
        metrics = {
            "python_files": 0,
            "markdown_files": 0,
            "json_files": 0,
            "yaml_files": 0
        }
        
        for root, _, files in os.walk("."):
            if ".git" in root or "venv" in root:
                continue
            for f in files:
                if f.endswith(".py"): metrics["python_files"] += 1
                elif f.endswith(".md"): metrics["markdown_files"] += 1
                elif f.endswith(".json"): metrics["json_files"] += 1
                elif f.endswith(".yaml") or f.endswith(".yml"): metrics["yaml_files"] += 1
                
        os.makedirs("data/metadata", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        
        save_json_deterministic("data/metadata/repo_metrics.json", metrics)
        
        md_content = "# Repository Metrics\n\n"
        for k, v in metrics.items():
            md_content += f"- **{k}**: {v}\n"
            
        self.save_markdown("reports/repository_metrics.md", md_content)
        
        return {"records_processed": sum(metrics.values())}

    def run(self):
        self.generate()
