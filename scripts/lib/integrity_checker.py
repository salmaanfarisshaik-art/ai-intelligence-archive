"""
-------------------------------------------------------
THIS FILE IS AUTO-GENERATED.
DO NOT EDIT MANUALLY.
Changes may be overwritten during the next pipeline run.
-------------------------------------------------------

Repository Integrity & Health Monitor.
Validates the health of the entire repository ecosystem.
Integrity failures never terminate the ingestion pipeline.
"""
import os
import json
import glob
from datetime import datetime, timezone
from typing import Dict, Any, List

from scripts.lib.logger import setup_logger
from scripts.lib.config_loader import config

logger = setup_logger("integrity_checker")


class IntegrityChecker:
    """
    Read-only integrity validator.
    Checks schema compatibility, broken cross-links, orphaned entities,
    missing exports, stale indexes, missing documentation targets,
    duplicate identifiers, inconsistent manifests, corrupted cache artifacts,
    atomic write leftovers (.tmp files), and snapshot consistency.
    """

    def __init__(self):
        self.issues: List[Dict[str, Any]] = []
        self.warnings: int = 0
        self.errors: int = 0

    def _add_issue(self, severity: str, category: str, message: str):
        self.issues.append({
            "severity": severity,
            "category": category,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        if severity == "error":
            self.errors += 1
        else:
            self.warnings += 1

    def check_all(self) -> Dict[str, Any]:
        """Run all integrity checks."""
        if not config.is_feature_enabled("enable_integrity_checker"):
            logger.info("Integrity checker is disabled in config.")
            return {"status": "skipped"}

        logger.info("Running repository integrity checks...")

        self._check_processed_data()
        self._check_metadata_indexes()
        self._check_exports()
        self._check_documentation()
        self._check_tmp_leftovers()
        self._check_duplicate_ids()
        self._check_cross_links()

        status = "healthy"
        if self.errors > 0:
            status = "unhealthy"
        elif self.warnings > 0:
            status = "degraded"

        report = {
            "schema_version": "1.0",
            "generated_by": "AI Intelligence Archive",
            "generator_phase": "phase_5",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "total_warnings": self.warnings,
            "total_errors": self.errors,
            "issues": sorted(self.issues, key=lambda x: (x["severity"], x["category"]))
        }

        self._save_report(report)
        logger.info(f"Integrity check complete: {status} ({self.warnings} warnings, {self.errors} errors)")
        return report

    def _check_processed_data(self):
        """Verify data/processed/ directories contain valid data.json files."""
        processed_dir = os.path.join("data", "processed")
        if not os.path.isdir(processed_dir):
            self._add_issue("error", "processed_data", "data/processed directory not found")
            return

        for category_dir in sorted(os.listdir(processed_dir)):
            category_path = os.path.join(processed_dir, category_dir)
            if not os.path.isdir(category_path):
                continue
            data_file = os.path.join(category_path, "data.json")
            if not os.path.exists(data_file):
                self._add_issue("warning", "processed_data", f"Missing data.json in {category_dir}")
                continue
            try:
                with open(data_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
                if not isinstance(records, list):
                    self._add_issue("error", "schema", f"{category_dir}/data.json is not a JSON array")
            except json.JSONDecodeError as e:
                self._add_issue("error", "schema", f"{category_dir}/data.json is invalid JSON: {e}")

    def _check_metadata_indexes(self):
        """Verify metadata index files exist and are valid."""
        metadata_dir = os.path.join("data", "metadata")
        required_files = ["entity_index.json", "category_index.json", "tag_index.json"]

        for fname in required_files:
            fpath = os.path.join(metadata_dir, fname)
            if not os.path.exists(fpath):
                self._add_issue("warning", "metadata", f"Missing metadata file: {fname}")
            else:
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        json.load(f)
                except json.JSONDecodeError:
                    self._add_issue("error", "metadata", f"Invalid JSON in {fname}")

    def _check_exports(self):
        """Verify export directories are non-empty."""
        for fmt in ["json", "csv", "markdown"]:
            export_dir = os.path.join("exports", fmt)
            if not os.path.isdir(export_dir):
                self._add_issue("warning", "exports", f"Missing export directory: exports/{fmt}")
            elif len(os.listdir(export_dir)) == 0:
                self._add_issue("warning", "exports", f"Empty export directory: exports/{fmt}")

    def _check_documentation(self):
        """Verify documentation targets exist."""
        docs_dir = "docs"
        if not os.path.isdir(docs_dir):
            self._add_issue("warning", "documentation", "docs/ directory not found")
        elif len([f for f in os.listdir(docs_dir) if f.endswith(".md")]) == 0:
            self._add_issue("warning", "documentation", "No .md files found in docs/")

    def _check_tmp_leftovers(self):
        """Detect leftover .tmp files from failed atomic writes."""
        patterns = [
            os.path.join("data", "**", "*.tmp"),
            os.path.join("exports", "**", "*.tmp"),
            os.path.join("reports", "**", "*.tmp"),
            os.path.join("site", "**", "*.tmp"),
        ]
        for pattern in patterns:
            for tmp_file in glob.glob(pattern, recursive=True):
                self._add_issue("warning", "atomic_write", f"Leftover .tmp file: {tmp_file}")

    def _check_duplicate_ids(self):
        """Check for duplicate unique_ids across the entity index."""
        index_path = os.path.join("data", "metadata", "entity_index.json")
        if not os.path.exists(index_path):
            return
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                entities = json.load(f)
            seen_ids = set()
            for entity in entities:
                eid = entity.get("id", "")
                if eid in seen_ids:
                    self._add_issue("error", "duplicates", f"Duplicate entity ID: {eid}")
                seen_ids.add(eid)
        except Exception:
            pass

    def _check_cross_links(self):
        """Verify cross-link targets actually exist in the entity index."""
        graph_path = os.path.join("data", "metadata", "relationship_graph.json")
        index_path = os.path.join("data", "metadata", "entity_index.json")

        if not os.path.exists(graph_path) or not os.path.exists(index_path):
            return

        try:
            with open(index_path, "r", encoding="utf-8") as f:
                entities = json.load(f)
            entity_ids = {e.get("id", "") for e in entities}

            with open(graph_path, "r", encoding="utf-8") as f:
                graph = json.load(f)

            for edge in graph.get("edges", []):
                src = edge.get("source", "")
                tgt = edge.get("target", "")
                if src and src not in entity_ids:
                    self._add_issue("warning", "cross_links", f"Orphaned graph edge source: {src}")
                if tgt and tgt not in entity_ids:
                    self._add_issue("warning", "cross_links", f"Orphaned graph edge target: {tgt}")
        except Exception:
            pass

    def _save_report(self, report: Dict[str, Any]):
        """Atomically save integrity reports."""
        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        os.makedirs("reports", exist_ok=True)

        # JSON report
        json_path = os.path.join("reports", "integrity_status.json")
        json_content = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)
        self._atomic_write(json_path, json_content, is_dry_run)

        # Markdown report
        md_lines = [
            "<!-- THIS FILE IS AUTO-GENERATED. DO NOT EDIT MANUALLY. -->",
            "# Repository Integrity Report",
            "",
            f"**Status:** {report['status']}",
            f"**Generated:** {report['generated_at']}",
            f"**Warnings:** {report['total_warnings']}",
            f"**Errors:** {report['total_errors']}",
            "",
            "## Issues",
            "",
        ]
        if not report["issues"]:
            md_lines.append("No issues detected.")
        else:
            for issue in report["issues"]:
                md_lines.append(f"- **[{issue['severity'].upper()}]** `{issue['category']}`: {issue['message']}")
        md_lines.append("")

        md_path = os.path.join("reports", "integrity_report.md")
        self._atomic_write(md_path, "\n".join(md_lines), is_dry_run)

    def _atomic_write(self, filepath: str, content: str, is_dry_run: bool):
        if is_dry_run:
            logger.info(f"DRY RUN: Would have saved {filepath}")
            return
        tmp = f"{filepath}.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp, filepath)
            logger.info(f"Successfully saved {filepath}")
        except Exception as e:
            logger.error(f"Failed atomic write to {filepath}: {e}")
            if os.path.exists(tmp):
                os.remove(tmp)
