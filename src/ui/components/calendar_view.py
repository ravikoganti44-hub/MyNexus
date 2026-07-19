"""
Calendar View widget — monthly grid showing activity due dates as colored category dots.
Click a date cell to reveal the detail panel with that day's activities.
"""
import calendar
from datetime import datetime, timedelta, date
from collections import defaultdict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QListWidget, QListWidgetItem, QSplitter, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QCursor

from src.database.config import get_session
from src.database.operations import ActivityManager
from src.ui.components.premium_button import PremiumButton
from src.ui.styles.tokens import token, spacing

# One dot color per activity category
CATEGORY_COLORS: dict[str, str] = {
    "payment":      "#f59e0b",
    "subscription": "#8b5cf6",
    "maintenance":  "#06b6d4",
    "meeting":      "#3b82f6",
    "task":         "#10b981",
    "health":       "#f43f5e",
    "other":        "#6b7280",
}


class DayCell(QFrame):
    """A single day cell in the calendar grid."""

    clicked = pyqtSignal(date)

    def __init__(self, day_date: date, activities=None,
                 is_today: bool = False, is_other_month: bool = False):
        super().__init__()
        self.day_date       = day_date
        self.activities     = activities or []
        self.is_today       = is_today
        self.is_other_month = is_other_month
        self._build()

    def _build(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(3)

        # Day number
        num = QLabel(str(self.day_date.day))
        if self.is_today:
            num.setStyleSheet(
                f"color: {token('color.text.inverse')}; background-color: {token('color.accent.primary')}; "
                "border-radius: 11px; padding: 2px 6px; font-weight: 700;")
            num.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        elif self.is_other_month:
            num.setStyleSheet(f"color: {token('color.text.tertiary')};")
            num.setFont(QFont("Segoe UI", 11))
        else:
            num.setStyleSheet(f"color: {token('color.text.primary')};")
            num.setFont(QFont("Segoe UI", 11))
        layout.addWidget(num, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Activity dots (up to 5 visible)
        if self.activities and not self.is_other_month:
            dots_row = QWidget()
            dots_layout = QHBoxLayout(dots_row)
            dots_layout.setContentsMargins(0, 0, 0, 0)
            dots_layout.setSpacing(3)

            for act in self.activities[:5]:
                cat = act.category.value if hasattr(act.category, "value") else "other"
                color = CATEGORY_COLORS.get(cat, "#6b7280")
                dot = QFrame()
                dot.setFixedSize(8, 8)
                dot.setStyleSheet(
                    f"background-color: {color}; border-radius: 4px;")
                dot.setToolTip(act.title)
                dots_layout.addWidget(dot)

            if len(self.activities) > 5:
                more = QLabel(f"+{len(self.activities) - 5}")
                more.setFont(QFont("Segoe UI", 7))
                more.setStyleSheet(f"color: {token('color.text.tertiary')};")
                dots_layout.addWidget(more)

            dots_layout.addStretch()
            layout.addWidget(dots_row)

        layout.addStretch()
        self.setLayout(layout)

        # Frame style
        base_bg     = token("color.bg.primary") if self.is_other_month else token("color.bg.secondary")
        if self.is_today:
            border      = f"1px solid {token('color.accent.primary')}"
            hover_border = f"1px solid {token('color.text.primary')}"
            hover_bg    = base_bg
        elif self.is_other_month:
            border      = f"1px solid {token('color.bg.primary')}"
            hover_border = border
            hover_bg    = base_bg
        else:
            border      = f"1px solid {token('color.border.light')}"
            hover_border = border
            hover_bg    = f"{token('color.bg.hover')}"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {base_bg};
                border: {border};
                border-radius: 6px;
            }}
            QFrame:hover {{
                background-color: {hover_bg};
                border: 1px solid {hover_border};
            }}
        """)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(80)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.day_date)
        super().mousePressEvent(event)


class CalendarViewWidget(QWidget):
    """Full-page monthly calendar showing activity due dates."""

    def __init__(self):
        super().__init__()
        today = datetime.now()
        self.current_year  = today.year
        self.current_month = today.month
        self._all_activities = []
        self._setup_ui()
        self.refresh_data()

    # ── UI construction ────────────────────────────────────────────────────────

    def _setup_ui(self):
        main = QVBoxLayout()
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        # ── Header ──────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        title = QLabel("Calendar View")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setObjectName("titleLabel")
        hdr.addWidget(title)
        hdr.addStretch()

        today_btn = PremiumButton("Today", style=PremiumButton.Style.SECONDARY,
                                  icon_name="calendar")
        today_btn.clicked.connect(self._go_today)
        hdr.addWidget(today_btn)

        refresh_btn = PremiumButton("Refresh", style=PremiumButton.Style.FLAT,
                                    icon_name="refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        hdr.addWidget(refresh_btn)

        main.addLayout(hdr)

        # ── Month navigation + legend ────────────────────────────────────────
        nav = QHBoxLayout()
        nav.setSpacing(8)

        self.prev_btn = QPushButton("←")
        self.prev_btn.setFixedSize(36, 36)
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                background: {token("color.bg.secondary")}; color: {token("color.text.primary")};
                border: 1px solid {token("color.border.default")}; border-radius: 8px; font-size: 16px;
            }}
            QPushButton:hover {{ background: {token("color.bg.hover")}; border-color: {token("color.accent.primary")}; }}
        """)
        self.prev_btn.clicked.connect(self._prev_month)

        self.month_label = QLabel()
        self.month_label.setFont(QFont("Segoe UI", int(token("type.scale.h2").replace("px","")), QFont.Weight.Bold))
        self.month_label.setStyleSheet(f"color: {token('color.text.primary')};")
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_label.setMinimumWidth(200)

        self.next_btn = QPushButton("→")
        self.next_btn.setFixedSize(36, 36)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background: {token("color.bg.secondary")}; color: {token("color.text.primary")};
                border: 1px solid {token("color.border.default")}; border-radius: 8px; font-size: 16px;
            }}
            QPushButton:hover {{ background: {token("color.bg.hover")}; border-color: {token("color.accent.primary")}; }}
        """)
        self.next_btn.clicked.connect(self._next_month)

        nav.addWidget(self.prev_btn)
        nav.addWidget(self.month_label)
        nav.addWidget(self.next_btn)
        nav.addSpacing(24)

        # Legend dots
        for cat, color in CATEGORY_COLORS.items():
            dot = QFrame()
            dot.setFixedSize(9, 9)
            dot.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            lbl = QLabel(cat.title())
            lbl.setFont(QFont("Segoe UI", 9))
            lbl.setStyleSheet(f"color: {token('color.text.tertiary')}; font-size: 11px;")
            nav.addWidget(dot)
            nav.addWidget(lbl)
            nav.addSpacing(6)

        nav.addStretch()
        main.addLayout(nav)

        # ── Main content: calendar (left) + detail panel (right) ─────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Calendar column
        cal_container = QWidget()
        cal_v = QVBoxLayout(cal_container)
        cal_v.setContentsMargins(0, 0, 0, 0)
        cal_v.setSpacing(4)

        # Day-of-week header
        dow_frame = QWidget()
        dow_layout = QHBoxLayout(dow_frame)
        dow_layout.setContentsMargins(0, 0, 0, 0)
        dow_layout.setSpacing(4)
        for name in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color: {token('color.accent.primary')}; padding: 4px;")
            dow_layout.addWidget(lbl, 1)
        cal_v.addWidget(dow_frame)

        # Grid
        from PyQt6.QtWidgets import QGridLayout
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(4)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        cal_v.addWidget(self.grid_widget, 1)

        splitter.addWidget(cal_container)

        # Detail panel
        detail_panel = QFrame()
        detail_panel.setObjectName("card")
        detail_panel.setMinimumWidth(200)
        detail_panel.setMaximumWidth(260)
        detail_v = QVBoxLayout(detail_panel)
        detail_v.setContentsMargins(12, 14, 12, 14)
        detail_v.setSpacing(8)

        self.detail_date_lbl = QLabel("Select a date")
        self.detail_date_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.detail_date_lbl.setStyleSheet(f"color: {token('color.text.primary')};")
        self.detail_date_lbl.setWordWrap(True)
        detail_v.addWidget(self.detail_date_lbl)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {token('color.border.default')};")
        detail_v.addWidget(sep)

        self.detail_list = QListWidget()
        self.detail_list.setStyleSheet(f"""
            QListWidget {{ background-color: transparent; border: none; }}
            QListWidget::item {{
                background-color: {token('color.bg.tertiary')}; border-radius: 6px;
                padding: 8px; margin-bottom: 4px; color: {token('color.text.primary')}; font-size: 11px;
            }}
            QListWidget::item:hover {{ background-color: {token('color.border.default')}; }}
        """)
        detail_v.addWidget(self.detail_list)

        self.detail_empty_lbl = QLabel("No activities\ndue on this date.")
        self.detail_empty_lbl.setFont(QFont("Segoe UI", 10))
        self.detail_empty_lbl.setStyleSheet(f"color: {token('color.text.tertiary')};")
        self.detail_empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_empty_lbl.setWordWrap(True)
        detail_v.addWidget(self.detail_empty_lbl)
        detail_v.addStretch()

        splitter.addWidget(detail_panel)
        splitter.setSizes([1000, 240])

        main.addWidget(splitter, 1)
        self.setLayout(main)

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _nav_arrow(symbol: str) -> QPushButton:
        btn = QPushButton(symbol)
        btn.setFixedSize(36, 36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(88,166,255,0.08); color: {token('color.accent.primary')};
                border: 1px solid rgba(88,166,255,0.2); border-radius: 8px; font-size: 14px;
            }
            QPushButton:hover { background: rgba(88,166,255,0.15); }
        """)
        return btn

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _go_today(self):
        today = datetime.now()
        self.current_year  = today.year
        self.current_month = today.month
        self._rebuild_grid()

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._rebuild_grid()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._rebuild_grid()

    # ── Data refresh ───────────────────────────────────────────────────────────

    def refresh_data(self):
        session = get_session()
        try:
            self._all_activities = ActivityManager.get_all_activities(session, active_only=True)
        finally:
            session.close()
        self._rebuild_grid()

    def _activities_by_date(self) -> dict:
        by_date: dict = defaultdict(list)
        for act in self._all_activities:
            if act.next_due_date:
                by_date[act.next_due_date.date()].append(act)
        return by_date

    def _rebuild_grid(self):
        self.month_label.setText(
            datetime(self.current_year, self.current_month, 1).strftime("%B %Y"))

        # Remove previous cells
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        today   = datetime.now().date()
        by_date = self._activities_by_date()

        # calendar.monthcalendar: weeks = list of [Mon..Sun], 0 = not in month
        weeks = calendar.monthcalendar(self.current_year, self.current_month)
        first_day = date(self.current_year, self.current_month, 1)
        last_day  = date(self.current_year, self.current_month,
                         calendar.monthrange(self.current_year, self.current_month)[1])

        for row_idx, week in enumerate(weeks):
            for col_idx, day_num in enumerate(week):
                if day_num == 0:
                    # Fill with neighbouring month day (greyed out)
                    if col_idx < first_day.weekday():
                        d = first_day - timedelta(days=first_day.weekday() - col_idx)
                    else:
                        d = last_day + timedelta(days=col_idx - last_day.weekday())
                    cell = DayCell(d, is_other_month=True)
                else:
                    d    = date(self.current_year, self.current_month, day_num)
                    acts = by_date.get(d, [])
                    cell = DayCell(d, activities=acts, is_today=(d == today))

                cell.clicked.connect(self._on_day_clicked)
                self.grid_layout.addWidget(cell, row_idx, col_idx)
                self.grid_layout.setColumnStretch(col_idx, 1)
                self.grid_layout.setRowStretch(row_idx, 1)

    # ── Detail panel ───────────────────────────────────────────────────────────

    def _on_day_clicked(self, clicked_date: date):
        self.detail_date_lbl.setText(clicked_date.strftime("%A, %B %d, %Y"))
        self.detail_list.clear()

        activities = [a for a in self._all_activities
                      if a.next_due_date and a.next_due_date.date() == clicked_date]

        if activities:
            self.detail_list.setVisible(True)
            self.detail_empty_lbl.setVisible(False)
            for act in activities:
                cat   = act.category.value if hasattr(act.category, "value") else "other"
                color = CATEGORY_COLORS.get(cat, "#6b7280")
                status = "✓" if act.is_completed else "⏳"
                text   = (f"{status}  {act.title}\n"
                          f"   {cat.title()} · {act.recurrence_type.value.title()}")
                item = QListWidgetItem(text)
                item.setForeground(QColor(color))
                self.detail_list.addItem(item)
        else:
            self.detail_list.setVisible(False)
            self.detail_empty_lbl.setVisible(True)
