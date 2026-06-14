import os
import json
from typing import Dict, Any
from scripts.lib.base_generator import BaseGenerator
from scripts.lib.serialization import save_json_deterministic

class LeaderboardGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("leaderboard_generator", phase=6)
        
    def generate(self) -> Dict[str, Any]:
        """
        Generates deterministic leaderboards from Phase 1-5 outputs.
        """
        leaderboards = {
            "top_models": [],
            "top_datasets": []
        }
        
        models_path = "data/models/data.json"
        if os.path.exists(models_path):
            with open(models_path, "r", encoding="utf-8") as f:
                models = json.load(f)
                
                # Rank by metadata density (number of keys)
                def score_m(m):
                    return len(m.keys()) + len(m.get("tags", []))
                    
                sorted_models = sorted(models, key=lambda x: (-score_m(x), x.get("id", "")))
                leaderboards["top_models"] = [{"id": m.get("id"), "score": score_m(m)} for m in sorted_models[:10]]
                
        datasets_path = "data/datasets/data.json"
        if os.path.exists(datasets_path):
            with open(datasets_path, "r", encoding="utf-8") as f:
                datasets = json.load(f)
                
                def score_d(d):
                    return len(d.keys()) + len(d.get("tags", []))
                    
                sorted_datasets = sorted(datasets, key=lambda x: (-score_d(x), x.get("id", "")))
                leaderboards["top_datasets"] = [{"id": d.get("id"), "score": score_d(d)} for d in sorted_datasets[:10]]
                
        os.makedirs("data/metadata", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        os.makedirs("site", exist_ok=True)
        
        save_json_deterministic("data/metadata/leaderboards.json", leaderboards)
        save_json_deterministic("site/leaderboards.json", leaderboards)
        
        md_content = "# AI Ecosystem Leaderboards\n\n## Top Models\n"
        for m in leaderboards["top_models"]:
            md_content += f"- {m['id']} (Score: {m['score']})\n"
            
        md_content += "\n## Top Datasets\n"
        for d in leaderboards["top_datasets"]:
            md_content += f"- {d['id']} (Score: {d['score']})\n"
            
        self.save_markdown("reports/leaderboards.md", md_content)
        
        return {"records_processed": len(leaderboards["top_models"]) + len(leaderboards["top_datasets"])}

    def run(self):
        self.generate()
