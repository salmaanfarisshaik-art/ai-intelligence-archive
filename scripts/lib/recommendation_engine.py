import os
import json
from typing import Dict, Any, List
from scripts.lib.base_generator import BaseGenerator
from scripts.lib.serialization import save_json_deterministic

class RecommendationEngine(BaseGenerator):
    def __init__(self):
        super().__init__("recommendation_engine", phase=6)
        
    def _compute_jaccard(self, list1: List[str], list2: List[str]) -> float:
        set1, set2 = set(list1), set(list2)
        if not set1 and not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    def generate(self) -> Dict[str, Any]:
        """
        Generates deterministic recommendations based on metadata overlap.
        """
        recommendations = {}
        
        models_path = "data/models/data.json"
        models = []
        if os.path.exists(models_path):
            with open(models_path, "r", encoding="utf-8") as f:
                models = json.load(f)
                
        # Simple Jaccard similarity based on tags
        for i, m1 in enumerate(models):
            id1 = m1.get("id")
            if not id1:
                continue
                
            tags1 = m1.get("tags", []) + m1.get("ai_tags", [])
            # Convert to strings and lower case just to be safe
            tags1 = [str(t).lower() for t in tags1 if t]
            related = []
            
            for j, m2 in enumerate(models):
                if i == j:
                    continue
                id2 = m2.get("id")
                if not id2:
                    continue
                tags2 = m2.get("tags", []) + m2.get("ai_tags", [])
                tags2 = [str(t).lower() for t in tags2 if t]
                
                score = self._compute_jaccard(tags1, tags2)
                if score > 0.05: # Minimum threshold
                    related.append({"id": id2, "score": round(score, 3)})
            
            # Sort deterministically
            related.sort(key=lambda x: (-x["score"], x["id"]))
            
            recommendations[id1] = {
                "related_models": related[:5],
                "related_papers": [] # Placeholder for future
            }
                        
        os.makedirs("data/metadata", exist_ok=True)
        os.makedirs("site", exist_ok=True)
        
        save_json_deterministic("data/metadata/recommendations.json", recommendations)
        save_json_deterministic("site/recommendations.json", recommendations)
        
        return {"records_processed": len(recommendations)}

    def run(self):
        self.generate()
