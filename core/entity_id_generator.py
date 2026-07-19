import hashlib
import re

class EntityIDGenerator:
    """
    Generates stable canonical IDs for entities.
    IDs generated only from canonical attributes and use stable hashing.
    """
    
    @staticmethod
    def _normalize_string(s: str) -> str:
        if not s:
            return ""
        s = s.lower().strip()
        # Replace non-alphanumeric with underscore
        s = re.sub(r'[^a-z0-9]+', '_', s)
        # Remove consecutive underscores
        s = re.sub(r'_+', '_', s)
        return s.strip('_')

    @classmethod
    def generate_id(cls, prefix: str, *canonical_parts) -> str:
        """
        Generate a stable ID.
        Example: generate_id("model", "openai", "gpt4") -> "model_openai_gpt4"
        """
        normalized_parts = [cls._normalize_string(str(p)) for p in canonical_parts if p]
        
        # We try to make human readable IDs first.
        # But to guarantee uniqueness if parts are too long or overlap, we append a stable hash if needed,
        # or we just rely on the parts being canonical.
        
        # A good stable ID is prefix_part1_part2
        base_id = f"{prefix}_" + "_".join(normalized_parts)
        
        # If it's too long, truncate and append hash of the full parts
        if len(base_id) > 100:
            full_str = "_".join(normalized_parts)
            stable_hash = hashlib.sha256(full_str.encode('utf-8')).hexdigest()[:10]
            base_id = f"{prefix}_{normalized_parts[0][:40]}_{stable_hash}"
            
        return base_id
        
    @classmethod
    def generate_hash_id(cls, prefix: str, content: str) -> str:
        """
        Fallback for when canonical parts aren't clear, use a hash of the content.
        """
        stable_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:12]
        return f"{prefix}_{stable_hash}"
