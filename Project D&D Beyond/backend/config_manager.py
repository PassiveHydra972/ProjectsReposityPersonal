"""
config_manager.py
Manages config categories and preset operations.
"""

from backend import file_manager as fm


def get_config_text() -> str:
    return fm.read_config()


def save_config_text(text: str) -> None:
    fm.write_config(text)


def get_categories() -> list[str]:
    """Return non-empty lines from the config as category names."""
    text = fm.read_config()
    return [line.strip() for line in text.splitlines() if line.strip()]


def list_presets() -> list[str]:
    return fm.list_presets()


def load_preset(name: str) -> str:
    return fm.load_preset(name)


def save_preset(name: str, content: str) -> None:
    fm.save_preset(name, content)
