from typing import Dict, Any, List

class ChangeClassifier:
    def __init__(self):
        self.ignore_prefixes = [
            ".tmp", "__pycache__", "logs/", ".pytest_cache", "venv/",
            "reports/latest_run.md", "reports/run_manifest.json",
            "reports/change_summary.json", "reports/change_summary.md",
            "reports/project_status.json", "releases/", "snapshots/"
        ]
        
    def classify(self, changes: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Classifies meaningful changes vs noise.
        """
        all_changes = changes.get("files_added", []) + changes.get("files_modified", []) + changes.get("files_removed", [])
        
        volatile_files = {
            "reports/latest_run.md", "reports/run_manifest.json",
            "reports/change_summary.json", "reports/change_summary.md",
            "reports/project_status.json", "reports/dashboard.md",
            "reports/integrity_report.md", "reports/integrity_status.json",
            "reports/repository_metrics.md",
            "data/metadata/api_manifest.json", "data/metadata/connector_manifest.json",
            "data/metadata/feature_manifest.json", "data/metadata/repo_metrics.json",
            "data/metadata/repository_manifest.json", "data/metadata/schema_manifest.json",
            "graph/edges.json", "graph/graph_api.json", "graph/nodes.json",
            "site/index.json", "site/search_index.json"
        }
        
        meaningful_changes = []
        categories = set()
        
        for f in all_changes:
            # Normalize slashes
            norm_f = f.replace("\\", "/")
            if any(norm_f.startswith(p) or p in norm_f for p in self.ignore_prefixes):
                continue
                
            if norm_f in volatile_files:
                continue
            
            meaningful_changes.append(norm_f)
            
            if norm_f.startswith("data/"):
                categories.add("data_update")
            elif norm_f.startswith("docs/") or norm_f.endswith(".md"):
                categories.add("documentation_update")
            elif norm_f.startswith("site/"):
                categories.add("site_update")
            elif norm_f.startswith("reports/") or norm_f.endswith(".json"):
                categories.add("metadata_update")
            else:
                categories.add("system_update")
                
        # Determine overall commit message strategy
        commit_message = "chore(sync): automated repository maintenance [skip ci]"
        
        if "data_update" in categories:
            commit_message = "chore(sync): update AI ecosystem snapshot [skip ci]"
        elif "documentation_update" in categories and len(categories) == 1:
            commit_message = "docs: refresh generated documentation [skip ci]"
        elif "site_update" in categories and len(categories) == 1:
            commit_message = "build(site): regenerate static portal assets [skip ci]"
        elif len(categories) > 1:
            commit_message = "chore(sync): update repository intelligence artifacts [skip ci]"
            
        return {
            "meaningful_changes": meaningful_changes,
            "has_meaningful_changes": len(meaningful_changes) > 0,
            "categories": list(categories),
            "suggested_commit_message": commit_message
        }
