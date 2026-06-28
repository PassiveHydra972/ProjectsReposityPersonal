"""
Projects panel for Project Git-ULFA.

Lists all linked projects as cards in a scrollable area.  Provides
a toolbar to add new projects, search/filter, and link via the queue.
"""
import os
import threading
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog
from typing import Dict, Optional

import customtkinter as ctk

from config.settings import AppSettings
from core.github_api import GitHubAPI
from gui.components.project_card import ProjectCard
from models.project import ProjectModel
from utils.helpers import now_iso

import uuid


class ProjectSetupDialog(ctk.CTkToplevel):
    """Modal dialog for configuring a newly linked project."""

    _PLACEHOLDER_LOADING = "⟳  Loading repositories…"
    _PLACEHOLDER_NO_TOKEN = "⚠  No token — enter manually below"
    _PLACEHOLDER_FAILED = "⚠  Could not fetch — enter manually below"
    _PLACEHOLDER_MANUAL = "— Enter manually below —"

    def __init__(self, master, project: ProjectModel, settings: AppSettings,
                 existing_projects=None) -> None:
        super().__init__(master)
        self.title("Configure Project")
        self.geometry("520x720")
        self.resizable(False, False)
        self.grab_set()

        self._project = project
        self._settings = settings
        self._result: Optional[ProjectModel] = None
        self._repos: list[str] = []
        # List of already-configured projects (used for shared-repo warning)
        self._existing_projects: list = list(existing_projects or [])

        self._build()
        # Fetch repos in background so the dialog opens instantly
        threading.Thread(target=self._fetch_repos, daemon=True).start()

    def _build(self) -> None:
        ctk.CTkLabel(
            self,
            text="Configure GitHub Repository",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e6edf3",
        ).pack(padx=20, pady=(20, 4), anchor="w")

        ctk.CTkLabel(
            self,
            text=f"Project: {self._project.project_name}",
            font=ctk.CTkFont(size=12),
            text_color="#8b949e",
        ).pack(padx=20, pady=(0, 16), anchor="w")

        # Project name
        ctk.CTkLabel(self, text="Project Name:", anchor="w").pack(
            fill="x", padx=20, pady=(0, 2)
        )
        self._name_entry = ctk.CTkEntry(self, placeholder_text="My Project")
        self._name_entry.insert(0, self._project.project_name)
        self._name_entry.pack(fill="x", padx=20, pady=(0, 12))

        # ── Repository picker ──────────────────────────────────────────
        repo_label_row = ctk.CTkFrame(self, fg_color="transparent")
        repo_label_row.pack(fill="x", padx=20, pady=(0, 2))

        ctk.CTkLabel(
            repo_label_row,
            text="GitHub Repository:",
            anchor="w",
            text_color="#c9d1d9",
        ).pack(side="left")

        self._refresh_btn = ctk.CTkButton(
            repo_label_row,
            text="↻ Refresh",
            width=80,
            height=22,
            font=ctk.CTkFont(size=11),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            command=lambda: threading.Thread(
                target=self._fetch_repos, daemon=True
            ).start(),
        )
        self._refresh_btn.pack(side="right")

        # Dropdown of existing repos
        initial_dropdown = (
            self._PLACEHOLDER_LOADING
            if self._settings.github_token
            else self._PLACEHOLDER_NO_TOKEN
        )
        self._repo_dropdown = ctk.CTkOptionMenu(
            self,
            values=[initial_dropdown],
            command=self._on_repo_selected,
            dynamic_resizing=False,
            width=480,
        )
        self._repo_dropdown.pack(fill="x", padx=20, pady=(0, 6))

        # Manual entry (pre-filled if project already has a repo set)
        ctk.CTkLabel(
            self,
            text="Or type manually (owner/repo):",
            font=ctk.CTkFont(size=11),
            text_color="#8b949e",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 2))

        self._repo_entry = ctk.CTkEntry(
            self, placeholder_text="username/repository-name", height=34
        )
        if self._project.github_repository:
            self._repo_entry.insert(0, self._project.github_repository)
        self._repo_entry.pack(fill="x", padx=20, pady=(0, 12))

        # ── Branch ────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Branch:", anchor="w", text_color="#c9d1d9").pack(
            fill="x", padx=20, pady=(0, 2)
        )
        self._branch_entry = ctk.CTkEntry(self, placeholder_text="main", height=34)
        self._branch_entry.insert(0, self._project.branch or "main")
        self._branch_entry.pack(fill="x", padx=20, pady=(0, 12))

        # ── Subfolder picker ───────────────────────────────────────────
        subfolder_label_row = ctk.CTkFrame(self, fg_color="transparent")
        subfolder_label_row.pack(fill="x", padx=20, pady=(0, 2))

        ctk.CTkLabel(
            subfolder_label_row,
            text="Repository Subfolder:",
            anchor="w",
            text_color="#c9d1d9",
        ).pack(side="left")

        # Hint row
        ctk.CTkLabel(
            self,
            text="📁  Files will be stored inside this folder in the repository.\n"
                 "    Leave blank to use the project name as the folder automatically.",
            font=ctk.CTkFont(size=10),
            text_color="#8b949e",
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 6))

        self._subfolder_dropdown = ctk.CTkOptionMenu(
            self,
            values=["— Root of repository (this project owns the whole repo) —"],
            command=self._on_subfolder_selected,
            dynamic_resizing=False,
            width=480,
        )
        self._subfolder_dropdown.pack(fill="x", padx=20, pady=(0, 4))

        ctk.CTkLabel(
            self,
            text="Subfolder path (e.g. Project Decom  or  archive/old-projects):",
            font=ctk.CTkFont(size=11),
            text_color="#8b949e",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 2))

        self._subfolder_entry = ctk.CTkEntry(
            self,
            placeholder_text="Project folder name in the repository",
            height=34,
        )
        # Default to the project name so files land in their own folder
        default_subfolder = self._project.repo_subfolder or self._project.project_name
        self._subfolder_entry.insert(0, default_subfolder)
        self._subfolder_entry.pack(fill="x", padx=20, pady=(0, 12))

        # ── Sync toggle ────────────────────────────────────────────────
        self._sync_switch = ctk.CTkSwitch(
            self,
            text="Enable sync immediately",
            font=ctk.CTkFont(size=12),
        )
        self._sync_switch.pack(padx=20, pady=(0, 20), anchor="w")

        # ── Buttons ───────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 20), side="bottom")

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            width=100,
            fg_color="#21262d",
            hover_color="#30363d",
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_row,
            text="Save",
            width=100,
            fg_color="#238636",
            hover_color="#2ea043",
            command=self._save,
        ).pack(side="right")

    # ------------------------------------------------------------------
    # Repository fetching
    # ------------------------------------------------------------------

    def _fetch_repos(self) -> None:
        """Background thread: fetch repos and update the dropdown."""
        token = self._settings.github_token
        if not token:
            self.after(0, self._set_dropdown_values, [], self._PLACEHOLDER_NO_TOKEN)
            return

        self.after(0, self._set_dropdown_values, [], self._PLACEHOLDER_LOADING)
        try:
            api = GitHubAPI(token)
            repos = api.list_repositories()
        except Exception:
            repos = []

        if repos:
            self.after(0, self._set_dropdown_values, repos, self._PLACEHOLDER_MANUAL)
        else:
            self.after(0, self._set_dropdown_values, [], self._PLACEHOLDER_FAILED)

    def _set_dropdown_values(self, repos: list[str], placeholder: str) -> None:
        """Called on the main thread to update the dropdown."""
        self._repos = repos
        values = [placeholder] + repos if repos else [placeholder]
        self._repo_dropdown.configure(values=values)
        self._repo_dropdown.set(placeholder)

        # If the project already has a repo set and it's in the list, select it
        if self._project.github_repository in repos:
            self._repo_dropdown.set(self._project.github_repository)

    def _on_repo_selected(self, value: str) -> None:
        """When a repo is picked from the dropdown, populate the text entry."""
        if value.startswith("⟳") or value.startswith("⚠") or value.startswith("—"):
            return
        # Fill both the entry and auto-fill the branch
        self._repo_entry.delete(0, "end")
        self._repo_entry.insert(0, value)

        # Reset subfolder list while we fetch
        self._subfolder_dropdown.configure(values=["⟳  Loading folders…"])
        self._subfolder_dropdown.set("⟳  Loading folders…")

        # Try to auto-fill the default branch and load folders in the background
        threading.Thread(
            target=self._fetch_default_branch, args=(value,), daemon=True
        ).start()
        threading.Thread(
            target=self._fetch_subfolders, args=(value,), daemon=True
        ).start()

    def _fetch_default_branch(self, full_name: str) -> None:
        """Background thread: look up the repo's default branch."""
        try:
            api = GitHubAPI(self._settings.github_token)
            branch = api.get_default_branch(full_name)
            self.after(0, self._set_branch, branch)
        except Exception:
            pass

    def _set_branch(self, branch: str) -> None:
        self._branch_entry.delete(0, "end")
        self._branch_entry.insert(0, branch)

    def _fetch_subfolders(self, full_name: str) -> None:
        """Background thread: list directories inside the chosen repo."""
        try:
            api = GitHubAPI(self._settings.github_token)
            branch = self._branch_entry.get().strip() or "main"
            folders = api.list_repo_folders(full_name, branch)
        except Exception:
            folders = []
        self.after(0, self._set_subfolder_values, folders)

    def _set_subfolder_values(self, folders: list[str]) -> None:
        root_label = "— Root of repository —"
        values = [root_label] + folders if folders else [root_label, "(no sub-folders found)"]
        self._subfolder_dropdown.configure(values=values)
        # Re-select the project's current subfolder if it is in the list
        current = self._project.repo_subfolder
        if current and current in folders:
            self._subfolder_dropdown.set(current)
        else:
            self._subfolder_dropdown.set(root_label)

    def _on_subfolder_selected(self, value: str) -> None:
        """Populate the manual entry when a folder is chosen from the dropdown."""
        if value.startswith("—") or value.startswith("("):
            # 'Root of repository' or placeholder — clear the entry
            self._subfolder_entry.delete(0, "end")
            return
        self._subfolder_entry.delete(0, "end")
        self._subfolder_entry.insert(0, value)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save(self) -> None:
        name = self._name_entry.get().strip()
        # Prefer the manual entry; fall back to whatever the dropdown shows
        repo = self._repo_entry.get().strip()
        if not repo:
            selected = self._repo_dropdown.get()
            if not (
                selected.startswith("⟳")
                or selected.startswith("⚠")
                or selected.startswith("—")
            ):
                repo = selected
        branch = self._branch_entry.get().strip() or "main"

        if not name:
            messagebox.showerror("Error", "Project name is required.", parent=self)
            return

        self._project.project_name = name
        self._project.github_repository = repo
        self._project.branch = branch
        # Always use a subfolder — if the user left it blank, default to the
        # project name so files never land at the repository root.
        subfolder = self._subfolder_entry.get().strip().strip("/")
        if not subfolder:
            subfolder = name
        self._project.repo_subfolder = subfolder
        self._project.sync_enabled = self._sync_switch.get() == 1

        # Warn if this project shares a repo with another project but has no subfolder
        # (kept as a safety net in case the name is manually cleared to ".")
        if repo and not self._project.repo_subfolder:
            others = [
                p for p in self._existing_projects
                if p.github_repository == repo
                and p.project_id != self._project.project_id
            ]
            if others:
                other_names = ", ".join(p.project_name for p in others[:3])
                confirm = messagebox.askyesno(
                    "Shared Repository — Subfolder Recommended",
                    f"The repository '{repo}' is already used by:\n  {other_names}\n\n"
                    f"Without a subfolder, this project's files will be placed at the "
                    f"ROOT of the repository and may overwrite other projects' files.\n\n"
                    f"It is strongly recommended to set a Subfolder (e.g. '{name}').\n\n"
                    f"Continue without a subfolder anyway?",
                    parent=self,
                )
                if not confirm:
                    return
        if self._project.sync_enabled:
            self._project.status = "active"
        else:
            self._project.status = "paused"
        self._result = self._project
        self.destroy()

    @property
    def result(self) -> Optional[ProjectModel]:
        return self._result


