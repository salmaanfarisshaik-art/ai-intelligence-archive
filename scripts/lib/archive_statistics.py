import os
import json
import csv
import re
from datetime import datetime, timezone
from scripts.lib.logger import setup_logger
from scripts.lib.serialization import save_json_deterministic
from scripts.lib.archive_stats_generator import ArchiveStatsGenerator

logger = setup_logger("archive_statistics")

class ArchiveStatistics:
    """
    New Phase 8.5 Interface for Statistics Generation.
    Wraps/deprecates ArchiveStatsGenerator and ensures README boundaries.
    """
    def __init__(self):
        self.legacy_generator = ArchiveStatsGenerator()
        
    def generate(self):
        logger.info("Generating Archive Statistics (Phase 8.5)...")
        # Reuse core logic from legacy generator to count deterministically
        stats = self.legacy_generator.generate()
        
        # Ensure site and exports are updated (new requirements)
        self._export_csv(stats)
        self._sync_site(stats)
        self._update_readme(stats)
        
    def _export_csv(self, stats: dict):
        os.makedirs("exports", exist_ok=True)
        with open("exports/archive_stats.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Count"])
            for k, v in stats.items():
                if k != "generated_at":
                    writer.writerow([k, v])
                    
    def _sync_site(self, stats: dict):
        os.makedirs("site", exist_ok=True)
        save_json_deterministic("site/archive_stats.json", stats)
        
    def _update_readme(self, stats: dict):
        readme_path = "README.md"
        if not os.path.exists(readme_path):
            return
            
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        start_marker = "<!-- ARCHIVE_STATS_START -->"
        end_marker = "<!-- ARCHIVE_STATS_END -->"
        
        if start_marker in content and end_marker in content:
            friendly_names = {
                "models": "🤖 Models",
                "datasets": "📚 Datasets",
                "tools": "🧰 AI Tools",
                "benchmarks": "📊 Benchmarks",
                "prompts": "💬 Prompt Templates",
                "skills": "📝 AI Skills & Workflows",
                "mcp_servers": "🏗️ MCP Servers",
                "ide_rules": "🖥️ IDE Rules",
                "api_providers": "🔌 APIs & AI Services",
                "news_articles": "📰 News Articles",
                "knowledge_graph_relationships": "🧠 Knowledge Graph Relationships"
            }
            
            stats_text = "\n(auto-generated)\n\n📊 **AI Intelligence Archive Statistics**\n\n"
            for k, v in friendly_names.items():
                count = stats.get(k, 0)
                stats_text += f"{v}: {count:,}\n"
            stats_text += "\n"
            
            # Regex replacement
            pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
            new_content = pattern.sub(f"{start_marker}{stats_text}{end_marker}", content)
            
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            logger.info("README.md statistics auto-updated.")
        else:
            logger.warning("README.md is missing ARCHIVE_STATS markers.")
