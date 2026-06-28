"""
Project Manager for Project Git-ULFA.

Loads, saves, and manages the list of linked projects.  Also polls the
link-queue file written by ULFA-Link.py so that newly linked folders are
automatically picked up while the application is running.
"""
import json
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional

from config.settings import AppSettings
from models.project import ProjectModel
from utils.helpers import EventBus, now_iso


class ProjectManager:
    """Manages the full lifecycle of linked projects."""

    def __init__(self, settings: AppSettings, event_bus: EventBus) -> None:
        self._settings = settings
        self._bus = event_bus
        self._lock = threading.Lock()
        self._projects: Dict[str, ProjectModel] = {}
        self._load_all()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_all(self) -> None:
        """Load all projects from the projects JSON file."""
        path = self._settings.PROJECTS_FILE
        if not path.exists():
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                raw_list = json.load(fh)
            for raw in raw_list:
                proj = ProjectModel.from_dict(raw)
                self._projects[proj.project_id] = proj
        except (json.JSONDecodeError, OSError, TypeError):
            pass

    def _save_all(self) -> None:
        """Write the full project list to disk."""
        path = self._settings.PROJECTS_FILE
        try:
            data = [p.to_dict() for p in self._projects.values()]
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
        except OSError as exc:
            print(f"[ProjectManager] Failed to save projects: {exc}")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def get_all(self) -> List[ProjectModel]:
        with self._lock:
            return list(self._projects.values())

    def get_project(self, project_id: str) -> Optional[ProjectModel]:
        with self._lock:
            return self._projects.get(project_id)

    def add_project(self, project: ProjectModel) -> None:
        """Add a new project and persist it."""
        with self._lock:
            self._projects[project.project_id] = project
            self._save_all()
        # Ensure per-project data directory structure exists
        self._settings.project_data_dir(project.project_id)
        self._bus.emit("project_added", project=project)

    def update_project(self, project: ProjectModel) -> None:
        """Persist changes to an existing project."""
        with self._lock:
            self._projects[project.project_id] = project
            self._save_all()
        self._bus.emit("project_updated", project=project)

    def remove_project(self, project_id: str) -> None:
        """Remove a project from the managed list (does NOT delete local files)."""
        with self._lock:
            removed = self._projects.pop(project_id, None)
            if removed is not None:
                self._save_all()
        if removed:
            self._bus.emit("project_removed", project=removed)

    def save_project(self, project: ProjectModel) -> None:
        """Alias for update_project – used by the sync engine."""
        self.update_project(project)

    # ------------------------------------------------------------------
    # Link-queue processing
    # ------------------------------------------------------------------

    def process_link_queue(self) -> List[ProjectModel]:
        """
        Read projects queued by ULFA-Link.py, add them to the managed list,
        and clear the queue.  Returns the list of newly added projects.
        """
        queue_file = self._settings.LINK_QUEUE_FILE
        if not queue_file.exists():
            return []

        added: List[ProjectModel] = []
        try:
            with open(queue_file, "r", encoding="utf-8") as fh:
                queued = json.load(fh)

            for raw in queued:
                proj = ProjectModel.from_dict(raw)
                if proj.project_id not in self._projects:
                    proj.date_linked = proj.date_linked or now_iso()
                    self.add_project(proj)
                    added.append(proj)

            # Clear the queue
            queue_file.write_text("[]", encoding="utf-8")
        except (json.JSONDecodeError, OSError):
            pass

        return added

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def set_sync_enabled(self, project_id: str, enabled: bool) -> None:
        proj = self.get_project(project_id)
        if proj is None:
            return
        proj.sync_enabled = enabled
        proj.status = "active" if enabled else "paused"
        self.update_project(proj)

    def set_status(
        self,
        project_id: str,
        status: str,
        error: Optional[str] = None,
    ) -> None:
        proj = self.get_project(project_id)
        if proj is None:
            return
        proj.status = status
        if error is not None:
            proj.last_error = error
        self.update_project(proj)

    def increment_pending(self, project_id: str) -> None:
        proj = self.get_project(project_id)
        if proj is None:
            return
        proj.pending_changes += 1
        # Lightweight update – avoid firing heavy "project_updated" event;
        # we still persist so the count survives restarts.
        with self._lock:
            self._save_all()

    def reset_pending(self, project_id: str, last_sync: str) -> None:
        proj = self.get_project(project_id)
        if proj is None:
            return
        proj.pending_changes = 0
        proj.last_sync = last_sync
        self.update_project(proj)
