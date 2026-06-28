"""
config_tab.py
CONFIG / TEXT INPUT MODE — edit config categories, manage presets, add text context.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QLineEdit, QComboBox, QInputDialog,
    QMessageBox, QSplitter,
)

from backend import config_manager, file_manager as fm


class ConfigTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load_all()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("CONFIG / TEXT INPUT")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #c8d8e8;")
        layout.addWidget(title)

        splitter = QSplitter(Qt.Horizontal)

        # --- Left: config editor ---
        config_panel = QWidget()
        cp_layout = QVBoxLayout(config_panel)
        cp_layout.setContentsMargins(0, 0, 8, 0)

        cp_layout.addWidget(QLabel("Output Categories (one per line):"))

        self._config_edit = QTextEdit()
        self._config_edit.setStyleSheet(
            "QTextEdit { background: #0d1117; color: #e6edf3; "
            "border: 1px solid #30363d; border-radius: 4px; font-family: monospace; }"
        )
        self._config_edit.setPlaceholderText("AGE\nHEIGHT\nPHYSICAL FEATURES\nRACE\nGENDER")
        cp_layout.addWidget(self._config_edit, stretch=1)

        # Preset controls
        preset_row = QHBoxLayout()
        self._preset_combo = QComboBox()
        self._preset_combo.setMinimumWidth(160)
        preset_row.addWidget(QLabel("Preset:"))
        preset_row.addWidget(self._preset_combo)

        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self._load_preset)
        preset_row.addWidget(load_btn)

        save_preset_btn = QPushButton("Save Preset…")
        save_preset_btn.clicked.connect(self._save_preset)
        preset_row.addWidget(save_preset_btn)
        preset_row.addStretch()
        cp_layout.addLayout(preset_row)

        # Save config button
        save_cfg_btn = QPushButton("Save Config")
        save_cfg_btn.setStyleSheet(
            "QPushButton { background: #238636; color: white; padding: 6px; "
            "border-radius: 4px; }"
            "QPushButton:hover { background: #2ea043; }"
        )
        save_cfg_btn.clicked.connect(self._save_config)
        cp_layout.addWidget(save_cfg_btn)

        splitter.addWidget(config_panel)

        # --- Right: text input ---
        text_panel = QWidget()
        tp_layout = QVBoxLayout(text_panel)
        tp_layout.setContentsMargins(8, 0, 0, 0)

        tp_layout.addWidget(QLabel("Supplementary Text Input (optional):"))

        self._text_input = QTextEdit()
        self._text_input.setStyleSheet(
            "QTextEdit { background: #0d1117; color: #e6edf3; "
            "border: 1px solid #30363d; border-radius: 4px; font-family: monospace; }"
        )
        self._text_input.setPlaceholderText(
            "e.g. Character is immortal\nFemale\nFantasy setting"
        )
        tp_layout.addWidget(self._text_input, stretch=1)

        save_text_btn = QPushButton("Save Text Input")
        save_text_btn.setStyleSheet(
            "QPushButton { background: #238636; color: white; padding: 6px; "
            "border-radius: 4px; }"
            "QPushButton:hover { background: #2ea043; }"
        )
        save_text_btn.clicked.connect(self._save_text_input)
        tp_layout.addWidget(save_text_btn)

        clear_text_btn = QPushButton("Clear Text Input")
        clear_text_btn.clicked.connect(self._clear_text_input)
        tp_layout.addWidget(clear_text_btn)

        splitter.addWidget(text_panel)
        splitter.setSizes([400, 400])
        layout.addWidget(splitter, stretch=1)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #3fb950; font-size: 12px;")
        layout.addWidget(self._status)

    def _load_all(self):
        self._config_edit.setPlainText(config_manager.get_config_text())
        self._text_input.setPlainText(fm.read_text_input())
        self._refresh_presets()

    def _refresh_presets(self):
        self._preset_combo.clear()
        for name in config_manager.list_presets():
            self._preset_combo.addItem(name)

    def _load_preset(self):
        name = self._preset_combo.currentText()
        if name:
            content = config_manager.load_preset(name)
            self._config_edit.setPlainText(content)
            self._set_status(f"Preset '{name}' loaded.")

    def _save_preset(self):
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name.strip():
            name = name.strip()
            config_manager.save_preset(name, self._config_edit.toPlainText())
            self._refresh_presets()
            idx = self._preset_combo.findText(name)
            if idx >= 0:
                self._preset_combo.setCurrentIndex(idx)
            self._set_status(f"Preset '{name}' saved.")

    def _save_config(self):
        config_manager.save_config_text(self._config_edit.toPlainText())
        self._set_status("Config saved.")

    def _save_text_input(self):
        fm.write_text_input(self._text_input.toPlainText())
        self._set_status("Text input saved.")

    def _clear_text_input(self):
        self._text_input.clear()
        fm.write_text_input("")
        self._set_status("Text input cleared.")

    def _set_status(self, msg: str):
        self._status.setText(msg)
