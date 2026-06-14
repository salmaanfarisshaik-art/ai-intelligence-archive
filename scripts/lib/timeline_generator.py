import os
import json
from typing import Dict, Any
from scripts.lib.base_generator import BaseGenerator
from scripts.lib.serialization import save_json_deterministic

class TimelineGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("timeline_generator", phase=6)
        
    def generate(self) -> Dict[str, Any]:
        """
        Generates historical timeline deterministically from releases/snapshots.
        """
        timeline = []
        
        timeline.append({"date": "2023-01-01", "event": "Repository initialized", "type": "init"})
        
        releases_dir = "releases"
        if os.path.exists(releases_dir):
            for file in sorted(os.listdir(releases_dir)):
                if file.endswith(".json"):
                    # basic parsing assuming filename contains date
                    date_str = file.replace("release_", "").replace(".json", "")
                    timeline.append({"date": date_str, "event": f"Release {file}", "type": "release"})
        
        # Sort timeline deterministically by date
        timeline.sort(key=lambda x: (x["date"], x["event"]))
        
        os.makedirs("data/metadata", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        
        save_json_deterministic("data/metadata/timeline.json", timeline)
        
        md_content = "# Historical Timeline\n\n"
        for t in timeline:
            md_content += f"- **{t['date']}**: {t['event']}\n"
        self.save_markdown("reports/timeline.md", md_content)
        
        return {"records_processed": len(timeline)}

    def run(self):
        self.generate()
