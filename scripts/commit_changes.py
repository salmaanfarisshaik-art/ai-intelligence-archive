import os
import subprocess
from scripts.lib.logger import setup_logger

logger = setup_logger("commit_changes")

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def main():
    logger.info("Checking for meaningful data changes...")
    
    # Example logic to see if data/processed actually changed
    # In a real setup, we might use `git status --porcelain data/`
    status = run_cmd(["git", "status", "--porcelain", "data/"])
    if not status:
        logger.info("No meaningful data changes detected. Skipping commit.")
        return

    # Add data/ and commit
    run_cmd(["git", "add", "data/"])
    
    commit_msg = "update(phase1): refresh automated data"
    run_cmd(["git", "commit", "-m", commit_msg])
    logger.info(f"Committed changes with message: {commit_msg}")

if __name__ == "__main__":
    main()
