"""
output_tab.py
OUTPUT MODE — generate, view, copy, save structured output.
"""

import threading
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QFileDialog, QProgressBar,
)

from backend import output_generator, file_manager as fm


class _WorkerSignals(QObject):
    progress = Signal(str)
    chunk = Signal(str)
    finished = Signal(str)
    error = Signal(str)


class OutputTab(QWidget):
    def __init__(self, get_model_fn, parent=None):
        super().__init__(parent)
        self._get_model = get_model_fn
        self._signals = _WorkerSignals()
        self._signals.progress.connect(self._on_progress)
        self._signals.chunk.connect(self._on_chunk)
        self._signals.finished.connect(self._on_finished)
        self._signals.error.connect(self._on_error)
        self._build_ui()
        self._load_existing()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("OUTPUT")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #c8d8e8;")
        layout.addWidget(title)

        # Action buttons
        btn_row = QHBoxLayout()

        self._generate_btn = QPushButton("Generate Output")
        self._generate_btn.setStyleSheet(
            "QPushButton { background: #9b59b6; color: white; font-size: 14px; "
            "padding: 8px 16px; border-radius: 6px; }"
            "QPushButton:hover { background: #a66bbe; }"
            "QPushButton:disabled { background: #3a4a5a; color: #6a7a8a; }"
        )
        self._generate_btn.clicked.connect(self._run_generate)
        btn_row.addWidget(self._generate_btn)

        self._regen_btn = QPushButton("Regenerate")
        self._regen_btn.setStyleSheet(
            "QPushButton { background: #5a3a7a; color: white; padding: 8px 12px; "
            "border-radius: 6px; }"
            "QPushButton:hover { background: #6a4a8a; }"
            "QPushButton:disabled { background: #3a4a5a; color: #6a7a8a; }"
        )
        self._regen_btn.setEnabled(False)
        self._regen_btn.clicked.connect(self._run_generate)
        btn_row.addWidget(self._regen_btn)

        btn_row.addStretch()

        self._copy_btn = QPushButton("Copy to Clipboard")
        self._copy_btn.clicked.connect(self._copy_output)
        btn_row.addWidget(self._copy_btn)

        self._save_btn = QPushButton("Save Output…")
        self._save_btn.clicked.connect(self._save_output)
        btn_row.addWidget(self._save_btn)

        layout.addLayout(btn_row)

        # Progress bar (indeterminate marquee while generating)
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # indeterminate
        self._progress.setFixedHeight(6)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet(
            "QProgressBar { background: #21262d; border: none; border-radius: 3px; }"
            "QProgressBar::chunk { background: #58a6ff; border-radius: 3px; }"
        )
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # Status
        self._status = QLabel("")
        self._status.setStyleSheet("color: #58a6ff; font-size: 12px;")
        layout.addWidget(self._status)

        # Output viewer
        self._output_view = QTextEdit()
        self._output_view.setReadOnly(True)
        self._output_view.setStyleSheet(
            "QTextEdit { background: #0d1117; color: #e6edf3; "
            "border: 1px solid #30363d; border-radius: 4px; "
            "font-family: monospace; font-size: 13px; }"
        )
        layout.addWidget(self._output_view, stretch=1)

    def _load_existing(self):
        existing = fm.read_output()
        if existing and not existing.startswith("(No output"):
            self._output_view.setPlainText(existing)
            self._regen_btn.setEnabled(True)

    def _run_generate(self):
        model = self._get_model()
        if not model:
            self._set_status("ERROR: No model selected.")
            return
        self._generate_btn.setEnabled(False)
        self._regen_btn.setEnabled(False)
        self._output_view.clear()
        self._progress.setVisible(True)
        self._set_status(f"Generating with model: {model}…")
        threading.Thread(target=self._generate_worker, daemon=True).start()

    def _generate_worker(self):
        try:
            result = output_generator.generate_output(
                model=self._get_model(),
                progress_callback=lambda msg: self._signals.progress.emit(msg),
                chunk_callback=lambda token: self._signals.chunk.emit(token),
            )
            self._signals.finished.emit(result)
        except Exception as exc:  # noqa: BLE001
            self._signals.error.emit(str(exc))

    def _on_progress(self, msg: str):
        self._set_status(msg)

    def _on_chunk(self, token: str):
        # Append token directly — moves cursor to end for live streaming
        cursor = self._output_view.textCursor()
        from PySide6.QtGui import QTextCursor
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(token)
        self._output_view.setTextCursor(cursor)

    def _on_finished(self, result: str):
        self._output_view.setPlainText(result)
        self._progress.setVisible(False)
        self._set_status("Output generated successfully.")
        self._generate_btn.setEnabled(True)
        self._regen_btn.setEnabled(True)

    def _on_error(self, msg: str):
        self._progress.setVisible(False)
        self._set_status(f"ERROR: {msg}")
        self._output_view.setPlainText(f"Error during generation:\n\n{msg}")
        self._generate_btn.setEnabled(True)
        self._regen_btn.setEnabled(True)

    def _copy_output(self):
        from PySide6.QtWidgets import QApplication
        text = self._output_view.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self._set_status("Copied to clipboard.")

    def _save_output(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Output", "generated_output.txt", "Text Files (*.txt)"
        )
        if path:
            Path(path).write_text(self._output_view.toPlainText(), encoding="utf-8")
            self._set_status(f"Saved to {path}")

    def _set_status(self, msg: str):
        self._status.setText(msg)
