import subprocess
import os
from scripts.lib.logger import setup_logger

class CommitManager:
    def __init__(self, is_dry_run: bool = False):
        self.logger = setup_logger("commit_manager")
        self.is_dry_run = is_dry_run
        
    def _run_cmd(self, cmd: list) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, capture_output=True, text=True)

    def _setup_git_identity(self):
        """Sets git identity if not configured."""
        name_check = self._run_cmd(["git", "config", "user.name"])
        email_check = self._run_cmd(["git", "config", "user.email"])
        
        if name_check.returncode != 0 or not name_check.stdout.strip():
            self._run_cmd(["git", "config", "user.name", "github-actions[bot]"])
            self.logger.info("Configured default git user.name")
            
        if email_check.returncode != 0 or not email_check.stdout.strip():
            self._run_cmd(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
            self.logger.info("Configured default git user.email")
            
    def commit(self, files_to_commit: list, commit_message: str) -> bool:
        """
        Stages and commits the specified files.
        """
        if self.is_dry_run:
            self.logger.info(f"DRY RUN: Would have committed {len(files_to_commit)} files with message: '{commit_message}'")
            return True
            
        self._setup_git_identity()
        
        # Stage files safely
        for f in files_to_commit:
            res = self._run_cmd(["git", "add", f])
            if res.returncode != 0:
                self.logger.warning(f"Failed to stage file: {f}")
                
        # Commit
        res = self._run_cmd(["git", "commit", "-m", commit_message])
        if res.returncode != 0:
            # It's possible nothing was staged if all were noise or filtered out
            self.logger.warning(f"Git commit returned non-zero. Possibly nothing to commit: {res.stdout} {res.stderr}")
            return False
            
        self.logger.info(f"Successfully committed changes: '{commit_message}'")
        return True
