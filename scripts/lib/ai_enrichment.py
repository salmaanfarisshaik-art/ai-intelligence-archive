import os
import json
import requests
from typing import List, Dict, Any
from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("ai_enrichment")

class AIEnricher:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}" if self.api_key else ""

    def enrich(self, schema_name: str, records: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        if not config.is_feature_enabled("enable_ai_enrichment"):
            return records
            
        if not self.api_key:
            logger.warning("enable_ai_enrichment is true but GEMINI_API_KEY is not set. Skipping enrichment.")
            return records

        logger.info(f"Running AI enrichment for {schema_name}")
        for record in records:
            # Skip if already enriched to save quota
            if "ai_summary" in record:
                continue
                
            try:
                payload_str = str(record.get("raw_payload", ""))[:3000] # Truncate to avoid token limits
                if not payload_str:
                    continue
                    
                prompt = (
                    f"Analyze the following {schema_name} data and provide a concise summary, 3 tags, and a difficulty label (Beginner, Intermediate, Advanced). "
                    f"Output strict JSON format with exactly these keys: ai_summary, ai_tags (list of strings), ai_difficulty. "
                    f"Data: {payload_str}"
                )
                
                response = requests.post(
                    self.endpoint,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"response_mime_type": "application/json"}
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    resp_data = response.json()
                    text = resp_data["candidates"][0]["content"]["parts"][0]["text"]
                    enrichment_data = json.loads(text)
                    
                    # Store as optional fields (AI output is supplementary metadata only)
                    record["ai_summary"] = enrichment_data.get("ai_summary", "")
                    record["ai_tags"] = enrichment_data.get("ai_tags", [])
                    record["ai_difficulty"] = enrichment_data.get("ai_difficulty", "")
                    record["ai_generated"] = True
                else:
                    logger.warning(f"Enrichment failed with status {response.status_code}: {response.text}")
                    # Phase 3 Contract: Pipeline MUST continue gracefully without crashing
                    continue

            except Exception as e:
                logger.warning(f"Enrichment exception for record {record.get('unique_id')}: {e}")
                # Phase 3 Contract: Pipeline MUST continue gracefully without crashing
                continue

        return records

ai_enricher = AIEnricher()
