"""
Project Git-ULFA — GitHub Universal Local Files Archiver
Entry point.

Usage:
    python main.py
"""
import sys
from pathlib import Path

# Ensure the project root is on sys.path so all packages resolve correctly
sys.path.insert(0, str(Path(__file__).parent))

from gui.app import GitULFAApp


def main() -> None:
    app = GitULFAApp()
    app.mainloop()


if __name__ == "__main__":
    main()
