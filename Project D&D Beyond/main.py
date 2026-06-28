"""
main.py
Entry point for the D&D Beyond LLM Character Extractor.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.dashboard import Dashboard


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Global dark palette override for native widgets
    from PySide6.QtGui import QPalette, QColor
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#0d1117"))
    palette.setColor(QPalette.WindowText, QColor("#e6edf3"))
    palette.setColor(QPalette.Base, QColor("#161b22"))
    palette.setColor(QPalette.AlternateBase, QColor("#0d1117"))
    palette.setColor(QPalette.ToolTipBase, QColor("#161b22"))
    palette.setColor(QPalette.ToolTipText, QColor("#e6edf3"))
    palette.setColor(QPalette.Text, QColor("#e6edf3"))
    palette.setColor(QPalette.Button, QColor("#21262d"))
    palette.setColor(QPalette.ButtonText, QColor("#e6edf3"))
    palette.setColor(QPalette.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.Link, QColor("#58a6ff"))
    palette.setColor(QPalette.Highlight, QColor("#2d6a9f"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = Dashboard()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
