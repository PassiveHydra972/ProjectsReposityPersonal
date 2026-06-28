"""
image_scan_tab.py
IMAGE SCAN MODE — drag/drop or browse an image, analyse with vision LLM.
"""

import threading
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QObject, QMimeData, QUrl
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QTextEdit, QSizePolicy, QFrame,
    QComboBox, QProgressBar,
)

from backend import image_analyser, llm_handler


class _WorkerSignals(QObject):
    progress = Signal(str)
    chunk = Signal(str)
    finished = Signal(str)
    error = Signal(str)


class _DropArea(QLabel):
    """A label that accepts image drops."""

    image_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 260)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            "QLabel {"
            "  border: 2px dashed #5a7fa8;"
            "  border-radius: 8px;"
            "  color: #8a9bb0;"
            "  font-size: 14px;"
            "}"
        )
        self.setText("Drag & drop image here\nor use Browse button")
        self._placeholder_text = "Drag & drop image here\nor use Browse button"

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and self._is_image(urls[0].toLocalFile()):
                event.acceptProposedAction()
                self.setStyleSheet(
                    "QLabel {"
                    "  border: 2px dashed #7eb8f7;"
                    "  border-radius: 8px;"
                    "  background: #1e2d3d;"
                    "}"
                )
                return
        event.ignore()

    def dragLeaveEvent(self, event):
        self._reset_style()

    def dropEvent(self, event: QDropEvent):
        self._reset_style()
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if self._is_image(path):
                self.image_dropped.emit(path)
        event.acceptProposedAction()

    def _reset_style(self):
        self.setStyleSheet(
            "QLabel {"
            "  border: 2px dashed #5a7fa8;"
            "  border-radius: 8px;"
            "  color: #8a9bb0;"
            "  font-size: 14px;"
            "}"
        )

    @staticmethod
    def _is_image(path: str) -> bool:
        return Path(path).suffix.lower() in {
            ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff"
        }

    def set_image(self, path: str):
        pix = QPixmap(path)
        if not pix.isNull():
            scaled = pix.scaled(
                self.width() - 8,
                self.height() - 8,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.setPixmap(scaled)
        else:
            self.setText("(Cannot preview this image)")

    def clear_image(self):
        self.clear()
        self.setText(self._placeholder_text)


class ImageScanTab(QWidget):
    def __init__(self, get_model_fn, parent=None):
        """
        get_model_fn: callable that returns the currently selected model name.
        """
        super().__init__(parent)
        self._get_model = get_model_fn
        self._current_image: str | None = None
        self._signals = _WorkerSignals()
        self._signals.progress.connect(self._on_progress)
        self._signals.chunk.connect(self._on_chunk)
        self._signals.finished.connect(self._on_finished)
        self._signals.error.connect(self._on_error)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Title
        title = QLabel("IMAGE SCAN")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #c8d8e8;")
        layout.addWidget(title)

        # Drop area
        self._drop_area = _DropArea()
        self._drop_area.image_dropped.connect(self._load_image)
        layout.addWidget(self._drop_area, stretch=1)

        # Browse + clear row
        btn_row = QHBoxLayout()
        self._browse_btn = QPushButton("Browse Image…")
        self._browse_btn.clicked.connect(self._browse)
        btn_row.addWidget(self._browse_btn)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.clicked.connect(self._clear_image)
        btn_row.addWidget(self._clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Analyse button
        self._analyse_btn = QPushButton("Analyse Image")
        self._analyse_btn.setStyleSheet(
            "QPushButton { background: #2d6a9f; color: white; font-size: 14px; "
            "padding: 8px; border-radius: 6px; }"
            "QPushButton:hover { background: #3a7fbf; }"
            "QPushButton:disabled { background: #3a4a5a; color: #6a7a8a; }"
        )
        self._analyse_btn.setEnabled(False)
        self._analyse_btn.clicked.connect(self._run_analysis)
        layout.addWidget(self._analyse_btn)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setFixedHeight(6)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet(
            "QProgressBar { background: #21262d; border: none; border-radius: 3px; }"
            "QProgressBar::chunk { background: #3a86d4; border-radius: 3px; }"
        )
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # Status log
        log_label = QLabel("Analysis Log:")
        log_label.setStyleSheet("color: #8a9bb0; font-size: 12px;")
        layout.addWidget(log_label)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(160)
        self._log.setStyleSheet(
            "QTextEdit { background: #0d1117; color: #58a6ff; "
            "border: 1px solid #30363d; border-radius: 4px; font-family: monospace; }"
        )
        layout.addWidget(self._log)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff)",
        )
        if path:
            self._load_image(path)

    def _load_image(self, path: str):
        self._current_image = path
        self._drop_area.set_image(path)
        self._analyse_btn.setEnabled(True)
        self._log_message(f"Image loaded: {path}")

    def _clear_image(self):
        self._current_image = None
        self._drop_area.clear_image()
        self._analyse_btn.setEnabled(False)
        self._log.clear()

    def _run_analysis(self):
        if not self._current_image:
            return
        model = self._get_model()
        if not model:
            self._log_message("ERROR: No model selected.")
            return
        self._analyse_btn.setEnabled(False)
        self._log_message(f"Starting analysis with model: {model}")
        self._progress.setVisible(True)
        self._log.clear()
        threading.Thread(target=self._analysis_worker, daemon=True).start()

    def _analysis_worker(self):
        try:
            image_analyser.analyse_image(
                image_path=self._current_image,
                model=self._get_model(),
                progress_callback=lambda token: self._signals.chunk.emit(token),
            )
            from backend import file_manager as fm
            result = fm.read_image_analysis()
            self._signals.finished.emit(result)
        except Exception as exc:  # noqa: BLE001
            self._signals.error.emit(str(exc))

    def _on_progress(self, msg: str):
        self._log_message(msg)

    def _on_chunk(self, token: str):
        # Stream tokens inline — append without newline prefix
        cursor = self._log.textCursor()
        from PySide6.QtGui import QTextCursor
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(token)
        self._log.setTextCursor(cursor)
        self._log.verticalScrollBar().setValue(
            self._log.verticalScrollBar().maximum()
        )

    def _on_finished(self, result: str):
        self._progress.setVisible(False)
        self._log_message("\n=== ANALYSIS SAVED ===")
        self._analyse_btn.setEnabled(True)

    def _on_error(self, msg: str):
        self._progress.setVisible(False)
        self._log_message(f"ERROR: {msg}")
        self._analyse_btn.setEnabled(True)

    def _log_message(self, msg: str):
        self._log.append(msg)
        self._log.verticalScrollBar().setValue(
            self._log.verticalScrollBar().maximum()
        )
