"""
Settings panel for Project Git-ULFA.
"""
import threading
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from config.settings import AppSettings
from core.github_api import GitHubAPI


# ---------------------------------------------------------------------------
# Terminate-repository 3-step dialog
# ---------------------------------------------------------------------------

class TerminateDialog(ctk.CTkToplevel):
    """
    Three-step confirmation dialog for deleting all files in a repository.

    Step 1 — Password
    Step 2 — Yes / No
    Step 3 — Are you sure?
    """

    def __init__(self, master, settings: AppSettings) -> None:
        super().__init__(master)
        self.title("⚠  Terminate Repository")
        self.geometry("480x380")
        self.resizable(False, False)
        self.grab_set()

        self._settings = settings
        self._confirmed = False
        self._chosen_repo = ""
        self._chosen_branch = ""

        self._step = 1
        self._repos: list[str] = []

        self._build()
        threading.Thread(target=self._fetch_repos, daemon=True).start()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # Red warning header
        header = ctk.CTkFrame(self, fg_color="#3d0000", corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="⚠  TERMINATE REPOSITORY",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#f85149",
        ).pack(pady=12)

        # Dynamic content frame
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="both", expand=True, padx=24, pady=16)

        self._show_step1()

    def _clear_content(self) -> None:
        for w in self._content.winfo_children():
            w.destroy()

    # ------------------------------------------------------------------
    # Step 1 — Password
    # ------------------------------------------------------------------

    def _show_step1(self) -> None:
        self._clear_content()
        ctk.CTkLabel(
            self._content,
            text="Step 1 of 3 — Enter Termination Password",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#e6edf3",
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            self._content,
            text="This will permanently delete ALL files in a GitHub repository.\n"
                 "Enter the termination password set in Settings to continue.",
            font=ctk.CTkFont(size=11),
            text_color="#8b949e",
            justify="left",
            anchor="w",
            wraplength=430,
        ).pack(anchor="w", pady=(0, 16))

        ctk.CTkLabel(self._content, text="Password:", anchor="w",
                     text_color="#c9d1d9").pack(fill="x", pady=(0, 4))
        self._pw_entry = ctk.CTkEntry(self._content, show="*", height=34)
        self._pw_entry.pack(fill="x", pady=(0, 4))
        self._pw_entry.bind("<Return>", lambda _: self._verify_password())

        self._pw_error = ctk.CTkLabel(
            self._content, text="", text_color="#f85149",
            font=ctk.CTkFont(size=11), anchor="w"
        )
        self._pw_error.pack(fill="x")

        btn_row = ctk.CTkFrame(self._content, fg_color="transparent")
        btn_row.pack(fill="x", pady=(16, 0))
        ctk.CTkButton(
            btn_row, text="Cancel", width=100,
            fg_color="#21262d", hover_color="#30363d",
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            btn_row, text="Next →", width=100,
            fg_color="#b62324", hover_color="#f85149",
            command=self._verify_password,
        ).pack(side="right")

    def _verify_password(self) -> None:
        entered = self._pw_entry.get()
        stored = self._settings.get("termination_password", "")
        if not stored:
            self._pw_error.configure(
                text="No termination password set. Set one in the Danger Zone section first."
            )
            return
        if entered != stored:
            self._pw_error.configure(text="Incorrect password.")
            return
        self._show_step2()

    # ------------------------------------------------------------------
    # Step 2 — Choose repo + Yes / No
    # ------------------------------------------------------------------

    def _fetch_repos(self) -> None:
        token = self._settings.github_token
        if not token:
            return
        try:
            api = GitHubAPI(token)
            repos = api.list_repositories()
            self.after(0, self._set_repos, repos)
        except Exception:
            pass

    def _set_repos(self, repos: list[str]) -> None:
        self._repos = repos
        if hasattr(self, "_repo_dropdown") and self._repo_dropdown.winfo_exists():
            values = repos if repos else ["(no repositories found)"]
            self._repo_dropdown.configure(values=values)
            if repos:
                self._repo_dropdown.set(repos[0])

    def _show_step2(self) -> None:
        self._clear_content()
        ctk.CTkLabel(
            self._content,
            text="Step 2 of 3 — Choose Repository",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#e6edf3",
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            self._content,
            text="Select the repository whose files will be permanently deleted.",
            font=ctk.CTkFont(size=11),
            text_color="#8b949e",
            anchor="w",
            wraplength=430,
        ).pack(anchor="w", pady=(0, 12))

        ctk.CTkLabel(self._content, text="Repository:", anchor="w",
                     text_color="#c9d1d9").pack(fill="x", pady=(0, 4))
        initial = self._repos[0] if self._repos else "⟳  Loading…"
        self._repo_dropdown = ctk.CTkOptionMenu(
            self._content,
            values=[initial] if not self._repos else self._repos,
            dynamic_resizing=False,
            width=430,
        )
        self._repo_dropdown.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(self._content, text="Branch:", anchor="w",
                     text_color="#c9d1d9").pack(fill="x", pady=(0, 4))
        self._branch_entry2 = ctk.CTkEntry(self._content, height=34,
                                           placeholder_text="main")
        self._branch_entry2.insert(0, "main")
        self._branch_entry2.pack(fill="x", pady=(0, 16))

        btn_row = ctk.CTkFrame(self._content, fg_color="transparent")
        btn_row.pack(fill="x")
        ctk.CTkButton(
            btn_row, text="Cancel", width=100,
            fg_color="#21262d", hover_color="#30363d",
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            btn_row, text="Yes, continue →", width=130,
            fg_color="#b62324", hover_color="#f85149",
            command=self._confirm_step2,
        ).pack(side="right")

    def _confirm_step2(self) -> None:
        repo = self._repo_dropdown.get().strip()
        branch = self._branch_entry2.get().strip() or "main"
        if not repo or repo.startswith("⟳"):
            return
        self._chosen_repo = repo
        self._chosen_branch = branch
        self._show_step3()

    # ------------------------------------------------------------------
    # Step 3 — Final "are you sure?"
    # ------------------------------------------------------------------

    def _show_step3(self) -> None:
        self._clear_content()
        ctk.CTkLabel(
            self._content,
            text="Step 3 of 3 — Final Confirmation",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f85149",
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            self._content,
            text=f"You are about to DELETE EVERY FILE in:\n\n"
                 f"    {self._chosen_repo}  (branch: {self._chosen_branch})\n\n"
                 f"This CANNOT be undone.\n"
                 f"Are you absolutely sure?",
            font=ctk.CTkFont(size=12),
            text_color="#e6edf3",
            justify="left",
            anchor="w",
            wraplength=430,
        ).pack(anchor="w", pady=(0, 20))

        btn_row = ctk.CTkFrame(self._content, fg_color="transparent")
        btn_row.pack(fill="x")
        ctk.CTkButton(
            btn_row, text="Cancel — keep my files", width=180,
            fg_color="#238636", hover_color="#2ea043",
            command=self.destroy,
        ).pack(side="left")
        ctk.CTkButton(
            btn_row, text="DELETE EVERYTHING", width=160,
            fg_color="#b62324", hover_color="#f85149",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._execute,
        ).pack(side="right")

    # ------------------------------------------------------------------
    # Execute deletion with progress
    # ------------------------------------------------------------------

    def _execute(self) -> None:
        self._clear_content()
        ctk.CTkLabel(
            self._content,
            text="Deleting files…",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f85149",
        ).pack(anchor="w", pady=(0, 8))

        self._progress_bar = ctk.CTkProgressBar(self._content)
        self._progress_bar.set(0)
        self._progress_bar.pack(fill="x", pady=(0, 8))

        self._progress_label = ctk.CTkLabel(
            self._content, text="Preparing…",
            font=ctk.CTkFont(size=11), text_color="#8b949e", anchor="w"
        )
        self._progress_label.pack(fill="x")

        threading.Thread(target=self._run_deletion, daemon=True).start()

    def _run_deletion(self) -> None:
        api = GitHubAPI(self._settings.github_token)

        def on_progress(current, total, path):
            fraction = current / total
            short_path = path if len(path) < 50 else "…" + path[-48:]
            self.after(0, self._update_progress, fraction,
                       f"({current}/{total})  {short_path}")

        ok, err = api.delete_all_repo_files(
            self._chosen_repo,
            self._chosen_branch,
            progress_callback=on_progress,
        )
        self.after(0, self._deletion_done, ok, err)

    def _update_progress(self, fraction: float, label: str) -> None:
        if self._progress_bar.winfo_exists():
            self._progress_bar.set(fraction)
        if self._progress_label.winfo_exists():
            self._progress_label.configure(text=label)

    def _deletion_done(self, ok: bool, err: str) -> None:
        if ok:
            messagebox.showinfo(
                "Terminated",
                f"All files in '{self._chosen_repo}' have been deleted.",
                parent=self,
            )
        else:
            messagebox.showerror(
                "Deletion Failed",
                f"An error occurred:\n{err}",
                parent=self,
            )
        self.destroy()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    @property
    def confirmed(self) -> bool:
        return self._confirmed


