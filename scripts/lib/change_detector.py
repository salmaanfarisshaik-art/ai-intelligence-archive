import subprocess
import os
from typing import Dict, Any, List
from scripts.lib.base_generator import BaseGenerator

class ChangeDetector(BaseGenerator):
    def __init__(self):
        super().__init__("change_detector", phase=8)
        
    def generate(self) -> Dict[str, Any]:
        """
        Detects file changes using git status --porcelain.
        Returns the raw changed files lists.
        """
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode != 0:
            self.logger.error(f"Failed to execute git status: {result.stderr}")
            return {"errors": 1}
            
        added = []
        modified = []
        removed = []
        
        for line in result.stdout.splitlines():
            if len(line) < 4:
                continue
            status = line[:2]
            file_path = line[3:].strip()
            
            # Handle renames (e.g., 'R  old -> new')
            if "->" in file_path:
                file_path = file_path.split("->")[1].strip()
            
            if status in ("A ", "??", " A", "AM"):
                added.append(file_path)
            elif status in (" M", "M ", "MM"):
                modified.append(file_path)
            elif status in (" D", "D "):
                removed.append(file_path)
            elif status.startswith("R"):
                added.append(file_path) # Treat rename as add for the new file
                
        summary = {
            "files_added": added,
            "files_modified": modified,
            "files_removed": removed,
            "total_changes": len(added) + len(modified) + len(removed)
        }
        
        os.makedirs("reports", exist_ok=True)
        self.save_json("reports/change_summary.json", summary)
        
        md_content = "# Change Summary\n\n"
        md_content += f"**Total Changes:** {summary['total_changes']}\n\n"
        md_content += "## Added\n" + ("\n".join([f"- {f}" for f in added]) if added else "None") + "\n\n"
        md_content += "## Modified\n" + ("\n".join([f"- {f}" for f in modified]) if modified else "None") + "\n\n"
        md_content += "## Removed\n" + ("\n".join([f"- {f}" for f in removed]) if removed else "None") + "\n"
        
        self.save_markdown("reports/change_summary.md", md_content)
        
        return summary

    def run(self) -> Dict[str, Any]:
        return self.generate()
