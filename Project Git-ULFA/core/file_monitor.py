"""
File system monitoring for Project Git-ULFA.

Uses the *watchdog* library to detect file creation, modification, deletion,
and renames inside a project folder.  Each event is placed in a thread-safe
queue for the SyncEngine to consume.
"""
import queue
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from watchdog.events import (
    DirCreatedEvent,
    DirDeletedEvent,
    DirModifiedEvent,
    DirMovedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from utils.ignore_patterns import IgnoreMatcher


# ---------------------------------------------------------------------------
# Change event dataclass
# ---------------------------------------------------------------------------

@dataclass
class FileChange:
    """Represents a single detected file-system change."""

    event_type: str          # created | modified | deleted | renamed
    src_path: str
    dest_path: str = ""      # only set for moves/renames
    is_directory: bool = False


# ---------------------------------------------------------------------------
# Watchdog event handler
# ---------------------------------------------------------------------------

class _Handler(FileSystemEventHandler):
    """Watchdog handler that converts raw events into FileChange objects."""

    def __init__(
        self,
        change_queue: "queue.Queue[FileChange]",
        matcher: IgnoreMatcher,
    ) -> None:
        super().__init__()
        self._q = change_queue
        self._matcher = matcher

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _should_ignore(self, path: str) -> bool:
        # Fast-path: always block .git internals regardless of platform path
        # separators or matcher edge-cases.
        normalized = path.replace('\\', '/')
        if '/.git/' in normalized or normalized.endswith('/.git'):
            return True
        return self._matcher.is_ignored(path)

    def _put(self, change: FileChange) -> None:
        self._q.put_nowait(change)

    # ------------------------------------------------------------------
    # Event callbacks
    # ------------------------------------------------------------------

    def on_created(self, event: FileSystemEvent) -> None:
        if self._should_ignore(event.src_path):
            return
        self._put(FileChange(
            event_type="created",
            src_path=event.src_path,
            is_directory=event.is_directory,
        ))

    def on_deleted(self, event: FileSystemEvent) -> None:
        if self._should_ignore(event.src_path):
            return
        self._put(FileChange(
            event_type="deleted",
            src_path=event.src_path,
            is_directory=event.is_directory,
        ))

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if self._should_ignore(event.src_path):
            return
        self._put(FileChange(
            event_type="modified",
            src_path=event.src_path,
            is_directory=False,
        ))

    def on_moved(self, event: FileSystemEvent) -> None:
        if self._should_ignore(event.src_path):
            return
        self._put(FileChange(
            event_type="renamed",
            src_path=event.src_path,
            dest_path=getattr(event, "dest_path", ""),
            is_directory=event.is_directory,
        ))


# ---------------------------------------------------------------------------
# Per-project monitor
# ---------------------------------------------------------------------------

class ProjectMonitor:
    """
    Wraps a watchdog Observer for a single project directory.
    Exposes the change queue for the SyncEngine to read from.
    """

    def __init__(self, project_id: str, path: str, matcher: IgnoreMatcher) -> None:
        self.project_id = project_id
        self._path = path
        self._change_queue: "queue.Queue[FileChange]" = queue.Queue()
        self._handler = _Handler(self._change_queue, matcher)
        self._observer: Optional[Observer] = None
        self._running = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._running:
            return
        self._observer = Observer()
        self._observer.schedule(self._handler, self._path, recursive=True)
        self._observer.start()
        self._running = True

    def stop(self) -> None:
        if not self._running or self._observer is None:
            return
        self._observer.stop()
        self._observer.join(timeout=5)
        self._observer = None
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    # ------------------------------------------------------------------
    # Queue access
    # ------------------------------------------------------------------

    def drain_changes(self) -> list[FileChange]:
        """Return all currently queued changes without blocking."""
        changes: list[FileChange] = []
        try:
            while True:
                changes.append(self._change_queue.get_nowait())
        except queue.Empty:
            pass
        return changes

    def has_changes(self) -> bool:
        return not self._change_queue.empty()


# ---------------------------------------------------------------------------
# Monitor registry
# ---------------------------------------------------------------------------

class FileMonitorRegistry:
    """Manages a collection of ProjectMonitors, one per linked project."""

    def __init__(self) -> None:
        self._monitors: Dict[str, ProjectMonitor] = {}
        self._lock = threading.Lock()

    def start_monitor(
        self,
        project_id: str,
        path: str,
        matcher: IgnoreMatcher,
    ) -> ProjectMonitor:
        with self._lock:
            if project_id in self._monitors:
                return self._monitors[project_id]
            monitor = ProjectMonitor(project_id, path, matcher)
            monitor.start()
            self._monitors[project_id] = monitor
            return monitor

    def stop_monitor(self, project_id: str) -> None:
        with self._lock:
            monitor = self._monitors.pop(project_id, None)
        if monitor:
            monitor.stop()

    def stop_all(self) -> None:
        with self._lock:
            monitors = list(self._monitors.values())
            self._monitors.clear()
        for m in monitors:
            m.stop()

    def get_monitor(self, project_id: str) -> Optional[ProjectMonitor]:
        with self._lock:
            return self._monitors.get(project_id)

    def all_monitors(self) -> list[ProjectMonitor]:
        with self._lock:
            return list(self._monitors.values())
