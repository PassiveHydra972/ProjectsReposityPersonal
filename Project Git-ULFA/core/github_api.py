"""
GitHub API wrapper for Project Git-ULFA.

Provides token validation, repository listing/creation, and basic
account information via the PyGithub library.
"""
from typing import List, Optional, Tuple

try:
    from github import Github, GithubException, Auth
    _PYGITHUB_AVAILABLE = True
except ImportError:
    _PYGITHUB_AVAILABLE = False


class GitHubAPI:
    """Thin wrapper around the PyGithub library."""

    def __init__(self, token: str = "") -> None:
        self._token = token
        self._gh = None
        if token and _PYGITHUB_AVAILABLE:
            self._gh = Github(auth=Auth.Token(token))

    def update_token(self, token: str) -> None:
        self._token = token
        if _PYGITHUB_AVAILABLE and token:
            self._gh = Github(auth=Auth.Token(token))
        else:
            self._gh = None

    # ------------------------------------------------------------------
    # Token / account validation
    # ------------------------------------------------------------------

    def validate_token(self) -> Tuple[bool, str]:
        """
        Validate the current token.

        Returns (True, username) on success or (False, error_message) on failure.
        """
        if not _PYGITHUB_AVAILABLE:
            return False, "PyGithub is not installed. Run: pip install PyGithub"
        if not self._token:
            return False, "No Personal Access Token configured."
        if self._gh is None:
            return False, "GitHub client not initialised."
        try:
            user = self._gh.get_user()
            # Access .login to trigger the actual API call
            login = user.login
            return True, login
        except GithubException as exc:
            return False, f"GitHub error {exc.status}: {exc.data.get('message', str(exc))}"
        except Exception as exc:
            return False, str(exc)

    def get_username(self) -> Optional[str]:
        """Return the authenticated user's login name, or None on failure."""
        ok, result = self.validate_token()
        return result if ok else None

    # ------------------------------------------------------------------
    # Repository management
    # ------------------------------------------------------------------

    def list_repositories(self) -> List[str]:
        """Return a list of repository full names (owner/repo) for the user."""
        if self._gh is None:
            return []
        try:
            return [r.full_name for r in self._gh.get_user().get_repos()]
        except Exception:
            return []

    def repo_exists(self, full_name: str) -> bool:
        """Check whether *full_name* (e.g. 'user/repo') exists and is accessible."""
        if self._gh is None:
            return False
        try:
            self._gh.get_repo(full_name)
            return True
        except Exception:
            return False

    def create_repository(
        self,
        name: str,
        private: bool = True,
        description: str = "Managed by Project Git-ULFA",
    ) -> Tuple[bool, str]:
        """
        Create a new repository for the authenticated user.

        Returns (True, full_name) on success or (False, error_message) on failure.
        """
        if self._gh is None:
            return False, "Not connected to GitHub."
        try:
            repo = self._gh.get_user().create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=False,
            )
            return True, repo.full_name
        except GithubException as exc:
            return False, f"GitHub error {exc.status}: {exc.data.get('message', str(exc))}"
        except Exception as exc:
            return False, str(exc)

    def get_default_branch(self, full_name: str) -> str:
        """Return the default branch name of a repository."""
        if self._gh is None:
            return "main"
        try:
            return self._gh.get_repo(full_name).default_branch
        except Exception:
            return "main"

    def list_repo_folders(self, full_name: str, branch: str = "") -> List[str]:
        """
        Return a flat list of top-level directory paths inside *full_name*.

        Recurses one level deep so users can pick e.g. ``projects/my-app``.
        Returns an empty list on any error.
        """
        if self._gh is None:
            return []
        try:
            repo = self._gh.get_repo(full_name)
            ref = branch or repo.default_branch
            # Top-level directories
            top_dirs = [
                c.path for c in repo.get_contents("", ref=ref)
                if c.type == "dir"
            ]
            # One level of sub-directories for each top-level dir
            sub_dirs: List[str] = []
            for d in top_dirs:
                try:
                    for c in repo.get_contents(d, ref=ref):
                        if c.type == "dir":
                            sub_dirs.append(c.path)
                except Exception:
                    pass
            return top_dirs + sub_dirs
        except Exception:
            return []

    def delete_all_repo_files(
        self,
        full_name: str,
        branch: str = "",
        progress_callback=None,
    ) -> Tuple[bool, str]:
        """
        Delete every file in *full_name* on *branch* via the GitHub API.

        *progress_callback(current, total, path)* is called after each deletion
        if provided.  Returns (True, "") on success or (False, error_message).
        """
        if self._gh is None:
            return False, "Not connected to GitHub."
        try:
            repo = self._gh.get_repo(full_name)
            ref = branch or repo.default_branch

            # Collect all file blobs recursively using the Git Trees API
            # (much faster than walking get_contents recursively)
            tree = repo.get_git_tree(ref, recursive=True)
            files = [leaf for leaf in tree.tree if leaf.type == "blob"]
            total = len(files)

            if total == 0:
                return True, ""

            for i, leaf in enumerate(files):
                # get_contents returns the file object with its sha
                contents = repo.get_contents(leaf.path, ref=ref)
                repo.delete_file(
                    path=leaf.path,
                    message=f"Git-ULFA: Remove {leaf.path}",
                    sha=contents.sha,
                    branch=ref,
                )
                if progress_callback:
                    progress_callback(i + 1, total, leaf.path)

            return True, ""

        except Exception as exc:
            return False, str(exc)
