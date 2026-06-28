"""
Application settings management for Project Git-ULFA.
Settings are persisted to ~/.git-ulfa/settings.json.
"""
import json
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_SETTINGS: Dict[str, Any] = {
    "github_token": "",
    "github_username": "",
    "default_branch": "main",
    "sync_interval": 300,
    "max_changes_before_push": 10,
    "commit_template": "Git-ULFA: {change_summary} [{timestamp}]",
    "pull_before_push": True,
    "auto_start_sync": False,
    "minimize_to_tray": True,
    "show_notifications": True,
    "theme": "dark",
    "log_retention_days": 30,
    "termination_password": "",
    "default_ignore_patterns": [
        ".git",
        "__pycache__",
        ".idea",
        ".vscode",
        "node_modules",
        "build",
        "dist",
        "*.tmp",
        "*.bak",
        "*.swp",
        ".DS_Store",
        "Thumbs.db",
        "*.pyc",
        ".env",
    ],
}


class AppSettings:
    """Manages application-wide settings stored as JSON."""

    DATA_DIR: Path = Path.home() / ".git-ulfa"
    SETTINGS_FILE: Path = DATA_DIR / "settings.json"
    PROJECTS_FILE: Path = DATA_DIR / "projects.json"
    LINK_QUEUE_FILE: Path = DATA_DIR / "link_queue.json"
    PROJECTS_DATA_DIR: Path = DATA_DIR / "projects"
    LOGS_DIR: Path = DATA_DIR / "logs"

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}
        self._ensure_dirs()
        self._load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_dirs(self) -> None:
        """Create required data directories if they do not exist."""
        for directory in (
            self.DATA_DIR,
            self.PROJECTS_DATA_DIR,
            self.LOGS_DIR,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def _load(self) -> None:
        """Load settings from disk, falling back to defaults."""
        self._data = dict(DEFAULT_SETTINGS)
        if self.SETTINGS_FILE.exists():
            try:
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as fh:
                    saved = json.load(fh)
                    self._data.update(saved)
            except (json.JSONDecodeError, OSError):
                pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Persist current settings to disk."""
        try:
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2)
        except OSError as exc:
            print(f"[Settings] Failed to save: {exc}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def github_token(self) -> str:
        return self._data.get("github_token", "")

    @github_token.setter
    def github_token(self, value: str) -> None:
        self._data["github_token"] = value

    @property
    def github_username(self) -> str:
        return self._data.get("github_username", "")

    @github_username.setter
    def github_username(self, value: str) -> None:
        self._data["github_username"] = value

    @property
    def sync_interval(self) -> int:
        return int(self._data.get("sync_interval", 300))

    @property
    def max_changes_before_push(self) -> int:
        return int(self._data.get("max_changes_before_push", 10))

    @property
    def commit_template(self) -> str:
        return self._data.get(
            "commit_template", "Git-ULFA: {change_summary} [{timestamp}]"
        )

    @property
    def pull_before_push(self) -> bool:
        return bool(self._data.get("pull_before_push", True))

    @property
    def default_ignore_patterns(self) -> List[str]:
        return list(self._data.get("default_ignore_patterns", []))

    @property
    def log_retention_days(self) -> int:
        return int(self._data.get("log_retention_days", 30))

    @property
    def show_notifications(self) -> bool:
        return bool(self._data.get("show_notifications", True))

    def project_data_dir(self, project_id: str) -> Path:
        """Return (and create) the per-project data directory."""
        p = self.PROJECTS_DATA_DIR / project_id
        for sub in ("metadata", "cache", "history", "logs", "pending", "snapshots"):
            (p / sub).mkdir(parents=True, exist_ok=True)
        return p
