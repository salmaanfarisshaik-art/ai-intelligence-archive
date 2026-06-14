import os
import json
from typing import Dict, Any
from scripts.lib.base_generator import BaseGenerator
from scripts.lib.serialization import save_json_deterministic

class CoverageAnalyzer(BaseGenerator):
    def __init__(self):
        super().__init__("coverage_analyzer", phase=7)
        
    def generate(self) -> Dict[str, Any]:
        """
        Generates ecosystem coverage metrics deterministically.
        """
        metrics = {
            "models_covered": 0,
            "datasets_covered": 0,
            "tools_covered": 0
        }
        
        for k, d in [("models_covered", "models"), ("datasets_covered", "datasets"), ("tools_covered", "tools")]:
            path = f"data/{d}/data.json"
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    metrics[k] = len(data)
        
        os.makedirs("data/metadata", exist_ok=True)
        save_json_deterministic("data/metadata/coverage_metrics.json", metrics)
        
        md_content = "# Ecosystem Coverage\n\n"
        for k, v in metrics.items():
            md_content += f"- **{k}**: {v}\n"
        self.save_markdown("reports/coverage_report.md", md_content)
        
        return {"records_processed": sum(metrics.values())}

    def run(self):
        self.generate()
