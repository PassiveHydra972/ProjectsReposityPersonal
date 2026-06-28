"""
Scheduler for Project Git-ULFA.

Wraps the *schedule* library to provide simple recurring task support.
The scheduler runs in a dedicated daemon thread.
"""
import threading
import time
from typing import Callable

try:
    import schedule as _schedule
    _SCHEDULE_AVAILABLE = True
except ImportError:
    _SCHEDULE_AVAILABLE = False


class Scheduler:
    """Runs scheduled jobs in a background thread."""

    def __init__(self) -> None:
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._run, name="Scheduler", daemon=True
        )
        if _SCHEDULE_AVAILABLE:
            # Use a separate scheduler instance to avoid global state collisions
            self._scheduler = _schedule.Scheduler()
        else:
            self._scheduler = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        while not self._stop.is_set():
            if self._scheduler is not None:
                try:
                    self._scheduler.run_pending()
                except Exception as exc:
                    print(f"[Scheduler] Job error: {exc}")
            time.sleep(1)

    # ------------------------------------------------------------------
    # Job registration helpers
    # ------------------------------------------------------------------

    def every_seconds(self, interval: int, job: Callable) -> None:
        """Schedule *job* to run every *interval* seconds."""
        if self._scheduler is not None:
            self._scheduler.every(interval).seconds.do(job)

    def every_minutes(self, interval: int, job: Callable) -> None:
        if self._scheduler is not None:
            self._scheduler.every(interval).minutes.do(job)

    def every_hours(self, interval: int, job: Callable) -> None:
        if self._scheduler is not None:
            self._scheduler.every(interval).hours.do(job)

    def clear_all(self) -> None:
        if self._scheduler is not None:
            self._scheduler.clear()
