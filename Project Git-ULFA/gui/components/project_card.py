"""
Project card widget for Project Git-ULFA.

Each linked project is displayed as a card in the Projects panel.
"""
import os
import subprocess
import webbrowser
from typing import Callable, Optional

import customtkinter as ctk

from gui.components.status_indicator import StatusIndicator
from models.project import ProjectModel
from utils.helpers import format_timestamp


class ProjectCard(ctk.CTkFrame):
    """A card widget displaying one linked project with action buttons."""

    def __init__(
        self,
        master,
        project: ProjectModel,
        on_sync_now: Optional[Callable[[str], None]] = None,
        on_toggle_sync: Optional[Callable[[str, bool], None]] = None,
        on_open_folder: Optional[Callable[[str], None]] = None,
        on_open_repo: Optional[Callable[[str], None]] = None,
        on_configure: Optional[Callable[[str], None]] = None,
        on_remove: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            fg_color="#1e2030",
            corner_radius=10,
            border_width=1,
            border_color="#30363d",
            **kwargs,
        )
        self._project = project
        self._on_sync_now = on_sync_now
        self._on_toggle_sync = on_toggle_sync
        self._on_open_folder = on_open_folder
        self._on_open_repo = on_open_repo
        self._on_configure = on_configure
        self._on_remove = on_remove

        self._build()

    # ------------------------------------------------------------------
    # Build layout
    # ------------------------------------------------------------------

    def _build(self) -> None:
        p = self._project

        # ---- Header row ------------------------------------------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(12, 4))

        # Name
        ctk.CTkLabel(
            header,
            text=p.project_name,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#e6edf3",
            anchor="w",
        ).pack(side="left")

        # Status indicator (right-aligned)
        self._status_ind = StatusIndicator(
            header,
            status=p.status if p.sync_enabled else "disabled",
        )
        self._status_ind.pack(side="right")

        # ---- Details row -----------------------------------------------
        details = ctk.CTkFrame(self, fg_color="transparent")
        details.pack(fill="x", padx=14, pady=2)

        # Repository
        ctk.CTkLabel(
            details,
            text=p.repo_display,
            font=ctk.CTkFont(size=11),
            text_color="#8b949e",
            anchor="w",
        ).pack(side="left")

        # Branch badge
        if p.branch:
            ctk.CTkLabel(
                details,
                text=f"  ⎇ {p.branch}",
                font=ctk.CTkFont(size=11),
                text_color="#8b949e",
            ).pack(side="left")

        # ---- Stats row -------------------------------------------------
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=14, pady=2)

        self._last_sync_label = ctk.CTkLabel(
            stats,
            text=f"Last sync: {format_timestamp(p.last_sync)}",
            font=ctk.CTkFont(size=11),
            text_color="#8b949e",
            anchor="w",
        )
        self._last_sync_label.pack(side="left")

        self._pending_label = ctk.CTkLabel(
            stats,
            text=self._pending_text(p.pending_changes),
            font=ctk.CTkFont(size=11),
            text_color="#FFA500" if p.pending_changes > 0 else "#8b949e",
        )
        self._pending_label.pack(side="right")

        # ---- Divider ---------------------------------------------------
        ctk.CTkFrame(self, height=1, fg_color="#30363d").pack(
            fill="x", padx=14, pady=(8, 0)
        )

        # ---- Action buttons row ----------------------------------------
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=(4, 10))

        # Sync toggle switch
        self._sync_switch = ctk.CTkSwitch(
            actions,
            text="Live Sync",
            font=ctk.CTkFont(size=12),
            command=self._on_switch_toggle,
            width=80,
            button_color="#388bfd",
            progress_color="#388bfd",
        )
        if p.sync_enabled:
            self._sync_switch.select()
        else:
            self._sync_switch.deselect()
        self._sync_switch.pack(side="left", padx=(4, 12))

        # Sync Now
        ctk.CTkButton(
            actions,
            text="Sync Now",
            width=88,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            command=self._cmd_sync_now,
        ).pack(side="left", padx=3)

        # Open Folder
        ctk.CTkButton(
            actions,
            text="📁 Folder",
            width=80,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            command=self._cmd_open_folder,
        ).pack(side="left", padx=3)

        # Open Repository
        ctk.CTkButton(
            actions,
            text="⎋ GitHub",
            width=80,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            command=self._cmd_open_repo,
        ).pack(side="left", padx=3)

        # Configure
        ctk.CTkButton(
            actions,
            text="⚙",
            width=34,
            height=28,
            font=ctk.CTkFont(size=14),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            command=self._cmd_configure,
        ).pack(side="left", padx=3)

        # Remove (right-aligned)
        ctk.CTkButton(
            actions,
            text="✕",
            width=34,
            height=28,
            font=ctk.CTkFont(size=14),
            fg_color="#21262d",
            hover_color="#f85149",
            text_color="#f85149",
            border_width=1,
            border_color="#30363d",
            command=self._cmd_remove,
        ).pack(side="right", padx=3)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update_project(self, project: ProjectModel) -> None:
        self._project = project
        self._status_ind.set_status(
            project.status if project.sync_enabled else "disabled"
        )
        self._last_sync_label.configure(
            text=f"Last sync: {format_timestamp(project.last_sync)}"
        )
        self._pending_label.configure(
            text=self._pending_text(project.pending_changes),
            text_color="#FFA500" if project.pending_changes > 0 else "#8b949e",
        )
        if project.sync_enabled:
            self._sync_switch.select()
        else:
            self._sync_switch.deselect()

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def _on_switch_toggle(self) -> None:
        enabled = self._sync_switch.get() == 1
        if self._on_toggle_sync:
            self._on_toggle_sync(self._project.project_id, enabled)

    def _cmd_sync_now(self) -> None:
        if self._on_sync_now:
            self._on_sync_now(self._project.project_id)

    def _cmd_open_folder(self) -> None:
        if self._on_open_folder:
            self._on_open_folder(self._project.project_id)
        else:
            path = self._project.local_path
            if os.path.isdir(path):
                os.startfile(path)

    def _cmd_open_repo(self) -> None:
        if self._on_open_repo:
            self._on_open_repo(self._project.project_id)
        elif self._project.github_repository:
            webbrowser.open(
                f"https://github.com/{self._project.github_repository}"
            )

    def _cmd_configure(self) -> None:
        if self._on_configure:
            self._on_configure(self._project.project_id)

    def _cmd_remove(self) -> None:
        if self._on_remove:
            self._on_remove(self._project.project_id)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pending_text(count: int) -> str:
        if count == 0:
            return "No pending changes"
        return f"⬆ {count} pending change{'s' if count != 1 else ''}"
