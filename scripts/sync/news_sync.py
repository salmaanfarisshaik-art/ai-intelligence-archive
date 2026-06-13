import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from scripts.lib.base_sync import BaseSync
from scripts.lib.normalizer import Normalizer
from scripts.lib.deduplicator import deduplicator
from scripts.sources.rss_fetcher import fetch_rss_feeds
from scripts.lib.config_loader import config

class NewsSync(BaseSync):
    def __init__(self):
        self.schema_version = "1.0"
        super().__init__(
            schema_name="news",
            output_dir=os.path.join("data", "processed", "news")
        )

    def fetch(self) -> List[Dict[Any, Any]]:
        records = []
        now = datetime.now(timezone.utc).isoformat()

        # Fetch RSS Feeds
        data = fetch_rss_feeds()
        
        for item in data:
            link = item.get("link", "")
            if not link:
                continue

            # Deterministic unique ID
            unique_id_str = f"news_{link}"
            import hashlib
            uid_hash = hashlib.md5(unique_id_str.encode('utf-8')).hexdigest()

            normalized = {
                "unique_id": f"news_{uid_hash}",
                "schema_version": self.schema_version,
                "title": item.get("title", "Unknown"),
                "summary": item.get("description", "No summary"),
                "author": item.get("author", "Unknown"),
                "source_url": link,
                "source_name": item.get("source_feed_name", "RSS"),
                "source_type": "rss",
                "category": "news",
                "raw_payload": item,
                "retrieval_timestamp": now,
                "last_updated": item.get("published", now)
            }
            records.append(normalized)

        # Deduplicate deterministically
        records, removed = deduplicator.remove_duplicates(records)

        return records

    def transform(self, data: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        from scripts.lib.link_builder import link_builder
        from scripts.lib.ai_enrichment import ai_enricher
        
        data = link_builder.build_links(self.schema_name, data)
        data = ai_enricher.enrich(self.schema_name, data)
        return data
