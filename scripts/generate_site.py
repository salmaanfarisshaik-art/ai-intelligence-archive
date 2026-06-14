import os
import shutil
from scripts.lib.logger import setup_logger
from scripts.lib.serialization import save_json_deterministic
from scripts.site.site_generator import SiteGenerator

logger = setup_logger("generate_site")

def generate_site():
    """
    Site generation orchestrator.
    Generates all static portal assets exclusively from generated indexes and metadata.
    Uses atomic .tmp writes before replacement.
    Produces deterministic byte-for-byte outputs.
    Fully compatible with GitHub Pages deployment.
    """
    logger.info("Starting site generation orchestrator")
    
    os.makedirs("site", exist_ok=True)
    
    # 1. Copy over deterministic metadata from Phase 6
    metadata_sources = [
        ("data/metadata/recommendations.json", "site/recommendations.json"),
        ("data/metadata/leaderboards.json", "site/leaderboards.json"),
        ("data/metadata/trends.json", "site/trending.json"),
        ("data/metadata/timeline.json", "site/timeline.json"),
    ]
    
    import json
    for src, dst in metadata_sources:
        if os.path.exists(src):
            # Read and save atomically
            with open(src, "r", encoding="utf-8") as f:
                data = json.load(f)
            save_json_deterministic(dst, data)
    
    # 2. Invoke legacy SiteGenerator
    try:
        SiteGenerator().run()
    except Exception as e:
        logger.error(f"Legacy SiteGenerator failed: {e}")

if __name__ == "__main__":
    generate_site()
