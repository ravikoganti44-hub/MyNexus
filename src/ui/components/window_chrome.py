"""
Frameless Fluent-style window chrome for MyNexus.

Wraps an existing QMainWindow with:
- custom title bar with traffic-light window controls
- native drag support
- QSizeGrip resize handle
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSizeGrip
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QMouseEvent

from src.ui.styles.tokens import token
from src.ui.styles.icon_manager import IconManager


class TitleBar(QWidget):
    """Custom frameless title bar."""

    def __init__(self, parent_window: QWidget, parent: QWidget | None = None):
        super().__init__(parent)
        self._parent_window = parent_window
        self._start = None
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 8, 4)
        layout.setSpacing(12)

        # Brand + title
        brand = QLabel("MyNexus")
        brand.setStyleSheet(
            f"color: {token('color.accent.primary')}; "
            f"font-size: 12px; font-weight: 700; letter-spacing: 0.4px;"
        )
        layout.addWidget(brand)

        separator = QLabel("•")
        separator.setStyleSheet(f"color: {token('color.text.muted')}; font-size: 12px;")
        layout.addWidget(separator)

        title = QLabel(parent_window.windowTitle())
        title.setObjectName("windowStatusLabel")
        title.setStyleSheet(
            f"color: {token('color.text.secondary')}; font-size: 11px;"
        )
        layout.addWidget(title, 1)

        # Window controls
        ctrl_style = (
            f"QPushButton {{ background: transparent; border: none; color: {token('color.text.secondary')}; "
            f"border-radius: 8px; padding: 4px 8px; font-size: 12px; }} "
            f"QPushButton:hover {{ background: {token('color.bg.tertiary')}; color: {token('color.text.primary')}; }}"
        )
        for label, slot in (("✕", parent_window.close),):
            btn = QPushButton(label)
            btn.setFixedSize(28, 28)
            btn.setStyleSheet(ctrl_style)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

    def mouseDoubleClickEvent(self, event: QMouseEvent):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._parent_window:
            if self._parent_window.isMaximized():
                self._parent_window.showNormal()
            else:
                self._parent_window.showMaximized()
        return super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._parent_window:
            self._start = event.globalPosition().toPoint() - self._parent_window.frameGeometry().topLeft()
            if event.position().y() <= 8:
                self._parent_window.windowHandle().startSystemResize(Qt.Edge.TopEdge)
            else:
                event.accept()
            return
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):  # noqa: N802
        if getattr(self, "_start", None) and self._parent_window:
            self._parent_window.move(
                event.globalPosition().toPoint() - self._start
            )
            event.accept()
            return
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):  # noqa: N802
        self._start = None
        return super().mouseReleaseEvent(event)


class FramelessFluentWindow(QWidget):
    """Mixing frameless window chrome onto a QMainWindow."""

    def __init__(self, main_window):
        super().__init__()
        self._main = main_window

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._title_bar = TitleBar(main_window, self)
        root.addWidget(self._title_bar)

        host = QWidget()
        host_layout = QVBoxLayout(host)
        host_layout.setContentsMargins(0, 0, 0, 0)
        host_layout.setSpacing(0)
        host_layout.addWidget(main_window.centralWidget())
        sb = main_window.statusBar()
        if sb is not None:
            sb.setParent(host)
            host_layout.addWidget(sb)
        root.addWidget(host, 1)

        grip = QSizeGrip(self)
        grip.setFixedSize(12, 12)
        root.addWidget(grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

    def sizeHint(self) -> QSize:
        return self._main.sizeHint()


__all__ = ["TitleBar", "FramelessFluentWindow"]
