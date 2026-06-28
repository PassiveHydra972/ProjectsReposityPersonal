"""
Logging system for Project Git-ULFA.

Each project writes dated log files to ~/.git-ulfa/projects/{id}/logs/.
A global application log is written to ~/.git-ulfa/logs/.
"""
import logging
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional


_FORMATTER = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s",
                               datefmt="%H:%M:%S")


def _file_handler(log_path: Path) -> logging.FileHandler:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(_FORMATTER)
    return handler


def get_app_logger(logs_dir: Path) -> logging.Logger:
    """Return (or create) the global application logger."""
    logger = logging.getLogger("git_ulfa.app")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        today = date.today().isoformat()
        logger.addHandler(_file_handler(logs_dir / f"{today}.log"))
        # Also echo to stderr at INFO level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(_FORMATTER)
        logger.addHandler(ch)
    return logger


def get_project_logger(project_id: str, project_logs_dir: Path) -> logging.Logger:
    """Return (or create) a per-project logger."""
    name = f"git_ulfa.project.{project_id}"
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        today = date.today().isoformat()
        logger.addHandler(_file_handler(project_logs_dir / f"{today}.log"))
        logger.propagate = False  # Do not bubble up to root / app logger
    return logger


class ProjectLogger:
    """
    Convenience wrapper that writes human-readable sync log entries to a
    project's daily log file AND to the standard Python logging system.
    """

    def __init__(self, project_id: str, project_name: str, logs_dir: Path) -> None:
        self._project_id = project_id
        self._project_name = project_name
        self._logs_dir = logs_dir
        self._logger = get_project_logger(project_id, logs_dir)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _raw_log_path(self) -> Path:
        today = date.today().isoformat()
        return self._logs_dir / f"{today}.log"

    def _write_raw(self, lines: list[str]) -> None:
        """Append raw lines to the plain-text daily log."""
        path = self._raw_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_sync_start(self) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._write_raw([f"\n{'─' * 48}", f"Sync started  {ts}", f"{'─' * 48}"])
        self._logger.info("Sync started")

    def log_sync_complete(self, commit_sha: str = "") -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        lines = [f"Sync completed  {ts}"]
        if commit_sha:
            lines.append(f"Commit: {commit_sha[:12]}")
        self._write_raw(lines)
        self._logger.info("Sync completed  commit=%s", commit_sha[:12] if commit_sha else "-")

    def log_sync_error(self, error: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._write_raw([f"Sync FAILED  {ts}", f"Error: {error}"])
        self._logger.error("Sync failed: %s", error)

    def log_file_event(self, event_type: str, path: str) -> None:
        self._write_raw([f"  {event_type:<10} {path}"])
        self._logger.debug("%s  %s", event_type, path)

    def log_push(self, remote: str) -> None:
        self._write_raw([f"Push → {remote}"])
        self._logger.info("Pushed to %s", remote)

    def log_pull(self) -> None:
        self._write_raw(["Pull ← remote"])
        self._logger.info("Pulled from remote")

    def log_info(self, message: str) -> None:
        self._write_raw([f"  {message}"])
        self._logger.info(message)

    def log_warning(self, message: str) -> None:
        self._write_raw([f"  WARNING: {message}"])
        self._logger.warning(message)

    def read_today_log(self) -> str:
        """Return today's raw log text (for the Logs panel)."""
        path = self._raw_log_path()
        if path.exists():
            try:
                return path.read_text(encoding="utf-8")
            except OSError:
                return ""
        return ""

    def list_log_dates(self) -> list[str]:
        """Return a sorted list of dates for which log files exist."""
        if not self._logs_dir.exists():
            return []
        dates = [
            p.stem for p in self._logs_dir.glob("*.log")
        ]
        return sorted(dates, reverse=True)

    def read_log_for_date(self, log_date: str) -> str:
        path = self._logs_dir / f"{log_date}.log"
        if path.exists():
            try:
                return path.read_text(encoding="utf-8")
            except OSError:
                return ""
        return ""

    def purge_old_logs(self, retention_days: int = 30) -> None:
        """Delete log files older than *retention_days* days."""
        if not self._logs_dir.exists():
            return
        cutoff = date.today() - timedelta(days=retention_days)
        for p in self._logs_dir.glob("*.log"):
            try:
                log_date = date.fromisoformat(p.stem)
                if log_date < cutoff:
                    p.unlink(missing_ok=True)
            except ValueError:
                pass
