"""
ULFA-Link.py  —  Project Git-ULFA Folder Linking Helper

Copy or place this script inside any folder you want to archive with
Project Git-ULFA, then run it.  The folder will be queued for registration
and picked up automatically when Git-ULFA is running.

Usage:
    python ULFA-Link.py              # Links the current working directory
    python ULFA-Link.py /some/path   # Links the specified path
"""
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ULFA_DATA_DIR: Path = Path.home() / ".git-ulfa"
LINK_QUEUE_FILE: Path = ULFA_DATA_DIR / "link_queue.json"
PROJECTS_FILE: Path = ULFA_DATA_DIR / "projects.json"

BANNER = """
╔══════════════════════════════════════════════════════╗
║       Project Git-ULFA  —  Folder Linking Helper     ║
╚══════════════════════════════════════════════════════╝
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_target_path() -> Path:
    """Return the path to link: argv[1] if given, else the script's directory."""
    if len(sys.argv) > 1:
        p = Path(sys.argv[1]).resolve()
    else:
        # Use CWD so the user can run:  python ULFA-Link.py  from any folder
        p = Path.cwd().resolve()
    return p


def _load_json(path: Path) -> list:
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_json(path: Path, data: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _is_already_linked(folder: Path) -> tuple[bool, str]:
    """Check the main projects file for an existing entry."""
    projects = _load_json(PROJECTS_FILE)
    for proj in projects:
        try:
            existing = Path(proj["local_path"]).resolve()
        except (KeyError, TypeError):
            continue
        if existing == folder:
            return True, proj.get("project_name", str(folder))
    return False, ""


def _is_in_queue(folder: Path) -> bool:
    """Check whether this folder is already waiting in the link queue."""
    queue = _load_json(LINK_QUEUE_FILE)
    for entry in queue:
        try:
            queued = Path(entry["local_path"]).resolve()
        except (KeyError, TypeError):
            continue
        if queued == folder:
            return True
    return False


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def register_folder(folder: Path) -> bool:
    """Queue *folder* for registration with Git-ULFA."""
    ULFA_DATA_DIR.mkdir(parents=True, exist_ok=True)

    already, name = _is_already_linked(folder)
    if already:
        print(f"\n  [!] This folder is already linked as '{name}'.")
        print("      Open the Git-ULFA dashboard to manage it.\n")
        return False

    if _is_in_queue(folder):
        print("\n  [!] This folder is already queued for linking.")
        print("      Open Git-ULFA to complete setup.\n")
        return False

    project_id = str(uuid.uuid4())
    folder_name = folder.name

    entry = {
        "project_name": folder_name,
        "project_id": project_id,
        "local_path": str(folder),
        "github_repository": "",
        "branch": "main",
        "sync_enabled": False,
        "live_sync": True,
        "date_linked": datetime.now().isoformat(),
        "last_sync": None,
        "sync_interval": 300,
        "commit_template": "Git-ULFA: Updated {project_name} - {timestamp}",
        "backup_destinations": ["github"],
        "ignore_patterns": [],
        "status": "pending_setup",
        "pending_changes": 0,
        "last_error": None,
        "auto_push": True,
        "max_changes_before_push": 10,
    }

    queue = _load_json(LINK_QUEUE_FILE)
    queue.append(entry)
    _save_json(LINK_QUEUE_FILE, queue)

    print(f"\n  ✓  Folder registered successfully!")
    print(f"     Name      : {folder_name}")
    print(f"     Path      : {folder}")
    print(f"     Project ID: {project_id}")
    print(f"\n  → Open the Git-ULFA dashboard to configure")
    print(f"    the GitHub repository and enable sync.\n")
    return True


def main() -> None:
    print(BANNER)
    target = _resolve_target_path()

    print(f"  Folder to link:\n  {target}\n")

    if not target.exists():
        print(f"  [✕] Path does not exist: {target}")
        sys.exit(1)

    if not target.is_dir():
        print(f"  [✕] Not a directory: {target}")
        sys.exit(1)

    # Confirm
    try:
        answer = input("  Link this folder? (yes/no): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\n  Cancelled.")
        sys.exit(0)

    if answer not in ("yes", "y"):
        print("\n  Cancelled.\n")
        sys.exit(0)

    success = register_folder(target)
    if not success:
        sys.exit(1)

    try:
        input("  Press Enter to close…")
    except (KeyboardInterrupt, EOFError):
        pass


if __name__ == "__main__":
    main()
