import os
import json
from scripts.lib.base_generator import BaseGenerator
from scripts.site.page_builder import PageBuilder
from scripts.site.navigation_builder import NavigationBuilder

class SiteGenerator(BaseGenerator):
    def __init__(self):
        super().__init__("site_generator", phase=6)
        
    def generate(self) -> dict:
        """
        Generates the static site.
        """
        os.makedirs("site/models", exist_ok=True)
        os.makedirs("site/papers", exist_ok=True)
        os.makedirs("site/datasets", exist_ok=True)
        os.makedirs("site/prompts", exist_ok=True)
        os.makedirs("site/tools", exist_ok=True)
        os.makedirs("site/assets", exist_ok=True)
        
        nav_builder = NavigationBuilder()
        page_builder = PageBuilder(nav_builder.get_nav_html())
        
        # Build index
        index_html = page_builder.build_index()
        self.save_markdown("site/index.html", index_html) # Using save_markdown as it writes text atomically
        
        # We could build pages for models, etc., but keeping it simple for the skeleton
        
        nav_json = nav_builder.get_nav_data()
        self.save_json("site/navigation.json", nav_json)
        
        return {"records_processed": 1}
