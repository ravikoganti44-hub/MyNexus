"""
AI Insights Panel widget — displays smart recommendations from NexusAI.
Embeddable in the Dashboard or any other page.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor

from src.core.ai_engine import Insight


# ---------------------------------------------------------------------------
# Single insight card
# ---------------------------------------------------------------------------

class _InsightCard(QFrame):
    """Compact, colour-coded card for a single AI insight."""
    action_clicked = pyqtSignal(str, dict)   # (action_label, action_data)

    _PRIORITY_BORDER = {
        "high":   "#f85149",
        "medium": "#f59e0b",
        "low":    "#3fb950",
    }

    def __init__(self, insight: Insight, parent=None):
        super().__init__(parent)
        self.insight = insight
        border_clr = self._PRIORITY_BORDER.get(insight.priority, "#30363d")

        self.setObjectName("insightCard")
        self.setStyleSheet(f"""
            QFrame#insightCard {{
                background-color: #161b22;
                border: 1px solid {border_clr};
                border-left: 4px solid {border_clr};
                border-radius: 10px;
                padding: 0;
            }}
            QFrame#insightCard:hover {{
                background-color: #1c2128;
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        # Row 1: icon + title + priority badge
        top = QHBoxLayout()
        icon_lbl = QLabel(insight.icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 14))
        icon_lbl.setFixedWidth(24)
        top.addWidget(icon_lbl)

        title_lbl = QLabel(insight.title)
        title_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #e6edf3; border: none; background: transparent;")
        title_lbl.setWordWrap(True)
        top.addWidget(title_lbl, 1)

        badge = QLabel(insight.priority.upper())
        badge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedWidth(56)
        badge.setFixedHeight(20)
        badge.setStyleSheet(f"""
            color: {border_clr};
            background: rgba({self._hex_to_rgb(border_clr)}, 0.12);
            border: 1px solid {border_clr};
            border-radius: 10px;
            padding: 0 6px;
        """)
        top.addWidget(badge)
        layout.addLayout(top)

        # Row 2: description
        desc = QLabel(insight.description)
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet("color: #8b949e; border: none; background: transparent;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Row 3: action button (optional)
        if insight.action_label:
            action_btn = QPushButton(f"→ {insight.action_label}")
            action_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            action_btn.setFixedHeight(26)
            action_btn.setStyleSheet(f"""
                QPushButton {{
                    color: {border_clr};
                    background: transparent;
                    border: none;
                    text-align: left;
                    padding: 0;
                }}
                QPushButton:hover {{
                    text-decoration: underline;
                }}
            """)
            action_btn.clicked.connect(
                lambda: self.action_clicked.emit(
                    insight.action_label, insight.action_data))
            layout.addWidget(action_btn)

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> str:
        h = hex_color.lstrip("#")
        return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

class AIInsightsPanel(QWidget):
    """Panel showing a list of AI-generated insights.  Emits signals when
    the user clicks an action so the parent can navigate to the relevant page."""
    insight_action = pyqtSignal(str, dict)   # (action_label, action_data)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header
        hdr = QHBoxLayout()
        icon = QLabel("🤖")
        icon.setFont(QFont("Segoe UI Emoji", 16))
        hdr.addWidget(icon)
        title = QLabel("AI Insights")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #a78bfa;")
        hdr.addWidget(title)

        ai_badge = QLabel("SMART")
        ai_badge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        ai_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ai_badge.setFixedWidth(52)
        ai_badge.setFixedHeight(20)
        ai_badge.setStyleSheet("""
            color: #a78bfa;
            background: rgba(167, 139, 250, 0.12);
            border: 1px solid rgba(167, 139, 250, 0.3);
            border-radius: 10px;
        """)
        hdr.addWidget(ai_badge)
        hdr.addStretch()

        self.count_label = QLabel("")
        self.count_label.setFont(QFont("Segoe UI", 9))
        self.count_label.setStyleSheet("color: #6b7280;")
        hdr.addWidget(self.count_label)
        layout.addLayout(hdr)

        # Cards container
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(8)
        layout.addLayout(self.cards_layout)

    # ── Public API ────────────────────────────────────────────────────────

    def set_insights(self, insights: list[Insight]):
        """Replace all existing cards with new insights."""
        # Clear old
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not insights:
            empty = QLabel("✅  All systems look good — no issues detected.")
            empty.setFont(QFont("Segoe UI", 10))
            empty.setStyleSheet("color: #3fb950; padding: 8px 0;")
            self.cards_layout.addWidget(empty)
            self.count_label.setText("")
            return

        self.count_label.setText(f"{len(insights)} insight{'s' if len(insights) != 1 else ''}")

        for insight in insights[:12]:          # cap visible cards
            card = _InsightCard(insight)
            card.action_clicked.connect(
                lambda lbl, data: self.insight_action.emit(lbl, data))
            self.cards_layout.addWidget(card)
