import os
import re
from scripts.lib.logger import setup_logger

logger = setup_logger("documentation_guard")

class DocumentationGuard:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def update_section(self, start_marker: str, end_marker: str, new_content: str, is_dry_run: bool = False):
        """
        Updates content only between the start_marker and end_marker in the file.
        Emits a warning if markers are not found and does not overwrite anything.
        """
        if not os.path.exists(self.filepath):
            logger.warning(f"File {self.filepath} not found. Cannot update section.")
            return

        with open(self.filepath, "r", encoding="utf-8") as f:
            content = f.read()

        pattern = re.compile(rf"({re.escape(start_marker)}).*?({re.escape(end_marker)})", re.DOTALL)
        
        if not pattern.search(content):
            logger.warning(f"Markers {start_marker} and {end_marker} not found in {self.filepath}. Skipping update.")
            return

        new_text = f"\\1\n{new_content.strip()}\n\\2"
        updated_content = pattern.sub(new_text, content)

        if updated_content == content:
            logger.info(f"No changes needed for section {start_marker} in {self.filepath}.")
            return

        if is_dry_run:
            logger.info(f"DRY RUN: Would have updated section {start_marker} in {self.filepath}.")
            return

        from scripts.lib.file_utils import atomic_write
        atomic_write(self.filepath, updated_content)
        logger.info(f"Successfully updated section {start_marker} in {self.filepath}.")
