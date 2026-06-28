"""
Sidebar navigation for Project Git-ULFA.
"""
from typing import Callable

import customtkinter as ctk


NAV_ITEMS = [
    ("dashboard",  "⊞  Dashboard"),
    ("projects",   "📁  Projects"),
    ("logs",       "📋  Logs"),
    ("settings",   "⚙   Settings"),
]


class Sidebar(ctk.CTkFrame):
    """Left-hand navigation sidebar."""

    def __init__(
        self,
        master,
        on_navigate: Callable[[str], None],
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            width=200,
            fg_color="#161b22",
            corner_radius=0,
            **kwargs,
        )
        self._on_navigate = on_navigate
        self._active: str = "dashboard"
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._kill_active = False

        self.pack_propagate(False)
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # App title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", pady=(20, 8))

        ctk.CTkLabel(
            title_frame,
            text="Git-ULFA",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#e6edf3",
        ).pack(padx=20, anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Universal Local Files Archiver",
            font=ctk.CTkFont(size=10),
            text_color="#8b949e",
        ).pack(padx=20, anchor="w")

        # Divider
        ctk.CTkFrame(self, height=1, fg_color="#30363d").pack(
            fill="x", padx=12, pady=(8, 12)
        )

        # Navigation buttons
        for page_id, label in NAV_ITEMS:
            btn = ctk.CTkButton(
                self,
                text=label,
                anchor="w",
                height=40,
                corner_radius=6,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                hover_color="#21262d",
                text_color="#c9d1d9",
                command=lambda pid=page_id: self._navigate(pid),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._buttons[page_id] = btn

        # Spacer
        ctk.CTkFrame(self, fg_color="transparent").pack(fill="both", expand=True)

        # Divider
        ctk.CTkFrame(self, height=1, fg_color="#30363d").pack(
            fill="x", padx=12, pady=4
        )

        # Kill switch
        self._kill_btn = ctk.CTkButton(
            self,
            text="🔴  Kill Switch",
            height=38,
            corner_radius=6,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#21262d",
            hover_color="#f85149",
            text_color="#f85149",
            border_width=1,
            border_color="#f85149",
            command=self._toggle_kill,
        )
        self._kill_btn.pack(fill="x", padx=10, pady=(4, 16))

        # Highlight active page
        self._set_active(self._active)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _navigate(self, page_id: str) -> None:
        self._set_active(page_id)
        self._on_navigate(page_id)

    def _set_active(self, page_id: str) -> None:
        # Deactivate previous
        for pid, btn in self._buttons.items():
            if pid == page_id:
                btn.configure(fg_color="#21262d", text_color="#58a6ff")
            else:
                btn.configure(fg_color="transparent", text_color="#c9d1d9")
        self._active = page_id

    # ------------------------------------------------------------------
    # Kill switch
    # ------------------------------------------------------------------

    def _toggle_kill(self) -> None:
        # Delegate actual logic to the app; just update the visual state here
        self._on_navigate("__kill_switch__")

    def set_kill_switch_active(self, active: bool) -> None:
        self._kill_active = active
        if active:
            self._kill_btn.configure(
                text="🟢  Resume Sync",
                fg_color="#f85149",
                text_color="#ffffff",
                hover_color="#da3633",
            )
        else:
            self._kill_btn.configure(
                text="🔴  Kill Switch",
                fg_color="#21262d",
                text_color="#f85149",
                hover_color="#f85149",
            )

    # ------------------------------------------------------------------
    # Status indicator
    # ------------------------------------------------------------------

    def set_connection_status(self, connected: bool, username: str = "") -> None:
        """Update the connection badge at the bottom of the sidebar (if added)."""
        pass  # Future: small label or dot at the bottom
