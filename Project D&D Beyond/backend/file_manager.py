"""
file_manager.py
Handles all file I/O for the application.
"""

import os
from pathlib import Path

# Resolve project root relative to this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent

PATHS = {
    "image_analysis": PROJECT_ROOT / "temp" / "current_image_analysis.txt",
    "text_input":     PROJECT_ROOT / "temp" / "current_text_input.txt",
    "config":         PROJECT_ROOT / "config" / "current_config.txt",
    "output":         PROJECT_ROOT / "output" / "generated_output.txt",
    "presets_dir":    PROJECT_ROOT / "config" / "presets",
}


def _ensure_parents(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_file(key: str) -> str:
    """Read a managed file by key. Returns empty string if not found."""
    path = PATHS[key]
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def write_file(key: str, content: str) -> None:
    """Overwrite a managed file entirely."""
    path = PATHS[key]
    _ensure_parents(path)
    path.write_text(content, encoding="utf-8")


def write_image_analysis(content: str) -> None:
    """Always overwrites — never appends. Prevents context contamination."""
    write_file("image_analysis", content)


def write_text_input(content: str) -> None:
    write_file("text_input", content)


def write_config(content: str) -> None:
    write_file("config", content)


def write_output(content: str) -> None:
    write_file("output", content)


def read_image_analysis() -> str:
    return read_file("image_analysis")


def read_text_input() -> str:
    return read_file("text_input")


def read_config() -> str:
    return read_file("config")


def read_output() -> str:
    return read_file("output")


def list_presets() -> list[str]:
    """Return list of preset filenames (without extension)."""
    presets_dir: Path = PATHS["presets_dir"]
    if not presets_dir.exists():
        return []
    return [p.stem for p in sorted(presets_dir.glob("*.txt"))]


def load_preset(name: str) -> str:
    path: Path = PATHS["presets_dir"] / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def save_preset(name: str, content: str) -> None:
    presets_dir: Path = PATHS["presets_dir"]
    presets_dir.mkdir(parents=True, exist_ok=True)
    (presets_dir / f"{name}.txt").write_text(content, encoding="utf-8")