# ---------------------------------------------------------------------------
# Projects panel
# ---------------------------------------------------------------------------

class ProjectsPanel(ctk.CTkFrame):
    """Panel that lists and manages all linked projects."""

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
        self._cards: Dict[str, ProjectCard] = {}
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self.refresh())

        self._build()
        self.refresh()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            header,
            text="Projects",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e6edf3",
        ).pack(side="left")

        # Add project button
        ctk.CTkButton(
            header,
            text="＋  Add Project",
            width=130,
            height=34,
            font=ctk.CTkFont(size=12),
            fg_color="#238636",
            hover_color="#2ea043",
            command=self._add_project,
        ).pack(side="right")

        # Search bar
        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.pack(fill="x", padx=24, pady=(8, 12))

        ctk.CTkEntry(
            search_row,
            textvariable=self._search_var,
            placeholder_text="🔍  Search projects…",
            height=34,
        ).pack(fill="x")

        # Scrollable project list
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#30363d",
        )
        self._scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Empty state label
        self._empty_label = ctk.CTkLabel(
            self._scroll,
            text="No projects linked yet.\nClick  ＋ Add Project  to get started.",
            font=ctk.CTkFont(size=13),
            text_color="#8b949e",
            justify="center",
        )

    # ------------------------------------------------------------------
    # Public refresh
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        query = self._search_var.get().lower().strip()
        projects = self._pm.get_all()
        filtered = [
            p for p in projects
            if not query
            or query in p.project_name.lower()
            or query in p.local_path.lower()
            or query in p.github_repository.lower()
        ]

        existing_ids = set(self._cards.keys())
        current_ids = {p.project_id for p in filtered}

        # Remove cards no longer needed
        for pid in existing_ids - current_ids:
            card = self._cards.pop(pid)
            card.destroy()

        # Add or update cards
        for project in filtered:
            if project.project_id in self._cards:
                self._cards[project.project_id].update_project(project)
            else:
                card = ProjectCard(
                    self._scroll,
                    project=project,
                    on_sync_now=self._on_sync_now,
                    on_toggle_sync=self._on_toggle_sync,
                    on_open_folder=self._on_open_folder,
                    on_open_repo=self._on_open_repo,
                    on_configure=self._on_configure,
                    on_remove=self._on_remove,
                )
                card.pack(fill="x", pady=(0, 10))
                self._cards[project.project_id] = card

        # Show / hide empty state
        if filtered:
            self._empty_label.pack_forget()
        else:
            self._empty_label.pack(pady=40)

    # ------------------------------------------------------------------
    # Add project
    # ------------------------------------------------------------------

    def _add_project(self) -> None:
        folder = filedialog.askdirectory(
            title="Select Folder to Link with Git-ULFA",
            mustexist=True,
        )
        if not folder:
            return

        # Check if already linked
        for p in self._pm.get_all():
            if Path(p.local_path).resolve() == Path(folder).resolve():
                messagebox.showinfo(
                    "Already Linked",
                    f"This folder is already linked as '{p.project_name}'.",
                )
                return

        # Create a provisional project
        project = ProjectModel(
            project_name=Path(folder).name,
            project_id=str(uuid.uuid4()),
            local_path=str(Path(folder).resolve()),
            date_linked=now_iso(),
            status="pending_setup",
        )

        # Open setup dialog
        self.after(10, lambda: self._open_setup_dialog(project))

    def _open_setup_dialog(self, project: ProjectModel, is_new: bool = True) -> None:
        existing = self._pm.get_all()
        dlg = ProjectSetupDialog(self, project, self._settings, existing_projects=existing)
        self.wait_window(dlg)
        result = dlg.result
        if result:
            if is_new:
                self._pm.add_project(result)
                self._se.add_project_monitor(result)
            else:
                self._pm.update_project(result)
                self._se.add_project_monitor(result)
            self.refresh()

    # ------------------------------------------------------------------
    # Card callbacks
    # ------------------------------------------------------------------

    def _on_sync_now(self, project_id: str) -> None:
        self._se.sync_now(project_id)

    def _on_toggle_sync(self, project_id: str, enabled: bool) -> None:
        self._pm.set_sync_enabled(project_id, enabled)
        if enabled:
            self._se.add_project_monitor(self._pm.get_project(project_id))
        self.refresh()

    def _on_open_folder(self, project_id: str) -> None:
        p = self._pm.get_project(project_id)
        if p and os.path.isdir(p.local_path):
            os.startfile(p.local_path)

    def _on_open_repo(self, project_id: str) -> None:
        p = self._pm.get_project(project_id)
        if p and p.github_repository:
            webbrowser.open(f"https://github.com/{p.github_repository}")

    def _on_configure(self, project_id: str) -> None:
        p = self._pm.get_project(project_id)
        if not p:
            return
        self.after(10, lambda: self._open_setup_dialog(p, is_new=False))

    def _on_remove(self, project_id: str) -> None:
        p = self._pm.get_project(project_id)
        if p is None:
            return
        confirm = messagebox.askyesno(
            "Remove Project",
            f"Remove '{p.project_name}' from Git-ULFA?\n\n"
            "The local folder will NOT be deleted.",
            parent=self,
        )
        if confirm:
            self._se.remove_project_monitor(project_id)
            self._pm.remove_project(project_id)
            self.refresh()
