import hashlib
import re
from typing import List, Dict, Any, Tuple
from scripts.lib.logger import setup_logger
from scripts.lib.source_metrics import metrics

logger = setup_logger("deduplicator")

class Deduplicator:
    def __init__(self):
        # Global hash index across runs in-memory
        self.seen_hashes = set()
        self.seen_titles = set()
        
        # Phase 3 Deduplication v2 additions
        self.seen_urls = set()
        self.seen_arxiv_ids = set()
        self.seen_hf_ids = set()

    def _get_record_hash(self, record: Dict[Any, Any]) -> str:
        # Use unique_id as primary hash base if available
        unique_id = record.get("unique_id", "")
        if unique_id:
            return hashlib.md5(unique_id.encode('utf-8')).hexdigest()
        
        # Fallback to source url
        source_url = record.get("source_url", "")
        return hashlib.md5(source_url.encode('utf-8')).hexdigest()

    def _normalize_title(self, title: str) -> str:
        if not title:
            return ""
        # Lowercase, remove non-alphanumeric, collapse spaces
        clean = re.sub(r'[^a-z0-9]', '', title.lower())
        return clean

    def _get_title_from_payload(self, record: Dict[Any, Any]) -> str:
        payload = record.get("raw_payload", {})
        # Try common title fields
        return payload.get("title", payload.get("name", ""))

    def _normalize_url(self, url: str) -> str:
        if not url:
            return ""
        # Remove tracking params and trailing slashes
        clean = re.sub(r'\?.*$', '', url)
        clean = clean.rstrip('/')
        return clean.lower()

    def _extract_arxiv_id(self, text: str) -> str:
        match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}(?:v\d+)?)', text)
        return match.group(1) if match else ""

    def _extract_hf_id(self, text: str) -> str:
        match = re.search(r'huggingface\.co/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)', text)
        return match.group(1) if match else ""

    def remove_duplicates(self, records: List[Dict[Any, Any]]) -> Tuple[List[Dict[Any, Any]], int]:
        filtered_records = []
        duplicates_removed = 0

        for record in records:
            rec_hash = self._get_record_hash(record)
            title = self._get_title_from_payload(record)
            norm_title = self._normalize_title(title)
            
            source_url = record.get("source_url", "")
            norm_url = self._normalize_url(source_url)
            
            # Use raw payload to extract explicit unique identifiers safely
            payload_str = str(record.get("raw_payload", {}))
            arxiv_id = self._extract_arxiv_id(source_url) or self._extract_arxiv_id(payload_str)
            hf_id = self._extract_hf_id(source_url) or self._extract_hf_id(payload_str)
            
            is_dup = False
            
            # Phase 1 & 2 exact hash matching
            if rec_hash in self.seen_hashes:
                is_dup = True
            # Phase 2 Semantic duplicate matching
            elif norm_title and norm_title in self.seen_titles:
                is_dup = True
            # Phase 3 Deduplication v2 extensions
            elif norm_url and norm_url in self.seen_urls:
                is_dup = True
            elif arxiv_id and arxiv_id in self.seen_arxiv_ids:
                is_dup = True
            elif hf_id and hf_id in self.seen_hf_ids:
                is_dup = True
                
            # If duplicate confidence is uncertain (none of the strict rules match), default to preserving records to prevent data loss.
                
            if is_dup:
                duplicates_removed += 1
                logger.debug(f"Duplicate removed: {record.get('unique_id', 'Unknown')}")
            else:
                self.seen_hashes.add(rec_hash)
                if norm_title:
                    self.seen_titles.add(norm_title)
                if norm_url:
                    self.seen_urls.add(norm_url)
                if arxiv_id:
                    self.seen_arxiv_ids.add(arxiv_id)
                if hf_id:
                    self.seen_hf_ids.add(hf_id)
                    
                filtered_records.append(record)

        if duplicates_removed > 0:
            metrics.record_duplicate_removed(duplicates_removed)
            logger.info(f"Removed {duplicates_removed} duplicates from batch.")
            
        return filtered_records, duplicates_removed

# Global deduplicator instance
deduplicator = Deduplicator()
