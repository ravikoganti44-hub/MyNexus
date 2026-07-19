"""
Frameless Fluent-style window chrome for MyNexus.

Provides:
- TitleBar: custom title bar with drag via startSystemMove()
- FramelessWindowMixin: mixin to add frameless behavior to a QWidget/QMainWindow
- QSizeGrip resize handle
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QSizeGrip
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from src.ui.styles.tokens import token


class TitleBar(QWidget):
    """Custom frameless title bar using native system move/resize."""

    def __init__(self, parent_window, parent=None):
        super().__init__(parent)
        self._parent_window = parent_window
        self.setFixedHeight(40)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 12, 8)
        layout.setSpacing(12)

        # Brand + title
        brand = QLabel("MyNexus")
        brand.setStyleSheet(
            f"color: {token('color.accent.primary')}; "
            f"font-size: 12px; font-weight: 700; letter-spacing: 0.5px;"
        )
        layout.addWidget(brand)

        separator = QLabel("•")
        separator.setStyleSheet(
            f"color: {token('color.text.muted')}; font-size: 12px;"
        )
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
            f"border-radius: 8px; padding: 6px 10px; font-size: 14px; font-weight: 600; }} "
            f"QPushButton:hover {{ background: {token('color.bg.tertiary')}; color: {token('color.text.primary')}; }}"
        )
        btn = QPushButton("✕")
        btn.setFixedSize(32, 32)
        btn.setStyleSheet(ctrl_style)
        btn.setToolTip("Close")
        btn.clicked.connect(parent_window.close)
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
            handle = self._parent_window.windowHandle()
            if handle is None:
                return super().mousePressEvent(event)
            pos = event.position().toPoint()
            rect = self.rect()
            # Edge resize handling
            if pos.y() <= 8:
                edge = Qt.Edge.TopEdge
                if pos.x() <= 8:
                    edge = Qt.Edge.TopEdge | Qt.Edge.LeftEdge
                elif pos.x() >= rect.width() - 8:
                    edge = Qt.Edge.TopEdge | Qt.Edge.RightEdge
                try:
                    handle.startSystemResize(edge)
                    return
                except Exception:
                    pass
            else:
                try:
                    handle.startSystemMove()
                    event.accept()
                    return
                except Exception:
                    pass
        return super().mousePressEvent(event)


class FramelessWindowMixin:
    """Mixin that adds frameless behavior to a QWidget/QMainWindow."""

    def _init_frameless(self):
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self._title_bar = TitleBar(self, self)
        self._title_bar.raise_()

    def _setup_frameless_layout(self, content_widget, parent_layout):
        if not hasattr(self, "_title_bar"):
            self._init_frameless()
        parent_layout.setContentsMargins(0, 0, 0, 0)
        parent_layout.setSpacing(0)
        parent_layout.addWidget(self._title_bar)
        parent_layout.addWidget(content_widget, 1)

    def _add_size_grip(self, parent_layout):
        grip = QSizeGrip(self)
        grip.setFixedSize(12, 12)
        parent_layout.addWidget(
            grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight
        )


__all__ = ["TitleBar", "FramelessWindowMixin"]
