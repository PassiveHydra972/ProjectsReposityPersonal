"""
Main application window for Project Git-ULFA.

Wires together all panels, the sync engine, and the GUI event queue.
"""
import threading
from typing import Any, Dict

import customtkinter as ctk

from config.settings import AppSettings
from core.git_manager import GitManager
from core.github_api import GitHubAPI
from core.project_manager import ProjectManager
from core.sync_engine import SyncEngine
from gui.components.notification import NotificationManager
from gui.dashboard import DashboardPanel
from gui.logs_panel import LogsPanel
from gui.projects_panel import ProjectsPanel
from gui.settings_panel import SettingsPanel
from gui.sidebar import Sidebar
from utils.helpers import EventBus, GUIEventQueue

# Apply dark theme before any CTk widget is created
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GitULFAApp(ctk.CTk):
    """The root application window."""

    _WIDTH = 1200
    _HEIGHT = 720
    _MIN_WIDTH = 900
    _MIN_HEIGHT = 580

    def __init__(self) -> None:
        super().__init__()

        # ---- Core services ----
        self.settings = AppSettings()
        self.event_bus = EventBus()
        self.gui_queue = GUIEventQueue()
        self.project_manager = ProjectManager(self.settings, self.event_bus)
        self.git_manager = GitManager()
        self.sync_engine = SyncEngine(
            settings=self.settings,
            project_manager=self.project_manager,
            git_manager=self.git_manager,
            event_bus=self.event_bus,
            gui_queue=self.gui_queue,
        )
        self.github_api = GitHubAPI(self.settings.github_token)

        # ---- Window setup ----
        self.title("Project Git-ULFA")
        self.geometry(f"{self._WIDTH}x{self._HEIGHT}")
        self.minsize(self._MIN_WIDTH, self._MIN_HEIGHT)
        self.configure(fg_color="#0d1117")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ---- Layout ----
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_sidebar()
        self._build_content()

        # ---- Notification manager (lives on top) ----
        self.notif = NotificationManager(self)

        # ---- Subscribe to engine events ----
        self._subscribe_events()

        # ---- Start background services ----
        self.sync_engine.start()

        # ---- Poll GUI queue ----
        self.after(200, self._poll_gui_queue)

        # ---- Check GitHub connection on startup ----
        self.after(800, self._check_github_on_start)

        # ---- Show dashboard by default ----
        self._show_panel("dashboard")

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _build_header(self) -> None:
        header = ctk.CTkFrame(
            self, height=52, fg_color="#161b22", corner_radius=0
        )
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text="  Project Git-ULFA",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#e6edf3",
        ).grid(row=0, column=0, padx=12, sticky="w")

        # Kill switch status label
        self._kill_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#f85149",
        )
        self._kill_label.grid(row=0, column=1, sticky="e", padx=12)

        # Global sync status
        self._header_status = ctk.CTkLabel(
            header,
            text="●  Ready",
            font=ctk.CTkFont(size=12),
            text_color="#2ea043",
        )
        self._header_status.grid(row=0, column=2, padx=12, sticky="e")

    # ------------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------------

    def _build_sidebar(self) -> None:
        self.sidebar = Sidebar(self, on_navigate=self._handle_nav)
        self.sidebar.grid(row=1, column=0, sticky="nsew")

    # ------------------------------------------------------------------
    # Content area
    # ------------------------------------------------------------------

    def _build_content(self) -> None:
        self._content = ctk.CTkFrame(
            self, fg_color="#0d1117", corner_radius=0
        )
        self._content.grid(row=1, column=1, sticky="nsew")
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

        # Instantiate all panels (hidden by default)
        self.dashboard = DashboardPanel(
            self._content,
            settings=self.settings,
            project_manager=self.project_manager,
            sync_engine=self.sync_engine,
        )
        self.projects_panel = ProjectsPanel(
            self._content,
            settings=self.settings,
            project_manager=self.project_manager,
            sync_engine=self.sync_engine,
        )
        self.logs_panel = LogsPanel(
            self._content,
            settings=self.settings,
            project_manager=self.project_manager,
        )
        self.settings_panel = SettingsPanel(
            self._content,
            settings=self.settings,
            on_settings_saved=self._on_settings_saved,
        )

        self._panels: Dict[str, ctk.CTkFrame] = {
            "dashboard": self.dashboard,
            "projects": self.projects_panel,
            "logs": self.logs_panel,
            "settings": self.settings_panel,
        }
        self._active_panel: str = ""

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _handle_nav(self, page_id: str) -> None:
        if page_id == "__kill_switch__":
            self._toggle_kill_switch()
        else:
            self._show_panel(page_id)

    def _show_panel(self, page_id: str) -> None:
        if page_id == self._active_panel:
            return
        for pid, panel in self._panels.items():
            if pid == page_id:
                panel.grid(row=0, column=0, sticky="nsew")
            else:
                panel.grid_remove()
        self._active_panel = page_id

        # Refresh the newly shown panel
        if page_id == "dashboard":
            self.dashboard.refresh()
        elif page_id == "projects":
            self.projects_panel.refresh()
        elif page_id == "logs":
            self.logs_panel.refresh_projects()

    # ------------------------------------------------------------------
    # Kill switch
    # ------------------------------------------------------------------

    def _toggle_kill_switch(self) -> None:
        if self.sync_engine.kill_switch_active:
            self.sync_engine.deactivate_kill_switch()
            self.sidebar.set_kill_switch_active(False)
            self._kill_label.configure(text="")
        else:
            self.sync_engine.activate_kill_switch()
            self.sidebar.set_kill_switch_active(True)
            self._kill_label.configure(text="⚠  Kill Switch Active  ")

    # ------------------------------------------------------------------
    # Event subscriptions
    # ------------------------------------------------------------------

    def _subscribe_events(self) -> None:
        self.event_bus.subscribe("project_added", self._on_project_added)
        self.event_bus.subscribe("project_removed", self._on_project_removed)

    def _on_project_added(self, project=None) -> None:
        self.after(0, self.projects_panel.refresh)

    def _on_project_removed(self, project=None) -> None:
        self.after(0, self.projects_panel.refresh)

    # ------------------------------------------------------------------
    # GUI queue polling
    # ------------------------------------------------------------------

    def _poll_gui_queue(self) -> None:
        for event_type, data in self.gui_queue.drain():
            self._handle_gui_event(event_type, data)
        self.after(200, self._poll_gui_queue)

    def _handle_gui_event(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == "notification":
            if self.settings.show_notifications:
                self.notif.show(data.get("message", ""), data.get("level", "info"))
            # Also append to dashboard activity
            self.dashboard.add_activity(data.get("message", ""))

        elif event_type in ("sync_completed", "status_changed", "pending_changed"):
            self.dashboard.refresh()
            if self._active_panel == "projects":
                self.projects_panel.refresh()

        elif event_type == "project_linked":
            project = data.get("project")
            self.projects_panel.refresh()
            if project:
                self.notif.show(
                    f"New project linked: {project.project_name}", level="info"
                )

        elif event_type == "kill_switch_changed":
            pass  # handled by sidebar + header already

    # ------------------------------------------------------------------
    # Settings saved callback
    # ------------------------------------------------------------------

    def _on_settings_saved(self) -> None:
        # Re-initialise GitHub API with new token
        self.github_api.update_token(self.settings.github_token)
        self.dashboard.refresh()

    # ------------------------------------------------------------------
    # GitHub connection check
    # ------------------------------------------------------------------

    def _check_github_on_start(self) -> None:
        def _check() -> None:
            api = GitHubAPI(self.settings.github_token)
            ok, result = api.validate_token()
            self.after(0, lambda: self.dashboard.set_github_status(ok, result if ok else ""))

        threading.Thread(target=_check, daemon=True).start()

    # ------------------------------------------------------------------
    # Close
    # ------------------------------------------------------------------

    def _on_close(self) -> None:
        self.sync_engine.stop()
        self.settings.save()
        self.destroy()
