"""
In-app notification center – a bell icon that shows unread count
and a dropdown panel listing recent notifications.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor

from src.database.config import get_session
from src.database.operations import NotificationManager
from src.ui.styles.tokens import token


class NotificationBell(QPushButton):
    """A small bell button with an unread badge, suitable for placing in a header."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("🔔")
        self.setFixedSize(40, 40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI Emoji", 14))
        self._badge_count = 0
        self._panel: NotificationPanel | None = None
        self.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 8px; }"
            "QPushButton:hover { background: rgba(138,174,252,0.1); }"
        )
        self.clicked.connect(self._toggle_panel)

        # Auto-refresh every 60 seconds
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(60_000)
        QTimer.singleShot(500, self.refresh)

    def refresh(self):
        session = get_session()
        try:
            unread = NotificationManager.get_unread_notifications(session, limit=50)
            self._badge_count = len(unread)
            self.setText(f"🔔 {self._badge_count}" if self._badge_count else "🔔")
            self.setToolTip(f"{self._badge_count} unread notifications" if self._badge_count else "No new notifications")
        finally:
            session.close()

    def _toggle_panel(self):
        if self._panel and self._panel.isVisible():
            self._panel.hide()
            return
        self._panel = NotificationPanel(self.window())
        # Position below the bell, aligned to the right
        pos = self.mapToGlobal(QPoint(self.width() - 340, self.height() + 4))
        self._panel.move(pos)
        self._panel.show()
        self._panel.raise_()


class NotificationPanel(QFrame):
    """Dropdown panel showing recent notifications."""

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setFixedSize(360, 380)
        self.setStyleSheet(
            f"NotificationPanel {{ background-color: {token('color.bg.secondary')}; border: 1px solid {token('color.border.default')}; "
            f"border-radius: 12px; }}"
        )
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 8)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        title = QLabel("Notifications")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {token('color.text.primary')};")
        header.addWidget(title)
        header.addStretch()

        mark_all = QPushButton("Mark all read")
        mark_all.setCursor(Qt.CursorShape.PointingHandCursor)
        mark_all.setFont(QFont("Segoe UI", 9))
        mark_all.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {token('color.accent.primary')}; border: none; }}"
            "QPushButton:hover { text-decoration: underline; }"
        )
        mark_all.clicked.connect(self._mark_all_read)
        header.addWidget(mark_all)
        layout.addLayout(header)

        # Scroll area for items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        container = QWidget()
        self._items_layout = QVBoxLayout(container)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSpacing(4)
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        self._load_notifications()

    def _load_notifications(self):
        session = get_session()
        try:
            notifs = NotificationManager.get_unread_notifications(session, limit=20)
            if not notifs:
                empty = QLabel("No new notifications")
                empty.setFont(QFont("Segoe UI", 10))
                empty.setStyleSheet(f"color: {token('color.text.tertiary')};")
                empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._items_layout.addWidget(empty)
                return

            for n in notifs:
                card = QFrame()
                card.setStyleSheet(
                    f"QFrame {{ background: {token('color.bg.tertiary')}; border-radius: 8px; padding: 8px; }}"
                )
                row = QVBoxLayout(card)
                row.setContentsMargins(10, 8, 10, 8)
                row.setSpacing(2)
                title = QLabel(n.title or "Notification")
                title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                title.setStyleSheet(f"color: {token('color.text.primary')};")
                row.addWidget(title)
                msg = QLabel(n.message or "")
                msg.setFont(QFont("Segoe UI", 9))
                msg.setStyleSheet(f"color: {token('color.text.secondary')};")
                msg.setWordWrap(True)
                row.addWidget(msg)
                ts = QLabel(n.sent_at.strftime("%b %d, %H:%M") if n.sent_at else "")
                ts.setFont(QFont("Segoe UI", 8))
                ts.setStyleSheet(f"color: {token('color.text.muted')};")
                row.addWidget(ts)
                self._items_layout.addWidget(card)
        finally:
            session.close()

        self._items_layout.addStretch()

    def _mark_all_read(self):
        session = get_session()
        try:
            notifs = NotificationManager.get_unread_notifications(session, limit=200)
            for n in notifs:
                NotificationManager.mark_as_read(session, n.id)
        finally:
            session.close()
        # Clear UI
        while self._items_layout.count():
            child = self._items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        empty = QLabel("All caught up!")
        empty.setFont(QFont("Segoe UI", 10))
        empty.setStyleSheet(f"color: {token('color.semantic.success')};")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._items_layout.addWidget(empty)
