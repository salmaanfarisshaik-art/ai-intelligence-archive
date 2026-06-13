import os
import json
import re
from typing import Dict, Any, List

from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("generate_docs")

class DocsGenerator:
    def __init__(self):
        self.metadata_dir = os.path.join("data", "metadata")
        self.docs_dir = "docs"
        os.makedirs(self.docs_dir, exist_ok=True)
        self.entity_index_path = os.path.join(self.metadata_dir, "entity_index.json")
        self.start_marker = "<!-- GENERATED_CONTENT_START -->"
        self.end_marker = "<!-- GENERATED_CONTENT_END -->"

    def _atomic_write(self, filepath: str, content: str):
        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        if is_dry_run:
            logger.info(f"DRY RUN: Would have saved docs to {filepath}")
            return
            
        tmp_filepath = f"{filepath}.tmp"
        try:
            with open(tmp_filepath, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_filepath, filepath)
            logger.info(f"Successfully saved {filepath}")
        except Exception as e:
            logger.error(f"Failed atomic write to {filepath}: {e}")
            if os.path.exists(tmp_filepath):
                os.remove(tmp_filepath)

    def _inject_content(self, filepath: str, generated_content: str, title: str) -> str:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                existing = f.read()
            
            pattern = re.compile(f"{self.start_marker}.*?{self.end_marker}", re.DOTALL)
            if pattern.search(existing):
                return pattern.sub(f"{self.start_marker}\n{generated_content}\n{self.end_marker}", existing)
            else:
                # Append to end if markers don't exist but file does
                return existing + f"\n\n{self.start_marker}\n{generated_content}\n{self.end_marker}\n"
        else:
            # Create fresh with markers
            return f"# {title}\n\n{self.start_marker}\n{generated_content}\n{self.end_marker}\n"

    def generate(self):
        if not config.is_feature_enabled("enable_doc_generation"):
            logger.info("Doc generation is disabled in config.")
            return

        logger.info("Generating documentation...")
        
        if not os.path.exists(self.entity_index_path):
            logger.warning(f"Cannot generate docs. {self.entity_index_path} is missing.")
            return
            
        try:
            with open(self.entity_index_path, "r", encoding="utf-8") as f:
                entities = json.load(f)
                
            categories = {}
            for entity in entities:
                cat = entity.get("category", "unknown")
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(entity)
                
            for cat, items in categories.items():
                items = sorted(items, key=lambda x: x["title"].lower())
                
                md_lines = []
                md_lines.append(f"## {cat.title().replace('_', ' ')} Directory")
                md_lines.append("")
                md_lines.append("| Name | Source | Tags | Links |")
                md_lines.append("|---|---|---|---|")
                
                for item in items:
                    name = item.get("title", "")
                    url = item.get("source_url", "")
                    name_link = f"[{name}]({url})" if url else name
                    source = item.get("source", "")
                    tags = ", ".join(item.get("tags", [])[:5])
                    
                    # count links
                    links_count = sum(len(v) for v in item.get("links", {}).values() if isinstance(v, list))
                    
                    md_lines.append(f"| {name_link} | {source} | {tags} | {links_count} |")
                    
                generated_section = "\n".join(md_lines)
                filepath = os.path.join(self.docs_dir, f"{cat}.md")
                
                final_content = self._inject_content(filepath, generated_section, cat.title().replace('_', ' '))
                self._atomic_write(filepath, final_content)
                
            logger.info("Documentation generated successfully.")
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")

if __name__ == "__main__":
    DocsGenerator().generate()
