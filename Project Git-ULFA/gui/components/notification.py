"""
Toast notification system for Project Git-ULFA.

Displays temporary overlay notifications in the bottom-right corner of
the application window.
"""
import customtkinter as ctk


LEVEL_COLORS = {
    "success": "#2ea043",
    "info":    "#388bfd",
    "warning": "#FFA500",
    "error":   "#f85149",
}

LEVEL_ICONS = {
    "success": "✓",
    "info":    "ℹ",
    "warning": "⚠",
    "error":   "✕",
}


class Toast(ctk.CTkFrame):
    """A single toast notification bubble."""

    def __init__(
        self,
        master,
        message: str,
        level: str = "info",
        duration_ms: int = 4000,
        on_close=None,
        width: int = 360,
        height: int = 64,
    ) -> None:
        color = LEVEL_COLORS.get(level, "#388bfd")
        super().__init__(
            master,
            fg_color="#2b2b2b",
            corner_radius=8,
            border_width=1,
            border_color=color,
            width=width,
            height=height,
        )

        icon = LEVEL_ICONS.get(level, "ℹ")

        ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color,
            width=28,
        ).pack(side="left", padx=(10, 4), pady=12)

        ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color="#e0e0e0",
            wraplength=280,
            justify="left",
            anchor="w",
        ).pack(side="left", padx=(0, 32), pady=12, fill="x", expand=True)

        close_btn = ctk.CTkButton(
            self,
            text="×",
            width=24,
            height=24,
            fg_color="transparent",
            hover_color="#444444",
            font=ctk.CTkFont(size=14),
            command=self._dismiss,
        )
        close_btn.pack(side="right", padx=6)

        self._on_close = on_close
        self._after_id = self.after(duration_ms, self._dismiss)

    def _dismiss(self) -> None:
        try:
            self.after_cancel(self._after_id)
        except Exception:
            pass
        if self._on_close:
            self._on_close(self)
        self.destroy()


class NotificationManager:
    """
    Manages a stack of toast notifications anchored to the bottom-right of
    the host window.
    """

    _MARGIN_RIGHT = 16
    _MARGIN_BOTTOM = 60
    _TOAST_HEIGHT = 64
    _TOAST_GAP = 8
    _TOAST_WIDTH = 360

    def __init__(self, root: ctk.CTk) -> None:
        self._root = root
        self._toasts: list[Toast] = []

    def show(self, message: str, level: str = "info") -> None:
        """Display a toast notification."""
        toast = Toast(
            self._root,
            message=message,
            level=level,
            on_close=self._on_toast_closed,
            width=self._TOAST_WIDTH,
            height=self._TOAST_HEIGHT,
        )
        self._toasts.append(toast)
        self._reposition()

    def _on_toast_closed(self, toast: Toast) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
        self._reposition()

    def _reposition(self) -> None:
        """Stack toasts vertically above the bottom-right corner."""
        win_w = self._root.winfo_width()
        win_h = self._root.winfo_height()

        y = win_h - self._MARGIN_BOTTOM
        for toast in reversed(self._toasts):
            y -= self._TOAST_HEIGHT + self._TOAST_GAP
            x = win_w - self._TOAST_WIDTH - self._MARGIN_RIGHT
            toast.place(x=x, y=y)
