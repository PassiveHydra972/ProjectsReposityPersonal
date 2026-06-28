"""
Thread-safe EventBus and miscellaneous utility helpers for Project Git-ULFA.
"""
import queue
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List


# ---------------------------------------------------------------------------
# EventBus
# ---------------------------------------------------------------------------

class EventBus:
    """
    Lightweight, thread-safe publish-subscribe event bus.

    Subscribers receive events via direct callback invocation from whatever
    thread calls ``emit``.  When the GUI subscribes, it should schedule work
    back on the main thread using widget.after().
    """

    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[..., None]]] = {}
        self._lock = threading.Lock()

    def subscribe(self, event: str, callback: Callable[..., None]) -> None:
        with self._lock:
            self._listeners.setdefault(event, []).append(callback)

    def unsubscribe(self, event: str, callback: Callable[..., None]) -> None:
        with self._lock:
            listeners = self._listeners.get(event, [])
            self._listeners[event] = [cb for cb in listeners if cb is not callback]

    def emit(self, event: str, **data: Any) -> None:
        with self._lock:
            listeners = list(self._listeners.get(event, []))
        for cb in listeners:
            try:
                cb(**data)
            except Exception as exc:  # pragma: no cover
                print(f"[EventBus] Error in '{event}' listener: {exc}")


# ---------------------------------------------------------------------------
# GUI event queue helpers
# ---------------------------------------------------------------------------

class GUIEventQueue:
    """
    A thread-safe queue for passing events from background threads to the
    Tkinter main thread.  The GUI polls this queue via widget.after().
    """

    def __init__(self) -> None:
        self._q: "queue.Queue[tuple[str, Dict[str, Any]]]" = queue.Queue()

    def put(self, event_type: str, **data: Any) -> None:
        self._q.put_nowait((event_type, data))

    def drain(self) -> List[tuple]:
        """Return all currently pending events without blocking."""
        events = []
        try:
            while True:
                events.append(self._q.get_nowait())
        except queue.Empty:
            pass
        return events


# ---------------------------------------------------------------------------
# Miscellaneous helpers
# ---------------------------------------------------------------------------

def format_timestamp(iso_str: str | None) -> str:
    """Convert an ISO-8601 string to a human-friendly display string."""
    if not iso_str:
        return "Never"
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return iso_str


def now_iso() -> str:
    """Return the current local time as an ISO-8601 string."""
    return datetime.now().isoformat()


def truncate(text: str, max_len: int = 40, ellipsis: str = "…") -> str:
    """Truncate *text* to *max_len* characters, appending *ellipsis* if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(ellipsis)] + ellipsis
