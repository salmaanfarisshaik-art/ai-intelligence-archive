class SourceMetrics:
    def __init__(self):
        self.api_calls_made = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.duplicates_removed = 0
        self.external_sources_failed = []

    def record_api_call(self):
        self.api_calls_made += 1

    def record_cache_hit(self):
        self.cache_hits += 1

    def record_cache_miss(self):
        self.cache_misses += 1
        
    def record_duplicate_removed(self, count=1):
        self.duplicates_removed += count
        
    def record_source_failure(self, source_name: str):
        if source_name not in self.external_sources_failed:
            self.external_sources_failed.append(source_name)

    def to_dict(self):
        return {
            "api_calls_made": self.api_calls_made,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "duplicates_removed": self.duplicates_removed,
            "external_sources_failed": self.external_sources_failed
        }

# Global metrics instance for the pipeline run
metrics = SourceMetrics()
