import os
import json
import time
from typing import Dict, Any

from scripts.lib.base_generator import BaseGenerator, ArtifactResult, BuildContext
from scripts.lib.artifact_utils import atomic_write_json_artifact
from scripts.lib.serialization import save_markdown_deterministic

class TimelineGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("timeline_generator", phase=9, version="1.0.0")
        self.output_file = os.path.join("site", "timeline.json")
        self.schema_path = os.path.join("schemas", "timeline.schema.json")
        self.report_file = os.path.join("reports", "timeline_report.md")
        
    def generate(self, context: BuildContext = None) -> ArtifactResult:
        start_time = time.time()
        result = ArtifactResult(
            generator_name=self.name,
            generator_version=self.version
        )
        
        timeline = []
        
        # We can extract timeline events from canonical entities
        # E.g. models have a creation date or retrieval date
        data_dir = os.path.join("data", "processed")
        domains = sorted(os.listdir(data_dir))
        for domain in domains:
            domain_dir = os.path.join(data_dir, domain)
            if not os.path.isdir(domain_dir):
                continue
                
            data_file = os.path.join(domain_dir, "data.json")
            if not os.path.exists(data_file):
                continue
                
            with open(data_file, "r", encoding="utf-8") as f:
                entities = json.load(f)
                
            for entity in entities:
                date_str = entity.get("retrieval_timestamp")
                if date_str:
                    # just extract YYYY-MM
                    year_month = date_str[:7]
                    name = entity.get("name", entity.get("title", entity.get("unique_id", "")))
                    timeline.append({
                        "date": year_month + "-01", # Ensure valid date format YYYY-MM-DD
                        "description": f"Added {domain} entity: {name}",
                        "event_type": "entity_added",
                        "entity_id": entity.get("unique_id")
                    })
                    
        # Sort deterministically
        timeline = sorted(timeline, key=lambda x: (x["date"], x["entity_id"], x["description"]))
        
        # Limit timeline size for frontend payload
        # or aggregate by month
        aggregated = {}
        for t in timeline:
            key = t["date"]
            if key not in aggregated:
                aggregated[key] = {
                    "date": key,
                    "description": f"Entities added in {key}",
                    "event_type": "aggregation",
                    "details": []
                }
            if len(aggregated[key]["details"]) < 50: # Limit details
                aggregated[key]["details"].append(t["description"])
                
        final_timeline = sorted(list(aggregated.values()), key=lambda x: x["date"])
        
        output_data = {
            "schema_version": self.version,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "events": final_timeline
        }
        
        success = atomic_write_json_artifact(
            self.output_file,
            output_data,
            schema_path=self.schema_path,
            is_dry_run=self.is_dry_run
        )
        
        result.validation_status = success
        if success:
            result.artifacts_written.append(self.output_file)
        else:
            result.warnings.append("Failed to write timeline.json or validation failed.")
            
        # Write markdown report
        md_content = "# Historical Timeline\n\n"
        for t in final_timeline:
            md_content += f"- **{t['date']}**: {t['description']} ({len(t['details'])} details)\n"
            
        if not self.is_dry_run:
            save_markdown_deterministic(self.report_file, md_content)
            result.artifacts_written.append(self.report_file)
            
        result.entities_processed = len(timeline)
        result.execution_time_ms = int((time.time() - start_time) * 1000)
        
        return result

if __name__ == "__main__":
    generator = TimelineGenerator()
    generator.generate()
