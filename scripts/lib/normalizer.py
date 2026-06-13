import json
from typing import Dict, Any, List
from scripts.lib.logger import setup_logger, ErrorCategory

logger = setup_logger("normalizer")

class Normalizer:
    @staticmethod
    def normalize(source_type: str, raw_records: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        normalized = []
        for record in raw_records:
            try:
                norm = Normalizer._normalize_single(source_type, record)
                if norm:
                    normalized.append(norm)
            except Exception as e:
                logger.error(f"Normalization failed for record from {source_type}", extra={"error_category": ErrorCategory.VALIDATION_ERROR.value})
        return normalized

    @staticmethod
    def _normalize_single(source_type: str, record: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Outputs:
        {
            "unique_id": "",
            "source_url": "",
            "source_name": "",
            "source_type": "arxiv | huggingface | rss",
            "last_updated": "",
            "category": "",
            "raw_payload": {}
        }
        """
        if source_type == "arxiv":
            return {
                "unique_id": f"arxiv_{record.get('id', '').split('/')[-1]}",
                "source_url": record.get('id', ''),
                "source_name": "ArXiv",
                "source_type": "arxiv",
                "last_updated": record.get('updated', ''),
                "category": record.get('primary_category', 'cs.AI'),
                "raw_payload": record
            }
        elif source_type == "huggingface":
            return {
                "unique_id": f"hf_{record.get('id', '').replace('/', '_')}",
                "source_url": f"https://huggingface.co/{record.get('id')}",
                "source_name": "Hugging Face",
                "source_type": "huggingface",
                "last_updated": record.get('lastModified', ''),
                "category": record.get('pipeline_tag', 'unknown'),
                "raw_payload": record
            }
        elif source_type == "rss":
            return {
                "unique_id": f"rss_{record.get('id', record.get('link', ''))}",
                "source_url": record.get('link', ''),
                "source_name": record.get('source_feed_name', 'RSS'),
                "source_type": "rss",
                "last_updated": record.get('published', ''),
                "category": "news",
                "raw_payload": record
            }
        else:
            raise ValueError(f"Unknown source type: {source_type}")
