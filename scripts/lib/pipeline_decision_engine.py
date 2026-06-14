import os
from typing import Dict, Any
from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config
from scripts.lib.change_detector import ChangeDetector
from scripts.lib.change_classifier import ChangeClassifier
from scripts.lib.commit_manager import CommitManager
from scripts.lib.push_manager import PushManager

class PipelineDecisionEngine:
    def __init__(self, is_dry_run: bool = False):
        self.logger = setup_logger("pipeline_decision_engine")
        self.is_dry_run = is_dry_run
        
    def run(self, pipeline_failed: bool) -> Dict[str, Any]:
        """
        Orchestrates Phase 8 logic.
        """
        status_report = {
            "commit_created": False,
            "push_completed": False,
            "site_regenerated": False,
            "phase8_status": "skipped",
            "files_added": 0,
            "files_modified": 0,
            "files_removed": 0
        }
        
        if pipeline_failed:
            self.logger.warning("Pipeline failed upstream. Skipping autonomous updates.")
            status_report["phase8_status"] = "skipped_due_to_upstream_failure"
            return status_report

        # 1. Detect Changes
        change_detector = ChangeDetector()
        change_detector.is_dry_run = self.is_dry_run
        raw_changes = change_detector.run()
        
        status_report["files_added"] = len(raw_changes.get("files_added", []))
        status_report["files_modified"] = len(raw_changes.get("files_modified", []))
        status_report["files_removed"] = len(raw_changes.get("files_removed", []))
        
        # 2. Classify Changes
        classifier = ChangeClassifier()
        classification = classifier.classify(raw_changes)
        
        if not classification["has_meaningful_changes"]:
            self.logger.info("No meaningful changes detected. Skipping site generation, commit, and push.")
            status_report["phase8_status"] = "success_no_changes"
            return status_report
            
        # 3. Generate Site (Imported lazily to avoid circular dependencies if any)
        from scripts.generate_site import generate_site
        
        if config.is_feature_enabled("enable_auto_site_publish"):
            try:
                self.logger.info("Meaningful changes detected. Regenerating static site assets...")
                generate_site()
                status_report["site_regenerated"] = True
            except Exception:
                self.logger.error("generate_site failed during Phase 8", exc_info=True)
                status_report["phase8_status"] = "failed_at_site_generation"
                return status_report
        
        # Re-detect changes after site generation to capture site artifacts
        raw_changes = change_detector.run()
        classification = classifier.classify(raw_changes)
        
        # Update metrics to include site files
        status_report["files_added"] = len(raw_changes.get("files_added", []))
        status_report["files_modified"] = len(raw_changes.get("files_modified", []))
        status_report["files_removed"] = len(raw_changes.get("files_removed", []))
        
        # 4. Commit
        auto_commit_enabled = config.is_feature_enabled("enable_auto_commit") and os.getenv("ENABLE_AUTOCOMMIT") == "true"
        
        if auto_commit_enabled:
            commit_mgr = CommitManager(is_dry_run=self.is_dry_run)
            success = commit_mgr.commit(classification["meaningful_changes"], classification["suggested_commit_message"])
            status_report["commit_created"] = success
            if not success and not self.is_dry_run:
                status_report["phase8_status"] = "failed_at_commit"
                return status_report
        else:
            self.logger.info("Auto-commit is disabled. Skipping commit.")
            
        # 5. Push
        auto_push_enabled = config.is_feature_enabled("enable_auto_push") and os.getenv("ENABLE_AUTOPUSH") == "true"
        
        if auto_push_enabled and (status_report["commit_created"] or self.is_dry_run):
            push_mgr = PushManager(is_dry_run=self.is_dry_run)
            success = push_mgr.push()
            status_report["push_completed"] = success
            if not success and not self.is_dry_run:
                status_report["phase8_status"] = "failed_at_push"
                return status_report
        elif status_report["commit_created"] or self.is_dry_run:
            self.logger.info("Auto-push is disabled. Skipping push.")
            
        status_report["phase8_status"] = "success"
        return status_report
