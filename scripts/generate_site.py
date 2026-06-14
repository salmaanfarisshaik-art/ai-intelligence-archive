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
        ("reports/archive_stats.json", "site/archive_stats.json"),
    ]
    
    import json
    for src, dst in metadata_sources:
        if os.path.exists(src):
            # Read and save atomically
            with open(src, "r", encoding="utf-8") as f:
                data = json.load(f)
            save_json_deterministic(dst, data)
            
    # 2. Support new Next.js Frontend Development
    frontend_data_dir = "frontend/public/data"
    if os.path.exists("frontend"):
        os.makedirs(frontend_data_dir, exist_ok=True)
        
        # Copy stats
        if os.path.exists("reports/archive_stats.json"):
            shutil.copy("reports/archive_stats.json", os.path.join(frontend_data_dir, "archive_stats.json"))
            
        import glob
        
        # Build global search index and subset data for categories
        search_index = []
        
        for filepath in glob.glob("data/processed/*/data.json"):
            category = os.path.basename(os.path.dirname(filepath))
            
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    records = json.load(f)
                except Exception:
                    continue
            
            # Slice top 150 items for fast frontend rendering
            subset = records[:150]
            cat_dir = os.path.join(frontend_data_dir, category)
            os.makedirs(cat_dir, exist_ok=True)
            save_json_deterministic(os.path.join(cat_dir, "data.json"), subset)
            
            # Add all items to lightweight search index
            for rec in records:
                # Try to extract the most meaningful title/name
                title = rec.get("name") or rec.get("title") or rec.get("skill_name") or rec.get("technique_name") or rec.get("server_name") or rec.get("provider") or rec.get("rule_name") or "Unknown"
                description = rec.get("description") or rec.get("summary") or rec.get("workflow") or ""
                
                search_index.append({
                    "id": rec.get("unique_id", ""),
                    "category": category,
                    "title": str(title)[:100],
                    "desc": str(description)[:150] # Snippet for search preview
                })
        
        # Save global search index
        save_json_deterministic(os.path.join(frontend_data_dir, "search_index.json"), search_index)
        logger.info(f"Generated search index with {len(search_index)} items")
    
    # 3. Invoke legacy SiteGenerator (can be deprecated later)
    try:
        SiteGenerator().run()
    except Exception as e:
        logger.error(f"Legacy SiteGenerator failed: {e}")

if __name__ == "__main__":
    generate_site()
