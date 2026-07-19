"""
Keyboard shortcuts overlay — shown via Ctrl+? or F1.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.styles.tokens import token


_SHORTCUTS = [
    ("Ctrl+K", "Global search across all data"),
    ("Ctrl+?", "Show this shortcuts overlay"),
    ("Ctrl+N", "New activity (when on Activities page)"),
    ("Ctrl+B", "Create backup"),
    ("Ctrl+Q", "Quit application"),
    ("F5", "Refresh current view"),
    ("Esc", "Close dialog / search overlay"),
]


class ShortcutsOverlay(QDialog):
    """Semi-transparent dialog listing keyboard shortcuts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setFixedSize(420, 380)
        self.setStyleSheet(f"QDialog {{ background: {token('color.bg.secondary')}; }}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(12)

        title = QLabel("Keyboard Shortcuts")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {token('color.accent.primary')};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        for key, desc in _SHORTCUTS:
            row = QHBoxLayout()
            badge = QLabel(key)
            badge.setFixedWidth(90)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            badge.setStyleSheet(
                f"background: {token('color.bg.tertiary')}; color: {token('color.text.primary')}; border: 1px solid {token('color.border.default')}; border-radius: 6px; padding: 4px 8px;"
            )
            row.addWidget(badge)
            lbl = QLabel(desc)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color: {token('color.text.secondary')};")
            row.addWidget(lbl, 1)
            layout.addLayout(row)

        layout.addStretch()

        close_hint = QLabel("Press Esc to close")
        close_hint.setFont(QFont("Segoe UI", 8))
        close_hint.setStyleSheet(f"color: {token('color.text.tertiary')};")
        close_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(close_hint)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)
