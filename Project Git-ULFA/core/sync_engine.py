"""
Synchronisation Engine for Project Git-ULFA.

The SyncEngine runs a background thread that:
  1. Polls per-project file monitors for changes.
  2. When a project's sync is enabled, batches changes and commits+pushes them.
  3. When sync is disabled, only tracks pending change counts.
  4. Emits GUI-safe events via the GUIEventQueue.

An emergency kill switch immediately suspends all activity.
"""
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from config.settings import AppSettings
from core.file_monitor import FileChange, FileMonitorRegistry
from core.git_manager import GitManager
from models.project import ProjectModel
from utils.helpers import EventBus, GUIEventQueue, now_iso
from utils.ignore_patterns import IgnoreMatcher, load_gitignore
from utils.logger import ProjectLogger


class SyncEngine:
    """Orchestrates file monitoring and GitHub synchronisation."""

    _POLL_INTERVAL = 5          # seconds between change-queue polls
    _LINK_QUEUE_INTERVAL = 15   # seconds between link-queue checks

    def __init__(
        self,
        settings: AppSettings,
        project_manager,          # ProjectManager (avoid circular import)
        git_manager: GitManager,
        event_bus: EventBus,
        gui_queue: GUIEventQueue,
    ) -> None:
        self._settings = settings
        self._pm = project_manager
        self._git = git_manager
        self._bus = event_bus
        self._gui_q = gui_queue

        self._registry = FileMonitorRegistry()
        self._kill_switch = threading.Event()   # set → all sync suspended
        self._stop_event = threading.Event()    # set → background thread exits

        # per-project accumulated changes since last commit
        self._pending: Dict[str, List[FileChange]] = {}
        # per-project last-sync timer
        self._last_push: Dict[str, float] = {}

        self._thread = threading.Thread(
            target=self._run, name="SyncEngine", daemon=True
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the sync engine background thread and all project monitors."""
        # Start monitors for projects that are already loaded
        for project in self._pm.get_all():
            self._start_monitor(project)
        self._thread.start()

    def stop(self) -> None:
        """Shut down the engine and all monitors."""
        self._stop_event.set()
        self._registry.stop_all()

    # ------------------------------------------------------------------
    # Kill switch
    # ------------------------------------------------------------------

    @property
    def kill_switch_active(self) -> bool:
        return self._kill_switch.is_set()

    def activate_kill_switch(self) -> None:
        self._kill_switch.set()
        self._gui_q.put("notification", message="Kill switch activated – all sync paused.",
                        level="warning")
        self._bus.emit("kill_switch_changed", active=True)

    def deactivate_kill_switch(self) -> None:
        self._kill_switch.clear()
        self._gui_q.put("notification", message="Kill switch deactivated – sync resumed.",
                        level="info")
        self._bus.emit("kill_switch_changed", active=False)

    # ------------------------------------------------------------------
    # Monitor management
    # ------------------------------------------------------------------

    def _start_monitor(self, project: ProjectModel) -> None:
        if not Path(project.local_path).exists():
            return
        patterns = list(self._settings.default_ignore_patterns)
        patterns += project.ignore_patterns
        patterns += load_gitignore(project.local_path)
        matcher = IgnoreMatcher(project.local_path, patterns)
        self._registry.start_monitor(project.project_id, project.local_path, matcher)
        self._pending.setdefault(project.project_id, [])
        self._last_push.setdefault(project.project_id, time.time())

    def add_project_monitor(self, project: ProjectModel) -> None:
        self._start_monitor(project)

    def remove_project_monitor(self, project_id: str) -> None:
        self._registry.stop_monitor(project_id)
        self._pending.pop(project_id, None)
        self._last_push.pop(project_id, None)

    # ------------------------------------------------------------------
    # Manual sync / pull
    # ------------------------------------------------------------------

    def sync_now(self, project_id: str) -> None:
        """Trigger an immediate sync for the given project (non-blocking)."""
        threading.Thread(
            target=self._perform_sync,
            args=(project_id, True),
            daemon=True,
        ).start()

    def pull_latest(self, project_id: str) -> None:
        """Pull the latest changes from the remote (non-blocking)."""
        threading.Thread(
            target=self._perform_pull,
            args=(project_id,),
            daemon=True,
        ).start()

    # ------------------------------------------------------------------
    # Background loop
    # ------------------------------------------------------------------

    def _run(self) -> None:
        """Main background loop – polls monitors and triggers syncs."""
        last_link_check = 0.0
        while not self._stop_event.is_set():
            now = time.time()

            # Periodically check the ULFA-Link queue
            if now - last_link_check >= self._LINK_QUEUE_INTERVAL:
                new_projects = self._pm.process_link_queue()
                for proj in new_projects:
                    self._start_monitor(proj)
                    self._gui_q.put("project_linked", project=proj)
                last_link_check = now

            if not self._kill_switch.is_set():
                for project in self._pm.get_all():
                    self._tick_project(project)

            time.sleep(self._POLL_INTERVAL)

    def _tick_project(self, project: ProjectModel) -> None:
        """Process one project during a poll cycle."""
        monitor = self._registry.get_monitor(project.project_id)
        if monitor is None:
            self._start_monitor(project)
            return

        changes = monitor.drain_changes()
        if not changes:
            # Nothing new – still check if a time-based sync is due
            if project.sync_enabled and project.live_sync:
                self._maybe_push_by_timer(project)
            return

        # Record pending changes
        pending = self._pending.setdefault(project.project_id, [])
        pending.extend(changes)
        self._pm.set_status(project.project_id, "active" if project.sync_enabled else "paused")

        # Notify GUI
        self._gui_q.put("pending_changed",
                        project_id=project.project_id,
                        count=len(pending))

        if not project.sync_enabled:
            # Accumulate, don't push
            return

        # Push immediately when the threshold is reached
        if len(pending) >= self._settings.max_changes_before_push:
            self._perform_sync(project.project_id)
        else:
            self._maybe_push_by_timer(project)

    def _maybe_push_by_timer(self, project: ProjectModel) -> None:
        """Push if the configured sync interval has elapsed."""
        last = self._last_push.get(project.project_id, 0.0)
        interval = project.sync_interval or self._settings.sync_interval
        if time.time() - last >= interval:
            pending = self._pending.get(project.project_id, [])
            if pending:
                self._perform_sync(project.project_id)

    # ------------------------------------------------------------------
    # Sync / pull implementation
    # ------------------------------------------------------------------

    def _perform_sync(
        self, project_id: str, force: bool = False
    ) -> None:
        """Commit and push all pending changes for *project_id*."""
        project = self._pm.get_project(project_id)
        if project is None:
            return

        token = self._settings.github_token
        if not token:
            self._gui_q.put("notification",
                            message=f"{project.project_name}: No GitHub token configured.",
                            level="error")
            return

        if not project.is_configured:
            self._gui_q.put("notification",
                            message=f"{project.project_name}: No GitHub repository set.",
                            level="warning")
            return

        pending = self._pending.get(project_id, [])
        if not pending and not force:
            return

        self._pm.set_status(project_id, "syncing")
        self._gui_q.put("status_changed", project_id=project_id, status="syncing")

        # Per-project logger
        logs_dir = self._settings.project_data_dir(project_id) / "logs"
        logger = ProjectLogger(project_id, project.project_name, logs_dir)
        logger.log_sync_start()
        for ch in pending:
            logger.log_file_event(ch.event_type, ch.src_path)

        try:
            # Ensure the repo is initialised
            ok, err = self._git.ensure_repo(project, token)
            if not ok:
                raise RuntimeError(err)

            # Pull first
            if self._settings.pull_before_push:
                ok, err = self._git.pull(project, token)
                if not ok:
                    logger.log_warning(f"Pull warning: {err}")
                else:
                    logger.log_pull()

            # Commit
            message = self._build_commit_message(project, pending)
            ok, sha = self._git.commit_all(project, message)
            if not ok and sha:  # sha contains error message when ok=False
                raise RuntimeError(sha)

            # Push
            ok, err = self._git.push(project, token)
            if not ok:
                raise RuntimeError(err)

            logger.log_push(project.repo_display)
            logger.log_sync_complete(sha)

            now = now_iso()
            self._pm.reset_pending(project_id, now)
            self._pending[project_id] = []
            self._last_push[project_id] = time.time()

            self._pm.set_status(project_id, "active")
            self._gui_q.put("sync_completed",
                            project_id=project_id,
                            last_sync=now)
            self._gui_q.put("notification",
                            message=f"{project.project_name}: Sync complete.",
                            level="success")

        except Exception as exc:
            error_msg = str(exc)
            logger.log_sync_error(error_msg)
            self._pm.set_status(project_id, "error", error_msg)
            self._gui_q.put("status_changed", project_id=project_id, status="error")
            self._gui_q.put("notification",
                            message=f"{project.project_name}: Sync failed – {error_msg}",
                            level="error")

    def _perform_pull(self, project_id: str) -> None:
        """Pull the latest remote changes for *project_id*."""
        project = self._pm.get_project(project_id)
        if project is None:
            return
        token = self._settings.github_token
        ok, err = self._git.pull(project, token)
        if ok:
            self._gui_q.put("notification",
                            message=f"{project.project_name}: Pull complete.",
                            level="success")
        else:
            self._gui_q.put("notification",
                            message=f"{project.project_name}: Pull failed – {err}",
                            level="error")

    # ------------------------------------------------------------------
    # Commit message builder
    # ------------------------------------------------------------------

    def _build_commit_message(
        self, project: ProjectModel, changes: List[FileChange]
    ) -> str:
        counts: Dict[str, int] = {}
        for ch in changes:
            counts[ch.event_type] = counts.get(ch.event_type, 0) + 1

        parts = [f"{v} {k}" for k, v in counts.items()]
        summary = ", ".join(parts) if parts else "changes"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")

        try:
            return project.commit_template.format(
                project_name=project.project_name,
                change_summary=summary,
                timestamp=ts,
            )
        except KeyError:
            return f"Git-ULFA: {summary} [{ts}]"
