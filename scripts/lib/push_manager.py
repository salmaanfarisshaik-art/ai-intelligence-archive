import subprocess
from scripts.lib.logger import setup_logger

class PushManager:
    def __init__(self, is_dry_run: bool = False):
        self.logger = setup_logger("push_manager")
        self.is_dry_run = is_dry_run
        
    def _run_cmd(self, cmd: list) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, capture_output=True, text=True)

    def push(self) -> bool:
        """
        Pushes commits to the remote. Never force pushes.
        """
        if self.is_dry_run:
            self.logger.info("DRY RUN: Would have executed 'git push origin HEAD'")
            return True
            
        res = self._run_cmd(["git", "push", "origin", "HEAD"])
        if res.returncode != 0:
            self.logger.error(f"Failed to push: {res.stderr}")
            return False
            
        self.logger.info("Successfully pushed changes to remote.")
        return True
