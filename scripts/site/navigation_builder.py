from typing import Dict, Any

class NavigationBuilder:
    def __init__(self):
        self.nav_items = [
            {"label": "Home", "url": "/"},
            {"label": "Models", "url": "/models/"},
            {"label": "Papers", "url": "/papers/"},
            {"label": "Datasets", "url": "/datasets/"},
            {"label": "Prompts", "url": "/prompts/"},
            {"label": "Tools", "url": "/tools/"},
            {"label": "Archive Statistics", "url": "/stats/"}
        ]
        
    def get_nav_data(self) -> Dict[str, Any]:
        return {"items": self.nav_items}
        
    def get_nav_html(self) -> str:
        links = []
        for item in self.nav_items:
            links.append(f'<a href="{item["url"]}">{item["label"]}</a>')
        return " | ".join(links)
