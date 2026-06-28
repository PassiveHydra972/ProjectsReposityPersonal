"""
Status indicator widget for Project Git-ULFA.

A small coloured dot + label combination used in project cards and the
dashboard to communicate the current sync state at a glance.
"""
import customtkinter as ctk


STATUS_COLORS = {
    "active":        "#2ea043",
    "syncing":       "#388bfd",
    "paused":        "#888888",
    "error":         "#f85149",
    "pending_setup": "#FFA500",
    "disabled":      "#888888",
}

STATUS_LABELS = {
    "active":        "Active",
    "syncing":       "Syncing…",
    "paused":        "Paused",
    "error":         "Error",
    "pending_setup": "Needs Setup",
    "disabled":      "Disabled",
}


class StatusIndicator(ctk.CTkFrame):
    """Coloured circle + text label that shows a project's sync status."""

    DOT_SIZE = 10

    def __init__(self, master, status: str = "paused", **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._status = status

        self._dot = ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color=self._color_for(status),
            width=20,
            anchor="center",
        )
        self._dot.pack(side="left", padx=(0, 4))

        self._label = ctk.CTkLabel(
            self,
            text=self._text_for(status),
            font=ctk.CTkFont(size=12),
            text_color="#cccccc",
            anchor="w",
        )
        self._label.pack(side="left")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_status(self, status: str) -> None:
        if status == self._status:
            return
        self._status = status
        self._dot.configure(text_color=self._color_for(status))
        self._label.configure(text=self._text_for(status))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _color_for(status: str) -> str:
        return STATUS_COLORS.get(status, "#888888")

    @staticmethod
    def _text_for(status: str) -> str:
        return STATUS_LABELS.get(status, status.replace("_", " ").title())
