import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from core.base_sync import BaseSync
from core.normalizer import Normalizer
from core.deduplicator import deduplicator
from scripts.sources.github_trending import GitHubTrendingFetcher
from core.config_loader import config

class ToolSync(BaseSync):
    def __init__(self):
        self.schema_version = "1.0"
        super().__init__(
            schema_name="tool",
            output_dir="tools"
        )
        self.fetcher = GitHubTrendingFetcher(
            endpoint=config.sources.get("github_trending", {}).get("endpoint", "https://api.github.com/search/repositories")
        )

    def fetch(self) -> List[Dict[Any, Any]]:
        records = []
        now = datetime.now(timezone.utc).isoformat()

        # Fetch from GitHub
        gh_data = self.fetcher.fetch()
        
        for item in gh_data:
            repo_id = str(item.get("id", ""))
            if not repo_id:
                continue

            normalized = {
                "unique_id": f"gh_{repo_id}",
                "schema_version": self.schema_version,
                "name": item.get("name", "Unknown"),
                "description": item.get("description", "No description"),
                "language": item.get("language", "Unknown"),
                "stars": item.get("stargazers_count", 0),
                "source_url": item.get("html_url", ""),
                "source_name": "GitHub Trending",
                "source_type": "api",
                "category": "tool",
                "raw_payload": item,
                "retrieval_timestamp": now,
                "last_updated": item.get("updated_at", now)
            }
            records.append(normalized)

        # Deduplicate deterministically
        records, removed = deduplicator.remove_duplicates(records)

        return records

    def transform(self, data: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
        from core.link_builder import link_builder
        from core.ai_enrichment import ai_enricher
        
        data = link_builder.build_links(self.schema_name, data)
        data = ai_enricher.enrich(self.schema_name, data)
        return data

