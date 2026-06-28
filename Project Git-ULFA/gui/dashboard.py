"""
Dashboard panel for Project Git-ULFA.

Shows a high-level overview: GitHub connection status, project statistics,
and a recent activity feed.
"""
from datetime import datetime
from typing import Optional

import customtkinter as ctk

from config.settings import AppSettings
from core.github_api import GitHubAPI
from utils.helpers import format_timestamp


class DashboardPanel(ctk.CTkFrame):
    """Main overview / dashboard panel."""

    def __init__(
        self,
        master,
        settings: AppSettings,
        project_manager,
        sync_engine,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._settings = settings
        self._pm = project_manager
        self._se = sync_engine

        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # Page title
        ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e6edf3",
            anchor="w",
        ).pack(fill="x", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            self,
            text="Overview of your GitHub synchronisation activity.",
            font=ctk.CTkFont(size=12),
            text_color="#8b949e",
            anchor="w",
        ).pack(fill="x", padx=24, pady=(0, 16))

        # ---- GitHub connection card ------------------------------------
        self._github_card = self._make_card(title="GitHub Connection")
        self._github_card.pack(fill="x", padx=24, pady=(0, 12))
        self._build_github_section(self._github_card)

        # ---- Stats row -------------------------------------------------
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=24, pady=(0, 12))
        stats_row.columnconfigure((0, 1, 2, 3), weight=1)

        self._stat_projects = self._make_stat(stats_row, "Projects", "0", col=0)
        self._stat_active = self._make_stat(stats_row, "Active Syncs", "0", col=1)
        self._stat_pending = self._make_stat(stats_row, "Pending Changes", "0", col=2)
        self._stat_kill = self._make_stat(stats_row, "Kill Switch", "Off", col=3)

        # ---- Quick actions card ----------------------------------------
        actions_card = self._make_card(title="Quick Actions")
        actions_card.pack(fill="x", padx=24, pady=(0, 12))
        self._build_actions(actions_card)

        # ---- Recent activity -------------------------------------------
        activity_card = self._make_card(title="Recent Activity")
        activity_card.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self._activity_box = ctk.CTkTextbox(
            activity_card,
            fg_color="#0d1117",
            text_color="#c9d1d9",
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled",
        )
        self._activity_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    def _build_github_section(self, parent: ctk.CTkFrame) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 4))

        self._gh_status_dot = ctk.CTkLabel(
            row, text="●", font=ctk.CTkFont(size=14), text_color="#8b949e", width=20
        )
        self._gh_status_dot.pack(side="left", padx=(0, 6))

        self._gh_status_label = ctk.CTkLabel(
            row,
            text="Not connected",
            font=ctk.CTkFont(size=13),
            text_color="#c9d1d9",
            anchor="w",
        )
        self._gh_status_label.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            row,
            text="Test Connection",
            width=130,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            command=self._test_connection,
        ).pack(side="right", padx=(8, 0))

    def _build_actions(self, parent: ctk.CTkFrame) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 4))

        btn_cfg = dict(
            height=34,
            font=ctk.CTkFont(size=12),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
        )
        ctk.CTkButton(
            row, text="⬆  Sync All Projects", **btn_cfg,
            command=self._sync_all,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            row, text="⬇  Pull All", **btn_cfg,
            command=self._pull_all,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            row, text="Refresh", **btn_cfg,
            command=self.refresh,
        ).pack(side="left")

    # ------------------------------------------------------------------
    # Public refresh
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        projects = self._pm.get_all()
        total = len(projects)
        active = sum(1 for p in projects if p.sync_enabled)
        pending = sum(p.pending_changes for p in projects)

        self._stat_projects.configure(text=str(total))
        self._stat_active.configure(text=str(active))
        self._stat_pending.configure(
            text=str(pending),
        )
        kill_state = "ON" if self._se.kill_switch_active else "Off"
        self._stat_kill.configure(
            text=kill_state,
            text_color="#f85149" if self._se.kill_switch_active else "#2ea043",
        )

    def set_github_status(self, connected: bool, username: str = "") -> None:
        if connected:
            self._gh_status_dot.configure(text_color="#2ea043")
            self._gh_status_label.configure(
                text=f"Connected as {username}" if username else "Connected"
            )
        else:
            self._gh_status_dot.configure(text_color="#8b949e")
            self._gh_status_label.configure(text="Not connected")

    def add_activity(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}]  {message}\n"
        self._activity_box.configure(state="normal")
        self._activity_box.insert("end", entry)
        self._activity_box.see("end")
        self._activity_box.configure(state="disabled")

    # ------------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------------

    def _test_connection(self) -> None:
        api = GitHubAPI(self._settings.github_token)
        ok, result = api.validate_token()
        self.set_github_status(ok, result if ok else "")
        msg = f"Connected as {result}" if ok else f"Connection failed: {result}"
        self.add_activity(msg)

    def _sync_all(self) -> None:
        for p in self._pm.get_all():
            if p.sync_enabled:
                self._se.sync_now(p.project_id)
        self.add_activity("Manual sync triggered for all active projects.")

    def _pull_all(self) -> None:
        for p in self._pm.get_all():
            if p.is_configured:
                self._se.pull_latest(p.project_id)
        self.add_activity("Pull triggered for all configured projects.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_card(self, title: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            self,
            fg_color="#161b22",
            corner_radius=8,
            border_width=1,
            border_color="#30363d",
        )
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#8b949e",
            anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 6))
        ctk.CTkFrame(card, height=1, fg_color="#30363d").pack(fill="x", padx=12, pady=(0, 8))
        return card

    def _make_stat(
        self, parent, label: str, value: str, col: int
    ) -> ctk.CTkLabel:
        cell = ctk.CTkFrame(
            parent,
            fg_color="#161b22",
            corner_radius=8,
            border_width=1,
            border_color="#30363d",
        )
        cell.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

        ctk.CTkLabel(
            cell,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color="#8b949e",
        ).pack(pady=(10, 2))

        val_label = ctk.CTkLabel(
            cell,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#e6edf3",
        )
        val_label.pack(pady=(0, 10))
        return val_label
