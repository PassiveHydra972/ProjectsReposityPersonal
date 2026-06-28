"""
Ignore-pattern matching for Project Git-ULFA.

Supports gitignore-style patterns (glob wildcards, leading /, negation).
"""
import fnmatch
import os
from pathlib import Path, PurePosixPath
from typing import List, Sequence


# Patterns that are always ignored regardless of user configuration
HARDCODED_IGNORES: List[str] = [
    ".git",
    ".git/*",
    "__pycache__",
    "__pycache__/*",
    "*.pyc",
    "*.pyo",
]


class IgnoreMatcher:
    """
    Determines whether a given file path should be ignored.

    Patterns follow a gitignore-like syntax:
    - ``*``   matches anything except a path separator
    - ``**``  matches anything including path separators
    - Leading ``/`` anchors to the base directory
    - Leading ``!`` negates the pattern (un-ignores)
    """

    def __init__(
        self,
        base_path: str,
        patterns: Sequence[str],
        extra_patterns: Sequence[str] | None = None,
    ) -> None:
        self._base = Path(base_path).resolve()
        raw = list(HARDCODED_IGNORES) + list(patterns) + list(extra_patterns or [])
        self._patterns: List[tuple[bool, str]] = []  # (is_negation, pattern)
        for p in raw:
            p = p.strip()
            if not p or p.startswith("#"):
                continue
            if p.startswith("!"):
                self._patterns.append((True, p[1:]))
            else:
                self._patterns.append((False, p))

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def is_ignored(self, abs_path: str) -> bool:
        """Return True if *abs_path* should be ignored."""
        try:
            rel = Path(abs_path).resolve().relative_to(self._base)
        except ValueError:
            return False

        rel_str = rel.as_posix()           # always forward-slashes
        name = Path(abs_path).name
        ignored = False

        for is_negation, pattern in self._patterns:
            if self._match(pattern, rel_str, name):
                ignored = not is_negation

        return ignored

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _match(self, pattern: str, rel_posix: str, name: str) -> bool:
        # Strip leading slash for anchored patterns; remember anchorage
        anchored = pattern.startswith("/")
        if anchored:
            pattern = pattern[1:]

        # Patterns ending with / only match directories – we can't easily
        # know that here, so match both.
        dir_only = pattern.endswith("/")
        if dir_only:
            pattern = pattern[:-1]

        # ** matches any path depth
        if "**" in pattern:
            # Convert ** to a regex-style glob
            pat = pattern.replace("**", "*")
            if fnmatch.fnmatch(rel_posix, pat):
                return True
            return False

        if "/" in pattern:
            # Pattern contains a slash → must match the relative path
            return fnmatch.fnmatch(rel_posix, pattern)
        else:
            # No slash → match against the file name only OR any path segment
            if fnmatch.fnmatch(name, pattern):
                return True
            # Also match any path component (e.g. "node_modules" inside subdirs)
            for part in Path(rel_posix).parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
            return False


def load_gitignore(project_path: str) -> List[str]:
    """Read patterns from a .gitignore file in the project directory."""
    gitignore = Path(project_path) / ".gitignore"
    if not gitignore.exists():
        return []
    patterns: List[str] = []
    try:
        for line in gitignore.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)
    except OSError:
        pass
    return patterns
