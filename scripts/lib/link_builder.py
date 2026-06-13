import re
from typing import List, Dict, Any
from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("link_builder")

class LinkBuilder:
    def __init__(self):
        # Deterministic regex for extracting relationships
        self.arxiv_pattern = re.compile(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}(?:v\d+)?)')
        self.hf_pattern = re.compile(r'huggingface\.co/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)')

    def build_links(self, schema_name: str, records: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        if not config.is_feature_enabled("enable_cross_linking"):
            return records

        logger.info(f"Generating cross-links for {schema_name}")
        for record in records:
            if "links" not in record:
                record["links"] = {
                    "related_models": [],
                    "related_papers": [],
                    "related_datasets": [],
                    "related_tools": []
                }
            
            # Use raw payload stringification to deterministically find links
            payload_str = str(record.get("raw_payload", {}))
            
            # Deterministic ArXiv extraction
            arxiv_matches = sorted(list(set(self.arxiv_pattern.findall(payload_str))))
            for arxiv_id in arxiv_matches:
                if arxiv_id not in record["links"]["related_papers"]:
                    record["links"]["related_papers"].append(arxiv_id)

            # Deterministic HF model extraction
            hf_matches = sorted(list(set(self.hf_pattern.findall(payload_str))))
            for hf_id in hf_matches:
                if hf_id not in record["links"]["related_models"]:
                    record["links"]["related_models"].append(hf_id)

        return records

link_builder = LinkBuilder()
