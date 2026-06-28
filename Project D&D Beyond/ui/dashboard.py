"""
dashboard.py
Main application window — sidebar navigation, provider/model selector, tab switcher.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QComboBox, QStackedWidget,
    QFrame,
)

from backend import provider_manager as pm
from ui.image_scan_tab import ImageScanTab
from ui.config_tab import ConfigTab
from ui.output_tab import OutputTab
from ui.api_settings_dialog import ApiSettingsDialog

NAV_BUTTONS = [
    ("IMG SCAN",      0),
    ("CONFIG / TEXT", 1),
    ("OUTPUT",        2),
]

DARK_BG       = "#0d1117"
SIDEBAR_BG    = "#161b22"
ACCENT_ACTIVE = "#58a6ff"
TEXT  = "#e6edf3"
MUTED = "#8b949e"


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("D&D Beyond — LLM Character Extractor")
        self.setMinimumSize(1000, 700)
        self._selected_model: str = ""
        self._build_ui()
        self._on_provider_changed(self._provider_combo.currentData())

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.setStyleSheet(f"QMainWindow {{ background: {DARK_BG}; }}")

        central = QWidget()
        central.setStyleSheet(f"background: {DARK_BG}; color: {TEXT};")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background: {DARK_BG};")

        self._img_tab = ImageScanTab(get_model_fn=lambda: self._selected_model)
        self._cfg_tab = ConfigTab()
        self._out_tab = OutputTab(get_model_fn=lambda: self._selected_model)

        self._stack.addWidget(self._img_tab)
        self._stack.addWidget(self._cfg_tab)
        self._stack.addWidget(self._out_tab)

        root.addWidget(self._stack, stretch=1)
        self._switch_tab(0)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(188)
        sidebar.setStyleSheet(
            f"QFrame {{ background: {SIDEBAR_BG}; border-right: 1px solid #30363d; }}"
        )
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(0)

        # App title
        app_title = QLabel("D&D\nBEYOND")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setStyleSheet(
            f"color: {ACCENT_ACTIVE}; font-size: 16px; font-weight: bold; "
            "padding: 20px 8px 16px 8px; letter-spacing: 2px;"
        )
        sl.addWidget(app_title)
        sl.addWidget(self._hline())

        # Nav buttons
        self._nav_btns: list[QPushButton] = []
        for label, idx in NAV_BUTTONS:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(48)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self._nav_style(False))
            btn.clicked.connect(lambda _checked, i=idx: self._switch_tab(i))
            sl.addWidget(btn)
            self._nav_btns.append(btn)

        sl.addStretch()
        sl.addWidget(self._hline())

        # ---- Provider selector ----
        sl.addWidget(self._small_label("AI Provider:"))

        self._provider_combo = QComboBox()
        self._provider_combo.setStyleSheet(self._combo_style())
        for pid, plabel in pm.PROVIDER_LABELS.items():
            self._provider_combo.addItem(plabel, userData=pid)

        saved = pm.get_provider()
        idx = self._provider_combo.findData(saved)
        if idx >= 0:
            self._provider_combo.setCurrentIndex(idx)

        self._provider_combo.currentIndexChanged.connect(
            lambda _: self._on_provider_changed(self._provider_combo.currentData())
        )
        sl.addWidget(self._provider_combo)

        # ---- Model selector ----
        sl.addWidget(self._small_label("LLM Model:"))

        self._model_combo = QComboBox()
        self._model_combo.setStyleSheet(self._combo_style())
        self._model_combo.setEditable(True)  # allow typing custom model names
        self._model_combo.currentTextChanged.connect(self._on_model_changed)
        sl.addWidget(self._model_combo)

        # Refresh + API Keys row
        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(8, 2, 8, 2)
        row_layout.setSpacing(4)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(self._small_btn_style())
        refresh_btn.clicked.connect(
            lambda: self._on_provider_changed(self._provider_combo.currentData())
        )
        row_layout.addWidget(refresh_btn)

        api_btn = QPushButton("API Keys…")
        api_btn.setStyleSheet(self._small_btn_style())
        api_btn.clicked.connect(self._open_api_settings)
        row_layout.addWidget(api_btn)

        sl.addWidget(row_widget)

        # Status label
        self._status_lbl = QLabel("")
        self._status_lbl.setAlignment(Qt.AlignCenter)
        self._status_lbl.setWordWrap(True)
        self._status_lbl.setStyleSheet(
            "font-size: 10px; padding: 4px; margin-bottom: 8px;"
        )
        sl.addWidget(self._status_lbl)

        return sidebar

    # ------------------------------------------------------------------
    # Provider / model logic
    # ------------------------------------------------------------------

    def _on_provider_changed(self, provider_id: str):
        if not provider_id:
            return
        pm.set_provider(provider_id)
        models = pm.get_models_for_provider(provider_id)
        current = self._model_combo.currentText()
        self._model_combo.blockSignals(True)
        self._model_combo.clear()
        if models:
            self._model_combo.addItems(models)
            idx = self._model_combo.findText(current)
            if idx >= 0:
                self._model_combo.setCurrentIndex(idx)
        self._model_combo.blockSignals(False)
        self._selected_model = self._model_combo.currentText()
        self._update_status(provider_id, models)

    def _update_status(self, provider_id: str, models: list):
        label = pm.PROVIDER_LABELS.get(provider_id, provider_id)
        if provider_id == pm.LOCAL:
            from backend import llm_handler
            if llm_handler.is_ollama_running():
                self._set_status(f"Ollama: ONLINE\n{len(models)} model(s)", "#3fb950")
            else:
                self._set_status("Ollama: OFFLINE\nStart Ollama first", "#f85149")
        else:
            key = pm.get_api_key(provider_id)
            if key:
                self._set_status(f"{label}\nKey set ✓", "#3fb950")
            else:
                self._set_status(f"{label}\nNo API key — click\nAPI Keys…", "#d29922")

    def _on_model_changed(self, text: str):
        self._selected_model = text if text and not text.startswith("(") else ""

    def _open_api_settings(self):
        dlg = ApiSettingsDialog(self)
        if dlg.exec():
            self._on_provider_changed(self._provider_combo.currentData())

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _switch_tab(self, index: int):
        self._stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_btns):
            btn.setChecked(i == index)
            btn.setStyleSheet(self._nav_style(i == index))

    # ------------------------------------------------------------------
    # Style helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _nav_style(active: bool) -> str:
        if active:
            return (
                "QPushButton { background: #1f2937; color: #58a6ff; "
                "border-left: 3px solid #58a6ff; font-weight: bold; "
                "font-size: 13px; padding-left: 16px; text-align: left; }"
            )
        return (
            "QPushButton { background: transparent; color: #8b949e; "
            "border-left: 3px solid transparent; font-size: 13px; "
            "padding-left: 16px; text-align: left; }"
            "QPushButton:hover { background: #1c2128; color: #c9d1d9; }"
        )

    @staticmethod
    def _combo_style() -> str:
        return (
            "QComboBox { background: #21262d; color: #e6edf3; "
            "  border: 1px solid #30363d; border-radius: 4px; "
            "  padding: 4px 8px; margin: 2px 8px; }"
            "QComboBox QAbstractItemView { background: #21262d; color: #e6edf3; "
            "  selection-background-color: #2d6a9f; }"
        )

    @staticmethod
    def _small_btn_style() -> str:
        return (
            "QPushButton { background: #21262d; color: #8b949e; "
            "border: 1px solid #30363d; border-radius: 4px; "
            "font-size: 11px; padding: 4px 6px; }"
            "QPushButton:hover { color: #e6edf3; background: #30363d; }"
        )

    def _small_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; padding: 4px 12px 0 12px;"
        )
        return lbl

    def _set_status(self, text: str, colour: str):
        self._status_lbl.setText(text)
        self._status_lbl.setStyleSheet(
            f"font-size: 10px; padding: 4px; margin-bottom: 8px; color: {colour};"
        )

    @staticmethod
    def _hline() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #30363d; margin: 0;")
        return line

