"""
Logs panel for Project Git-ULFA.

Displays per-project sync logs with a date selector.
"""
from pathlib import Path
from typing import Dict, List

import customtkinter as ctk

from config.settings import AppSettings
from models.project import ProjectModel
from utils.logger import ProjectLogger


class LogsPanel(ctk.CTkFrame):
    """View synchronisation logs per project and per date."""

    def __init__(
        self,
        master,
        settings: AppSettings,
        project_manager,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._settings = settings
        self._pm = project_manager
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        ctk.CTkLabel(
            self,
            text="Logs",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e6edf3",
            anchor="w",
        ).pack(fill="x", padx=24, pady=(20, 4))

        # Controls row
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=24, pady=(8, 12))

        ctk.CTkLabel(
            controls, text="Project:", font=ctk.CTkFont(size=12), text_color="#c9d1d9"
        ).pack(side="left", padx=(0, 6))

        self._project_menu = ctk.CTkOptionMenu(
            controls,
            values=["— Select project —"],
            width=220,
            command=self._on_project_selected,
        )
        self._project_menu.pack(side="left")

        ctk.CTkLabel(
            controls, text="Date:", font=ctk.CTkFont(size=12), text_color="#c9d1d9"
        ).pack(side="left", padx=(16, 6))

        self._date_menu = ctk.CTkOptionMenu(
            controls,
            values=["—"],
            width=140,
            command=self._on_date_selected,
        )
        self._date_menu.pack(side="left")

        ctk.CTkButton(
            controls,
            text="Refresh",
            width=90,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            command=self._load_log,
        ).pack(side="left", padx=(12, 0))

        ctk.CTkButton(
            controls,
            text="Clear View",
            width=90,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            command=self._clear,
        ).pack(side="left", padx=(6, 0))

        # Log display
        self._log_box = ctk.CTkTextbox(
            self,
            fg_color="#0d1117",
            text_color="#c9d1d9",
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled",
            wrap="none",
        )
        self._log_box.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Populate project list
        self.refresh_projects()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def refresh_projects(self) -> None:
        projects = self._pm.get_all()
        names = [p.project_name for p in projects]
        self._projects_by_name: Dict[str, ProjectModel] = {
            p.project_name: p for p in projects
        }
        if names:
            self._project_menu.configure(values=names)
            self._project_menu.set(names[0])
            self._on_project_selected(names[0])
        else:
            self._project_menu.configure(values=["— No projects —"])

    def append_log(self, message: str) -> None:
        """Append a line to the live log view."""
        self._log_box.configure(state="normal")
        self._log_box.insert("end", message + "\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_project_selected(self, name: str) -> None:
        project = self._projects_by_name.get(name)
        if project is None:
            return
        logs_dir = self._settings.project_data_dir(project.project_id) / "logs"
        logger = ProjectLogger(project.project_id, project.project_name, logs_dir)
        dates = logger.list_log_dates()
        if dates:
            self._date_menu.configure(values=dates)
            self._date_menu.set(dates[0])
        else:
            self._date_menu.configure(values=["No logs"])
            self._date_menu.set("No logs")
        self._load_log()

    def _on_date_selected(self, _date: str) -> None:
        self._load_log()

    def _load_log(self) -> None:
        project_name = self._project_menu.get()
        project = self._projects_by_name.get(project_name)
        if project is None:
            return
        selected_date = self._date_menu.get()
        if selected_date in ("No logs", "—"):
            self._show_text("No log entries found for this project.")
            return
        logs_dir = self._settings.project_data_dir(project.project_id) / "logs"
        logger = ProjectLogger(project.project_id, project.project_name, logs_dir)
        content = logger.read_log_for_date(selected_date)
        self._show_text(content or "(Log file is empty)")

    def _show_text(self, text: str) -> None:
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.insert("1.0", text)
        self._log_box.configure(state="disabled")

    def _clear(self) -> None:
        self._show_text("")
