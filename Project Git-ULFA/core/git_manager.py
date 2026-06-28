"""
Git operations manager for Project Git-ULFA.

Wraps GitPython to provide per-project git init, stage, commit, push, and pull.
Authentication uses a token-embedded HTTPS remote URL which keeps credentials
out of the commit history (they remain only in .git/config which is never pushed).

Subfolder support
-----------------
When ``project.repo_subfolder`` is non-empty the project's local files are NOT
committed from the local directory itself.  Instead, Git-ULFA maintains a
**staging clone** of the repository (stored in ~/.git-ulfa/clones/<project_id>/)
and mirrors only the relevant files into the configured subfolder there before
committing and pushing.  This means multiple projects can share one repository,
each occupying a different subfolder.

When ``repo_subfolder`` is empty (default) the local directory itself is used as
the git working tree — identical to the original behaviour.
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple

try:
    import os as _os
    _os.environ.setdefault("GIT_PYTHON_REFRESH", "quiet")
    import git
    from git import GitCommandError, InvalidGitRepositoryError, Repo
    # Verify the git executable is actually reachable
    git.Git().version()
    _GITPYTHON_AVAILABLE = True
    _GITPYTHON_ERROR = ""
except ImportError:
    _GITPYTHON_AVAILABLE = False
    _GITPYTHON_ERROR = "GitPython is not installed. Run: pip install gitpython"
except Exception as _e:
    _GITPYTHON_AVAILABLE = False
    _GITPYTHON_ERROR = (
        "Git executable not found. Please install Git for Windows from "
        "https://git-scm.com/download/win and restart the application."
    )

from models.project import ProjectModel

# Root directory for staging clones
_CLONES_ROOT = Path.home() / ".git-ulfa" / "clones"


class GitManager:
    """Handles all Git operations for a single project."""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _auth_url(project: ProjectModel, token: str) -> str:
        repo = project.github_repository.strip().strip("/")
        return f"https://{token}@github.com/{repo}.git"

    @staticmethod
    def _clean_url(project: ProjectModel) -> str:
        repo = project.github_repository.strip().strip("/")
        return f"https://github.com/{repo}.git"

    def _staging_dir(self, project: ProjectModel) -> Path:
        """Return the path of the staging clone for this project."""
        return _CLONES_ROOT / project.project_id

    def _uses_subfolder(self, project: ProjectModel) -> bool:
        return bool(project.repo_subfolder and project.repo_subfolder.strip("/"))

    def _working_path(self, project: ProjectModel) -> str:
        """
        Return the path of the git working tree root.
        - No subfolder → the project's local directory itself.
        - With subfolder → the staging clone directory.
        """
        if self._uses_subfolder(project):
            return str(self._staging_dir(project))
        return project.local_path

    def _target_subfolder_path(self, project: ProjectModel) -> Optional[Path]:
        """
        Return the absolute path of the subfolder inside the staging clone,
        or None when no subfolder is configured.
        """
        if not self._uses_subfolder(project):
            return None
        return self._staging_dir(project) / project.repo_subfolder.strip("/")

    # ------------------------------------------------------------------
    # Staging clone management
    # ------------------------------------------------------------------

    def _ensure_staging_clone(self, project: ProjectModel, token: str) -> Tuple[bool, str]:
        """
        Ensure the staging clone exists and has the remote configured.
        Clones the repo if the staging dir does not exist yet.
        """
        staging = self._staging_dir(project)
        staging.parent.mkdir(parents=True, exist_ok=True)
        auth_url = self._auth_url(project, token)
        clean_url = self._clean_url(project)

        try:
            if staging.exists():
                repo = Repo(str(staging))
                if "origin" in [r.name for r in repo.remotes]:
                    repo.remotes.origin.set_url(auth_url)
                else:
                    repo.create_remote("origin", auth_url)
            else:
                # Clone the remote repo into the staging directory
                repo = Repo.clone_from(auth_url, str(staging))

            # Switch to the target branch (create it if needed)
            branch = project.branch or "main"
            try:
                repo.git.checkout(branch)
            except GitCommandError:
                repo.git.checkout("-b", branch)

            # Store the clean URL (no token) so .git/config is safe
            repo.remotes.origin.set_url(clean_url)
            return True, ""

        except Exception as exc:
            return False, str(exc)

    def _sync_files_to_subfolder(self, project: ProjectModel) -> None:
        """
        Mirror the project's local files into the configured subfolder
        inside the staging clone, then remove files that no longer exist locally.
        """
        subfolder_path = self._target_subfolder_path(project)
        if subfolder_path is None:
            return

        local = Path(project.local_path)
        subfolder_path.mkdir(parents=True, exist_ok=True)

        # Copy new / updated files
        for src in local.rglob("*"):
            # Skip .git and other ignored patterns
            rel = src.relative_to(local)
            parts = rel.parts
            if any(p.startswith(".git") or p == "__pycache__" for p in parts):
                continue
            dest = subfolder_path / rel
            if src.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dest))

        # Remove files in the staging subfolder that no longer exist locally
        if subfolder_path.exists():
            for dest in list(subfolder_path.rglob("*")):
                if dest.is_file():
                    rel = dest.relative_to(subfolder_path)
                    if not (local / rel).exists():
                        dest.unlink(missing_ok=True)

    # ------------------------------------------------------------------
    # Repository initialisation
    # ------------------------------------------------------------------

    def ensure_repo(self, project: ProjectModel, token: str) -> Tuple[bool, str]:
        """
        Ensure the project has a valid git repository with a GitHub remote.

        Two modes:
        - repo_subfolder set  → staging clone in ~/.git-ulfa/clones/<id>/
          The local files are mirrored into the named sub-directory only.
          Multiple projects can safely share one repository.
        - repo_subfolder empty → the local directory IS the repo root.
          Use this ONLY when this project owns the entire repository.
          git add -A is safe here because no other project's files exist.
        """
        if not _GITPYTHON_AVAILABLE:
            return False, _GITPYTHON_ERROR

        if self._uses_subfolder(project):
            return self._ensure_staging_clone(project, token)

        # ── Simple mode: this project owns the entire repository ───────
        path = project.local_path
        if not Path(path).exists():
            return False, f"Project path does not exist: {path}"

        try:
            try:
                repo = Repo(path)
            except InvalidGitRepositoryError:
                repo = Repo.init(path)

            # Set git identity if not configured globally
            try:
                repo.config_reader().get_value("user", "email")
            except Exception:
                with repo.config_writer() as cw:
                    cw.set_value("user", "name", "Git-ULFA")
                    cw.set_value("user", "email", "git-ulfa@localhost")

            # Point the remote at the auth URL for this session
            auth_url = self._auth_url(project, token)
            if "origin" in [r.name for r in repo.remotes]:
                repo.remotes.origin.set_url(auth_url)
            else:
                repo.create_remote("origin", auth_url)

            # Make sure HEAD points to the configured branch name so that
            # the first commit lands on the right branch (e.g. "main").
            # We do NOT fetch or checkout — that would overwrite local files.
            branch = project.branch or "main"
            try:
                repo.git.symbolic_ref("HEAD", f"refs/heads/{branch}")
            except Exception:
                pass

            return True, ""

        except Exception as exc:
            return False, str(exc)

    # ------------------------------------------------------------------
    # Staging / committing
    # ------------------------------------------------------------------

    def has_changes(self, project: ProjectModel) -> bool:
        if not _GITPYTHON_AVAILABLE:
            return False
        try:
            repo = Repo(self._working_path(project))
            return repo.is_dirty(untracked_files=True)
        except Exception:
            return False

    def commit_all(self, project: ProjectModel, message: str) -> Tuple[bool, str]:
        """
        Stage all changes and create a commit.
        If a subfolder is configured, files are first mirrored from the local
        directory into the staging clone's subfolder.

        Returns (True, commit_sha) on success or (False, error_message).
        """
        if not _GITPYTHON_AVAILABLE:
            return False, _GITPYTHON_ERROR
        try:
            if self._uses_subfolder(project):
                self._sync_files_to_subfolder(project)

            repo = Repo(self._working_path(project))
            repo.git.add(A=True)

            # Use `git status --porcelain` — reliable on fresh checkouts and
            # orphan branches where is_dirty() gives false negatives.
            if not repo.git.status("--porcelain").strip():
                return True, ""

            commit = repo.index.commit(message)
            return True, commit.hexsha
        except GitCommandError as exc:
            return False, str(exc)
        except Exception as exc:
            return False, str(exc)

    # ------------------------------------------------------------------
    # Push / Pull
    # ------------------------------------------------------------------

    def push(self, project: ProjectModel, token: str) -> Tuple[bool, str]:
        if not _GITPYTHON_AVAILABLE:
            return False, _GITPYTHON_ERROR
        try:
            repo = Repo(self._working_path(project))
            origin = repo.remotes.origin
            auth_url = self._auth_url(project, token)
            clean_url = self._clean_url(project)
            origin.set_url(auth_url)

            try:
                branch = project.branch or "main"
                push_info = origin.push(
                    refspec=f"{branch}:{branch}",
                    set_upstream=True,
                )
                for info in push_info:
                    if info.flags & info.ERROR:
                        return False, f"Push error: {info.summary}"
            finally:
                origin.set_url(clean_url)

            return True, ""

        except GitCommandError as exc:
            return False, str(exc)
        except Exception as exc:
            return False, str(exc)

    def pull(self, project: ProjectModel, token: str) -> Tuple[bool, str]:
        if not _GITPYTHON_AVAILABLE:
            return False, _GITPYTHON_ERROR
        try:
            repo = Repo(self._working_path(project))
            origin = repo.remotes.origin
            auth_url = self._auth_url(project, token)
            clean_url = self._clean_url(project)
            origin.set_url(auth_url)

            try:
                branch = project.branch or "main"
                # Fetch first to check whether the remote branch exists at all
                origin.fetch()
                remote_heads = [r.remote_head for r in origin.refs]
                if branch not in remote_heads:
                    # Remote branch doesn't exist yet (brand-new repo or new branch)
                    # — nothing to pull, the first push will create it
                    return True, ""
                # Pull with allow-unrelated-histories in case local repo was
                # just git-init'd and doesn't share history with the remote
                repo.git.pull(
                    "--allow-unrelated-histories",
                    "--no-rebase",
                    "origin",
                    branch,
                )
            finally:
                origin.set_url(clean_url)

            return True, ""

        except GitCommandError as exc:
            err = str(exc).lower()
            if "no tracking information" in err or "couldn't find remote ref" in err:
                return True, ""
            return False, str(exc)
        except Exception as exc:
            return False, str(exc)

    # ------------------------------------------------------------------
    # History / info
    # ------------------------------------------------------------------

    def get_commit_count(self, project: ProjectModel) -> int:
        if not _GITPYTHON_AVAILABLE:
            return 0
        try:
            repo = Repo(self._working_path(project))
            return sum(1 for _ in repo.iter_commits())
        except Exception:
            return 0

    def get_last_commit_message(self, project: ProjectModel) -> str:
        if not _GITPYTHON_AVAILABLE:
            return ""
        try:
            repo = Repo(self._working_path(project))
            return repo.head.commit.message.strip()
        except Exception:
            return ""

    def is_git_repo(self, path: str) -> bool:
        if not _GITPYTHON_AVAILABLE:
            return False
        try:
            Repo(path)
            return True
        except Exception:
            return False


try:
    import os as _os
    _os.environ.setdefault("GIT_PYTHON_REFRESH", "quiet")
    import git
    from git import GitCommandError, InvalidGitRepositoryError, Repo
    # Verify the git executable is actually reachable
    git.Git().version()
    _GITPYTHON_AVAILABLE = True
    _GITPYTHON_ERROR = ""
except ImportError:
    _GITPYTHON_AVAILABLE = False
    _GITPYTHON_ERROR = "GitPython is not installed. Run: pip install gitpython"
except Exception as _e:
    _GITPYTHON_AVAILABLE = False
    _GITPYTHON_ERROR = (
        "Git executable not found. Please install Git for Windows from "
        "https://git-scm.com/download/win and restart the application."
    )

from models.project import ProjectModel
