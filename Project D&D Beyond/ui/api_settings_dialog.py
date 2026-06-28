"""
api_settings_dialog.py
Dialog for entering and saving API keys for online providers.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QFrame,
)

from backend import provider_manager as pm

PROVIDER_LINKS = {
    "openai":    ("OpenAI (ChatGPT)", "https://platform.openai.com/api-keys"),
    "grok":      ("Grok (xAI)",       "https://console.x.ai/"),
    "anthropic": ("Anthropic (Claude)", "https://console.anthropic.com/settings/keys"),
}


class ApiSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Key Settings")
        self.setMinimumWidth(480)
        self.setModal(True)
        self.setStyleSheet(
            "QDialog { background: #161b22; color: #e6edf3; }"
            "QLabel { color: #e6edf3; }"
            "QLineEdit { background: #0d1117; color: #e6edf3; "
            "  border: 1px solid #30363d; border-radius: 4px; padding: 6px 8px; }"
            "QLineEdit:focus { border-color: #58a6ff; }"
            "QPushButton { background: #21262d; color: #e6edf3; "
            "  border: 1px solid #30363d; border-radius: 4px; padding: 6px 12px; }"
            "QPushButton:hover { background: #30363d; }"
        )
        self._fields: dict[str, QLineEdit] = {}
        self._build_ui()
        self._load_keys()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Online Provider API Keys")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #58a6ff;")
        layout.addWidget(title)

        note = QLabel(
            "Keys are stored locally in config/providers.json and never sent anywhere "
            "except the respective provider's API."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #8b949e; font-size: 11px;")
        layout.addWidget(note)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #30363d;")
        layout.addWidget(divider)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        for key, (label, _url) in PROVIDER_LINKS.items():
            lbl = QLabel(f"{label}:")
            field = QLineEdit()
            field.setPlaceholderText("sk-…  (leave blank to skip)")
            field.setEchoMode(QLineEdit.Password)
            self._fields[key] = field
            form.addRow(lbl, field)

        layout.addLayout(form)

        # Show/hide toggle
        toggle = QPushButton("Show / Hide Keys")
        toggle.setCheckable(True)
        toggle.clicked.connect(self._toggle_visibility)
        layout.addWidget(toggle)

        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)
        divider2.setStyleSheet("color: #30363d;")
        layout.addWidget(divider2)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(
            "QPushButton { background: #238636; color: white; border: none; "
            "border-radius: 4px; padding: 6px 20px; }"
            "QPushButton:hover { background: #2ea043; }"
        )
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def _load_keys(self):
        for provider, field in self._fields.items():
            field.setText(pm.get_api_key(provider))

    def _save(self):
        for provider, field in self._fields.items():
            pm.set_api_key(provider, field.text().strip())
        self.accept()

    def _toggle_visibility(self, checked: bool):
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        for field in self._fields.values():
            field.setEchoMode(mode)
