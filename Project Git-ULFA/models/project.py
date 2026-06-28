"""
Project data model for Project Git-ULFA.
"""
import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProjectModel:
    """Represents a single linked project managed by Git-ULFA."""

    project_name: str
    project_id: str
    local_path: str
    github_repository: str = ""
    branch: str = "main"
    sync_enabled: bool = False
    live_sync: bool = True
    date_linked: str = ""
    last_sync: Optional[str] = None
    sync_interval: int = 300
    commit_template: str = "Git-ULFA: Updated {project_name} - {timestamp}"
    backup_destinations: List[str] = field(default_factory=lambda: ["github"])
    ignore_patterns: List[str] = field(default_factory=list)
    status: str = "pending_setup"
    pending_changes: int = 0
    last_error: Optional[str] = None
    auto_push: bool = True
    max_changes_before_push: int = 10
    repo_subfolder: str = ""   # optional sub-path inside the repo, e.g. "projects/my-app"

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectModel":
        """Construct from a plain dictionary (e.g. loaded from JSON)."""
        known = {f.name for f in dataclasses.fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a JSON-serialisable dictionary."""
        return dataclasses.asdict(self)

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def is_configured(self) -> bool:
        """True when a GitHub repository has been set."""
        return bool(self.github_repository)

    @property
    def display_status(self) -> str:
        """Human-readable status label."""
        if not self.is_configured:
            return "Needs Setup"
        if not self.sync_enabled:
            return "Sync Disabled"
        return {
            "pending_setup": "Needs Setup",
            "active": "Active",
            "paused": "Paused",
            "error": "Error",
            "syncing": "Syncing…",
        }.get(self.status, self.status.replace("_", " ").title())

    @property
    def status_color(self) -> str:
        """Hex colour code matching the current status."""
        if not self.is_configured:
            return "#FFA500"
        if not self.sync_enabled:
            return "#888888"
        return {
            "pending_setup": "#FFA500",
            "active": "#2ea043",
            "paused": "#888888",
            "error": "#f85149",
            "syncing": "#388bfd",
        }.get(self.status, "#888888")

    @property
    def repo_display(self) -> str:
        """Short display string for the GitHub repository."""
        if self.github_repository:
            base = f"github.com/{self.github_repository}"
            if self.repo_subfolder:
                return f"{base} / {self.repo_subfolder.strip('/')}"
            return base
        return "Not configured"
