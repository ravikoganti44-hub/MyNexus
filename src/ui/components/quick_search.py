"""
Global quick-search overlay (Ctrl+K / Ctrl+F system-wide search).
Searches across activities, connected apps, documents, and budget entries.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QListWidget, QListWidgetItem, QWidget, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QKeyEvent, QShortcut, QKeySequence

from src.database.config import get_session
from src.database.models import Activity, ConnectedApplication, Document


class QuickSearchDialog(QDialog):
    """Overlay search dialog triggered by Ctrl+K."""

    def __init__(self, parent=None, on_navigate=None):
        super().__init__(parent)
        self._on_navigate = on_navigate
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(560, 420)
        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(250)
        self._debounce.timeout.connect(self._do_search)
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: #161b22; border: 1px solid #30363d; border-radius: 14px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 12)
        card_layout.setSpacing(10)

        # Search input
        self._input = QLineEdit()
        self._input.setPlaceholderText("Search activities, apps, documents…")
        self._input.setMinimumHeight(40)
        self._input.setFont(QFont("Segoe UI", 12))
        self._input.setStyleSheet(
            "QLineEdit { background: #0d1117; color: #fff; border: 1px solid #30363d; "
            "border-radius: 10px; padding: 8px 14px; } "
            "QLineEdit:focus { border-color: #58a6ff; }"
        )
        self._input.textChanged.connect(lambda: self._debounce.start())
        card_layout.addWidget(self._input)

        # Hint
        hint = QLabel("Tip: Press Enter to navigate, Esc to close")
        hint.setFont(QFont("Segoe UI", 8))
        hint.setStyleSheet("color: #6b7280;")
        card_layout.addWidget(hint)

        # Results
        self._results = QListWidget()
        self._results.setStyleSheet(
            "QListWidget { background: transparent; border: none; } "
            "QListWidget::item { background: #21262d; border-radius: 8px; "
            "margin: 2px 0; padding: 10px 12px; color: #e8eefb; } "
            "QListWidget::item:selected { background: #30363d; border: 1px solid #58a6ff; }"
        )
        self._results.setFont(QFont("Segoe UI", 10))
        self._results.itemDoubleClicked.connect(self._on_item_activated)
        card_layout.addWidget(self._results, 1)

        outer.addWidget(card)
        self._input.setFocus()

    def _do_search(self):
        query = self._input.text().strip()
        self._results.clear()
        if len(query) < 2:
            return

        session = get_session()
        try:
            term = f"%{query}%"

            # Activities
            activities = session.query(Activity).filter(
                Activity.title.ilike(term) | Activity.description.ilike(term)
            ).limit(8).all()
            for a in activities:
                item = QListWidgetItem(f"📋  {a.title}")
                item.setData(Qt.ItemDataRole.UserRole, ("activity", a.id))
                self._results.addItem(item)

            # Connected apps
            apps = session.query(ConnectedApplication).filter(
                ConnectedApplication.name.ilike(term) |
                ConnectedApplication.app_name.ilike(term)
            ).limit(8).all()
            for app in apps:
                item = QListWidgetItem(f"🔗  {app.name} — {app.app_name or ''}")
                item.setData(Qt.ItemDataRole.UserRole, ("connected_app", app.id))
                self._results.addItem(item)

            # Documents
            docs = session.query(Document).filter(
                Document.title.ilike(term) |
                Document.description.ilike(term) |
                Document.tags.ilike(term)
            ).limit(8).all()
            for d in docs:
                item = QListWidgetItem(f"📁  {d.title}")
                item.setData(Qt.ItemDataRole.UserRole, ("document", d.id))
                self._results.addItem(item)

            if self._results.count() == 0:
                item = QListWidgetItem("No results found")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self._results.addItem(item)
        finally:
            session.close()

    def _on_item_activated(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data and self._on_navigate:
            self._on_navigate(data[0], data[1])
        self.accept()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            current = self._results.currentItem()
            if current:
                self._on_item_activated(current)
        elif event.key() == Qt.Key.Key_Down:
            row = self._results.currentRow()
            if row < self._results.count() - 1:
                self._results.setCurrentRow(row + 1)
        elif event.key() == Qt.Key.Key_Up:
            row = self._results.currentRow()
            if row > 0:
                self._results.setCurrentRow(row - 1)
        else:
            super().keyPressEvent(event)