# ---------------------------------------------------------------------------
# Settings panel
# ---------------------------------------------------------------------------

class SettingsPanel(ctk.CTkFrame):
    """Application settings form."""

    def __init__(
        self,
        master,
        settings: AppSettings,
        on_settings_saved=None,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._settings = settings
        self._on_saved = on_settings_saved
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e6edf3",
            anchor="w",
        ).pack(fill="x", padx=24, pady=(20, 4))

        scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent", scrollbar_button_color="#30363d"
        )
        scroll.pack(fill="both", expand=True, padx=24, pady=(8, 0))

        # ---- GitHub section -------------------------------------------
        self._section(scroll, "GitHub Authentication")

        ctk.CTkLabel(scroll, text="Personal Access Token:", anchor="w",
                     text_color="#c9d1d9").pack(fill="x", pady=(0, 2))

        token_entry_row = ctk.CTkFrame(scroll, fg_color="transparent")
        token_entry_row.pack(fill="x", pady=(0, 6))

        self._token_entry = ctk.CTkEntry(
            token_entry_row, placeholder_text="ghp_xxxxxxxxxxxxxxxxxxxx", show="*", height=34
        )
        if self._settings.github_token:
            self._token_entry.insert(0, self._settings.github_token)
        self._token_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self._token_visible = False
        self._show_token_btn = ctk.CTkButton(
            token_entry_row,
            text="👁",
            width=36,
            height=34,
            font=ctk.CTkFont(size=15),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            command=self._toggle_token_visibility,
        )
        self._show_token_btn.pack(side="left")

        token_row = ctk.CTkFrame(scroll, fg_color="transparent")
        token_row.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(
            token_row,
            text="Validate Token",
            width=130,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            command=self._validate_token,
        ).pack(side="left")

        self._token_status = ctk.CTkLabel(
            token_row,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#8b949e",
        )
        self._token_status.pack(side="left", padx=12)

        # ---- Sync section ---------------------------------------------
        self._section(scroll, "Synchronisation")

        ctk.CTkLabel(scroll, text="Default sync interval (seconds):", anchor="w",
                     text_color="#c9d1d9").pack(fill="x", pady=(0, 2))
        self._interval_entry = ctk.CTkEntry(
            scroll, placeholder_text="300", height=34
        )
        self._interval_entry.insert(0, str(self._settings.sync_interval))
        self._interval_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(scroll, text="Max changes before auto-push:", anchor="w",
                     text_color="#c9d1d9").pack(fill="x", pady=(0, 2))
        self._max_changes_entry = ctk.CTkEntry(
            scroll, placeholder_text="10", height=34
        )
        self._max_changes_entry.insert(
            0, str(self._settings.max_changes_before_push)
        )
        self._max_changes_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(scroll, text="Commit message template:", anchor="w",
                     text_color="#c9d1d9").pack(fill="x", pady=(0, 2))

        ctk.CTkLabel(
            scroll,
            text="Variables: {change_summary}  {timestamp}  {project_name}",
            font=ctk.CTkFont(size=10),
            text_color="#8b949e",
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self._template_entry = ctk.CTkEntry(scroll, height=34)
        self._template_entry.insert(0, self._settings.commit_template)
        self._template_entry.pack(fill="x", pady=(0, 10))

        # Pull before push toggle
        self._pull_switch = ctk.CTkSwitch(
            scroll,
            text="Pull before push (reduces conflicts)",
            font=ctk.CTkFont(size=12),
        )
        if self._settings.pull_before_push:
            self._pull_switch.select()
        self._pull_switch.pack(anchor="w", pady=(0, 10))

        # ---- Ignore patterns section ----------------------------------
        self._section(scroll, "Default Ignore Patterns")

        ctk.CTkLabel(
            scroll,
            text="One pattern per line. Applies to all new projects.",
            font=ctk.CTkFont(size=11),
            text_color="#8b949e",
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self._ignore_box = ctk.CTkTextbox(
            scroll,
            height=140,
            fg_color="#0d1117",
            text_color="#c9d1d9",
            font=ctk.CTkFont(family="Consolas", size=11),
        )
        self._ignore_box.insert(
            "1.0", "\n".join(self._settings.default_ignore_patterns)
        )
        self._ignore_box.pack(fill="x", pady=(0, 12))

        # ---- Notifications --------------------------------------------
        self._section(scroll, "Notifications")

        self._notif_switch = ctk.CTkSwitch(
            scroll,
            text="Show desktop notifications",
            font=ctk.CTkFont(size=12),
        )
        if self._settings.show_notifications:
            self._notif_switch.select()
        self._notif_switch.pack(anchor="w", pady=(0, 16))

        # ---- Save button ----------------------------------------------
        ctk.CTkButton(
            scroll,
            text="Save Settings",
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#238636",
            hover_color="#2ea043",
            command=self._save,
        ).pack(fill="x", pady=(0, 16))

        # ---- Danger Zone ---------------------------------------------
        self._section(scroll, "⚠  Danger Zone")

        ctk.CTkLabel(
            scroll,
            text="Termination Password",
            font=ctk.CTkFont(size=12),
            text_color="#c9d1d9",
            anchor="w",
        ).pack(fill="x", pady=(0, 2))
        ctk.CTkLabel(
            scroll,
            text="Required to use the Terminate Repository function. Set a strong password.",
            font=ctk.CTkFont(size=10),
            text_color="#8b949e",
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        term_row = ctk.CTkFrame(scroll, fg_color="transparent")
        term_row.pack(fill="x", pady=(0, 12))

        self._term_pw_entry = ctk.CTkEntry(
            term_row,
            placeholder_text="Set termination password…",
            show="*",
            height=34,
        )
        if self._settings.get("termination_password"):
            self._term_pw_entry.insert(0, self._settings.get("termination_password"))
        self._term_pw_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self._term_pw_visible = False
        self._term_pw_btn = ctk.CTkButton(
            term_row,
            text="👁",
            width=36,
            height=34,
            font=ctk.CTkFont(size=15),
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            command=self._toggle_term_pw_visibility,
        )
        self._term_pw_btn.pack(side="left")

        ctk.CTkButton(
            scroll,
            text="🗑  Terminate Repository…",
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#3d0000",
            hover_color="#b62324",
            text_color="#f85149",
            border_width=1,
            border_color="#f85149",
            command=self._open_terminate_dialog,
        ).pack(fill="x", pady=(0, 24))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _toggle_token_visibility(self) -> None:
        self._token_visible = not self._token_visible
        self._token_entry.configure(show="" if self._token_visible else "*")
        self._show_token_btn.configure(text="🔒" if self._token_visible else "👁")

    def _toggle_term_pw_visibility(self) -> None:
        self._term_pw_visible = not self._term_pw_visible
        self._term_pw_entry.configure(show="" if self._term_pw_visible else "*")
        self._term_pw_btn.configure(text="🔒" if self._term_pw_visible else "👁")

    def _open_terminate_dialog(self) -> None:
        if not self._settings.get("termination_password"):
            messagebox.showwarning(
                "No Termination Password",
                "Please set a Termination Password in the Danger Zone section "
                "and click Save Settings before using this function.",
                parent=self,
            )
            return
        dlg = TerminateDialog(self, self._settings)
        self.wait_window(dlg)

    def _validate_token(self) -> None:
        token = self._token_entry.get().strip()
        if not token:
            self._token_status.configure(text="Enter a token first.", text_color="#FFA500")
            return
        api = GitHubAPI(token)
        ok, result = api.validate_token()
        if ok:
            self._token_status.configure(
                text=f"✓ Connected as {result}", text_color="#2ea043"
            )
            self._settings.github_username = result
        else:
            self._token_status.configure(
                text=f"✕ {result}", text_color="#f85149"
            )

    def _save(self) -> None:
        token = self._token_entry.get().strip()
        self._settings.github_token = token

        try:
            interval = int(self._interval_entry.get().strip())
        except ValueError:
            interval = 300
        self._settings.set("sync_interval", interval)

        try:
            max_ch = int(self._max_changes_entry.get().strip())
        except ValueError:
            max_ch = 10
        self._settings.set("max_changes_before_push", max_ch)

        template = self._template_entry.get().strip()
        if template:
            self._settings.set("commit_template", template)

        self._settings.set("pull_before_push", self._pull_switch.get() == 1)

        patterns = [
            line.strip()
            for line in self._ignore_box.get("1.0", "end").splitlines()
            if line.strip()
        ]
        self._settings.set("default_ignore_patterns", patterns)
        self._settings.set("show_notifications", self._notif_switch.get() == 1)

        term_pw = self._term_pw_entry.get()
        if term_pw:
            self._settings.set("termination_password", term_pw)

        self._settings.save()

        if self._on_saved:
            self._on_saved()

        messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _section(self, parent, title: str) -> None:
        ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#8b949e",
            anchor="w",
        ).pack(fill="x", pady=(12, 4))
        ctk.CTkFrame(parent, height=1, fg_color="#30363d").pack(
            fill="x", pady=(0, 10)
        )
