"""
Dashboard widget with enhanced visualizations and premium design
"""
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QScrollArea, QProgressBar, QCalendarWidget,
    QTabWidget, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSlot, QDate, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPixmap, QImage, QBrush
from PyQt6.QtGui import QFontMetrics

from src.database.config import get_session
from src.database.operations import ActivityManager, ConnectedApplicationManager
from src.ui.components.stat_card import StatCard
from src.ui.components.premium_button import PremiumButton
from src.ui.styles.icon_manager import IconManager
from src.ui.components.ai_insights_panel import AIInsightsPanel
from src.ui.styles.tokens import token, spacing
from src.ui.styles.motion import duration as motion_duration
from src.core.ai_engine import NexusAI
from collections import Counter
from datetime import datetime, timedelta, date as _date


_ICON_FOR_STAT = {
    "Total Activities": "dashboard",
    "Due This Week": "calendar_view",
    "Overdue": "alert",
    "Completed Today": "check",
}

def _stat_icon(name: str, fallback: str) -> str:
    return _ICON_FOR_STAT.get(name, fallback)


class CollapsibleSection(QWidget):
    """Chevron-collapsible section wrapper for dashboard panels."""

    def __init__(self, title: str, widget: QWidget, parent=None):
        super().__init__(parent)
        self._widget = widget
        self._collapsed = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        self.chevron = QLabel("▶")
        self.chevron.setFixedWidth(16)
        self.chevron.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header_layout.addWidget(self.chevron)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        root.addWidget(header)

        root.addWidget(widget)

        header.setCursor(Qt.CursorShape.PointingHandCursor)
        header.mousePressEvent = self._toggle

    def _toggle(self, event=None):
        self._collapsed = not self._collapsed
        self._widget.setVisible(not self._collapsed)
        self.chevron.setText("▼" if not self._collapsed else "▶")


class DashboardWidget(QWidget):
    """Dashboard overview widget with premium design"""
    view_all_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.refresh_data()
    
    def _setup_ui(self):
        """Setup dashboard UI with premium design"""
        # Main outer layout
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {token("color.bg.primary")};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {token("color.bg.primary")};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {token("color.border.default")};
                border-radius: 6px;
                min-height: 50px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {token("color.border.light")};
            }}
        """)
        
        # Create container widget for scroll area
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        
        refresh_btn = PremiumButton("Refresh", style=PremiumButton.Style.SECONDARY, icon_name="refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        main_layout.addLayout(header_layout)

        # Quick-search hint bar
        search_hint = QLabel("  🔍  Press  Ctrl+K  to search across all your data")
        search_hint.setFont(QFont("Segoe UI", 9))
        search_hint.setFixedHeight(32)
        search_hint.setStyleSheet(
            f"background: {token('color.bg.secondary')}; color: {token('color.text.tertiary')}; border: 1px solid {token('color.border.default')}; "
            "border-radius: 8px; padding: 0 12px;"
        )
        main_layout.addWidget(search_hint)

        # ── AI Greeting ────────────────────────────────────────────────────
        self.ai_greeting = QLabel("")
        self.ai_greeting.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        self.ai_greeting.setStyleSheet(
            f"color: {token('color.accent.light')}; padding: 6px 0;"
        )
        self.ai_greeting.setWordWrap(True)
        main_layout.addWidget(self.ai_greeting)
        
        # Stats row with premium cards
        stats_layout = QGridLayout()
        stats_layout.setSpacing(spacing("space.gap.md"))
        
        # Create stat cards with icons and colors
        self.stat_total = StatCard("Total Activities", "0", "📊", token("color.accent.primary"))
        self.stat_due = StatCard("Due This Week", "0", "📅", token("color.semantic.warning"))
        self.stat_overdue = StatCard("Overdue", "0", "⚠️", token("color.semantic.error"))
        self.stat_completed = StatCard("Completed Today", "0", "✓", token("color.semantic.success"))
        
        # add placeholders; we'll arrange in _arrange_stats()
        stats_layout.addWidget(self.stat_total, 0, 0)
        stats_layout.addWidget(self.stat_due, 0, 1)
        stats_layout.addWidget(self.stat_overdue, 0, 2)
        stats_layout.addWidget(self.stat_completed, 0, 3)
        
        main_layout.addLayout(stats_layout)
        
        def _sep():
            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background-color: {token('color.border.default')};")
            return sep
        
        def _section_title(text: str) -> QLabel:
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color: {token('color.text.primary')};")
            return lbl
        
        main_layout.addWidget(_sep())
        
        # Due Soon section
        due_title = _section_title("Due This Week")
        main_layout.addWidget(due_title)
        
        # Table for due activities
        self.due_table = QTableWidget()
        self.due_table.setColumnCount(5)
        self.due_table.setHorizontalHeaderLabels(["Activity", "Category", "Due Date", "Days Left", "Status"])
        self.due_table.setMinimumHeight(200)
        self.due_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.due_table.setAlternatingRowColors(True)
        self._style_table(self.due_table)
        main_layout.addWidget(self.due_table, 1)
        
        main_layout.addWidget(_sep())
        
        # Overdue section
        overdue_title = _section_title("Overdue Activities")
        main_layout.addWidget(overdue_title)
        
        # Table for overdue activities
        self.overdue_table = QTableWidget()
        self.overdue_table.setColumnCount(5)
        self.overdue_table.setHorizontalHeaderLabels(["Activity", "Category", "Due Date", "Days Overdue", "Status"])
        self.overdue_table.setMinimumHeight(150)
        self.overdue_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.overdue_table.setAlternatingRowColors(True)
        self._style_table(self.overdue_table)
        main_layout.addWidget(self.overdue_table, 1)
        
        # Connected Applications quick access
        apps_title = _section_title("Connected Applications")
        main_layout.addWidget(apps_title)
        
        # Apps frame
        apps_frame = QFrame()
        apps_frame.setObjectName("card")
        apps_layout = QHBoxLayout()
        apps_layout.setContentsMargins(16, 12, 16, 12)
        apps_layout.setSpacing(12)
        
        # Apps will be populated here
        self.connected_apps_widget = apps_layout
        apps_frame.setLayout(apps_layout)
        main_layout.addWidget(apps_frame)

        main_layout.addWidget(_sep())
        
        # Streak indicator
        streak_frame = QFrame()
        streak_frame.setObjectName("card")
        streak_inner = QHBoxLayout(streak_frame)
        streak_inner.setContentsMargins(16, 12, 16, 12)
        streak_inner.setSpacing(24)

        self.streak_current_label = QLabel("0 days")
        self.streak_current_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.streak_current_label.setStyleSheet(f"color: {token('color.semantic.warning')};")
        streak_inner.addWidget(self.streak_current_label)

        streak_desc = QLabel("Current streak — consecutive days with at least one completed activity")
        streak_desc.setFont(QFont("Segoe UI", 10))
        streak_desc.setStyleSheet(f"color: {token('color.text.secondary')};")
        streak_desc.setWordWrap(True)
        streak_inner.addWidget(streak_desc, 1)

        self.streak_best_label = QLabel("Best: 0 days")
        self.streak_best_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.streak_best_label.setStyleSheet(f"color: {token('color.semantic.success')};")
        streak_inner.addWidget(self.streak_best_label)
        main_layout.addWidget(streak_frame)

        main_layout.addWidget(_sep())

        # Weekly Summary
        weekly_title = _section_title("This Week at a Glance")
        main_layout.addWidget(weekly_title)

        weekly_frame = QFrame()
        weekly_frame.setObjectName("card")
        weekly_grid = QGridLayout(weekly_frame)
        weekly_grid.setContentsMargins(16, 12, 16, 12)
        weekly_grid.setSpacing(14)

        self.weekly_completed = QLabel("0")
        self.weekly_completed.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.weekly_completed.setStyleSheet(f"color: {token('color.semantic.success')};")
        wc_label = QLabel("Completed this week")
        wc_label.setStyleSheet(f"color: {token('color.text.secondary')}; font-size: 10px;")
        weekly_grid.addWidget(self.weekly_completed, 0, 0, Qt.AlignmentFlag.AlignCenter)
        weekly_grid.addWidget(wc_label, 1, 0, Qt.AlignmentFlag.AlignCenter)

        self.weekly_new = QLabel("0")
        self.weekly_new.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.weekly_new.setStyleSheet(f"color: {token('color.accent.primary')};")
        wn_label = QLabel("New activities")
        wn_label.setStyleSheet(f"color: {token('color.text.secondary')}; font-size: 10px;")
        weekly_grid.addWidget(self.weekly_new, 0, 1, Qt.AlignmentFlag.AlignCenter)
        weekly_grid.addWidget(wn_label, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.weekly_overdue = QLabel("0")
        self.weekly_overdue.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.weekly_overdue.setStyleSheet(f"color: {token('color.semantic.error')};")
        wo_label = QLabel("Became overdue")
        wo_label.setStyleSheet(f"color: {token('color.text.secondary')}; font-size: 10px;")
        weekly_grid.addWidget(self.weekly_overdue, 0, 2, Qt.AlignmentFlag.AlignCenter)
        weekly_grid.addWidget(wo_label, 1, 2, Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(weekly_frame)

        main_layout.addWidget(_sep())

        # Recent Activity Feed
        feed_title = _section_title("Recent Activity")
        main_layout.addWidget(feed_title)

        self.feed_frame = QFrame()
        self.feed_frame.setObjectName("card")
        self.feed_layout = QVBoxLayout(self.feed_frame)
        self.feed_layout.setContentsMargins(16, 10, 16, 10)
        self.feed_layout.setSpacing(6)
        main_layout.addWidget(self.feed_frame)

        main_layout.addWidget(_sep())

        # AI Insights Panel
        self.ai_panel = AIInsightsPanel()
        self.ai_panel.insight_action.connect(self._on_insight_action)
        main_layout.addWidget(self.ai_panel)
        
        main_layout.addStretch()
        scroll_content.setLayout(main_layout)
        
        # Add scroll area to outer layout
        outer_layout.addWidget(scroll_area)
        self.setLayout(outer_layout)
    
    def _style_table(self, table: QTableWidget):
        """Style a table widget with premium design"""
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        table.verticalHeader().setVisible(False)
        table.setSelectionMode(table.SelectionMode.SingleSelection)
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setWordWrap(False)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {token("color.bg.secondary")};
                alternate-background-color: {token("color.bg.tertiary")};
                gridline-color: {token("color.border.default")};
                border: 1px solid {token("color.border.default")};
                border-radius: 8px;
            }}
            QTableWidget::item {{
                padding: 12px 10px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {token("color.accent.primary")};
                color: {token("color.text.primary")};
            }}
            QHeaderView::section {{
                background-color: {token("color.bg.tertiary")};
                color: {token("color.text.primary")};
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid {token("color.border.default")};
                font-weight: {token("type.weight.bold")};
                font-size: 12px;
            }}
        """)

    def resizeEvent(self, event):
        """Adjust dashboard layouts responsively when container is resized."""
        try:
            self._arrange_stats()
        except Exception:
            pass
        return super().resizeEvent(event)

    def _arrange_stats(self):
        """Arrange stat cards based on available width."""
        # Determine number of columns based on width
        width = self.width()
        if width >= 1400:
            cols = 4
        elif width >= 1000:
            cols = 3
        elif width >= 700:
            cols = 2
        else:
            cols = 1

        # Reparent widgets into grid positions
        parent_layout = self.stat_total.parentWidget().layout()
        if isinstance(parent_layout, QGridLayout):
            # remove all widgets from grid
            widgets = [self.stat_total, self.stat_due, self.stat_overdue, self.stat_completed]
            for i, w in enumerate(widgets):
                # clear previous position
                parent_layout.removeWidget(w)

            for idx, w in enumerate(widgets):
                r = idx // cols
                c = idx % cols
                parent_layout.addWidget(w, r, c)
    
    @pyqtSlot()
    def refresh_data(self):
        """Refresh dashboard data"""
        session = get_session()
        try:
            # Get statistics
            all_activities = ActivityManager.get_all_activities(session)
            due_activities = ActivityManager.get_due_activities(session, days_ahead=7)
            overdue_activities = ActivityManager.get_overdue_activities(session)
            
            # Calculate completed today
            today = datetime.now().date()
            completed_today = sum(1 for a in all_activities if a.is_completed and
                                 a.updated_at and a.updated_at.date() == today)
            
            # Update stat cards
            self.stat_total.set_value(str(len(all_activities)))
            self.stat_due.set_value(str(len(due_activities)))
            self.stat_overdue.set_value(str(len(overdue_activities)))
            self.stat_completed.set_value(str(completed_today))
            
            # Populate tables
            self._populate_due_table(due_activities)
            self._populate_overdue_table(overdue_activities)
            
            # Populate connected apps quick access
            self._populate_connected_apps()

            # ── Streaks ────────────────────────────────────────────────
            self._update_streaks(all_activities, session)

            # ── Weekly summary ─────────────────────────────────────────
            self._update_weekly_summary(all_activities, overdue_activities)

            # ── Recent feed ────────────────────────────────────────────
            self._update_recent_feed(all_activities)

            # ── AI Greeting & Insights ─────────────────────────────────
            try:
                self.ai_greeting.setText(NexusAI.generate_daily_greeting(session))
                insights = NexusAI.generate_all_insights(session)
                self.ai_panel.set_insights(insights)
            except Exception:
                self.ai_greeting.setText("")
            
        finally:
            session.close()

    # ── Streak calculation ─────────────────────────────────────────────
    def _update_streaks(self, all_activities, session):
        """Calculate current and best streak of consecutive completion days."""
        from src.database.models import ActivityCompletion
        completions = session.query(ActivityCompletion).order_by(
            ActivityCompletion.completed_at.desc()
        ).all()
        if not completions:
            self.streak_current_label.setText("0 days")
            self.streak_best_label.setText("Best: 0 days")
            return

        # Unique dates with completions
        comp_dates = sorted({c.completed_at.date() for c in completions}, reverse=True)
        # Current streak (must include today or yesterday)
        current = 0
        check_day = _date.today()
        if comp_dates and comp_dates[0] < check_day - timedelta(days=1):
            current = 0
        else:
            for d in comp_dates:
                if d == check_day or d == check_day - timedelta(days=1):
                    current += 1
                    check_day = d - timedelta(days=1)
                else:
                    break

        # Best streak
        best = 1
        streak = 1
        sorted_asc = sorted(comp_dates)
        for i in range(1, len(sorted_asc)):
            if sorted_asc[i] == sorted_asc[i - 1] + timedelta(days=1):
                streak += 1
                best = max(best, streak)
            else:
                streak = 1

        self.streak_current_label.setText(f"{current} day{'s' if current != 1 else ''}")
        self.streak_best_label.setText(f"Best: {best} day{'s' if best != 1 else ''}")

    # ── Weekly summary ─────────────────────────────────────────────────
    def _update_weekly_summary(self, all_activities, overdue_activities):
        week_start = datetime.now() - timedelta(days=7)
        completed_week = sum(
            1 for a in all_activities
            if a.is_completed and a.updated_at and a.updated_at >= week_start
        )
        new_week = sum(
            1 for a in all_activities
            if a.created_at and a.created_at >= week_start
        )
        overdue_week = sum(
            1 for a in overdue_activities
            if a.next_due_date and a.next_due_date >= week_start
        )
        self.weekly_completed.setText(str(completed_week))
        self.weekly_new.setText(str(new_week))
        self.weekly_overdue.setText(str(overdue_week))

    # ── Recent activity feed ───────────────────────────────────────────
    def _update_recent_feed(self, all_activities):
        # Clear old items
        while self.feed_layout.count():
            item = self.feed_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Build feed from recent updates (last 10)
        recent = sorted(
            [a for a in all_activities if a.updated_at],
            key=lambda a: a.updated_at, reverse=True,
        )[:10]
        if not recent:
            empty = QLabel("No recent activity yet.")
            empty.setStyleSheet("color: #8b949e; font-size: 11px;")
            self.feed_layout.addWidget(empty)
            return

        for act in recent:
            status_icon = "✅" if act.is_completed else ("⚠️" if act.next_due_date and act.next_due_date < datetime.now() else "📌")
            ts = act.updated_at.strftime("%b %d, %H:%M")
            lbl = QLabel(f"{status_icon}  <b>{act.title}</b>  —  <span style='color:#8b949e;'>{ts}</span>")
            lbl.setTextFormat(Qt.TextFormat.RichText)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("padding: 4px 0;")
            self.feed_layout.addWidget(lbl)
    
    def _populate_due_table(self, activities):
        """Populate due activities table"""
        self.due_table.setRowCount(len(activities))
        
        now = datetime.now()
        for row, activity in enumerate(activities):
            # Activity name (elide for display, keep full tooltip)
            fm = QFontMetrics(self.due_table.font())
            elided_title = fm.elidedText(activity.title or "", Qt.TextElideMode.ElideRight, 260)
            name_item = QTableWidgetItem(elided_title)
            name_item.setToolTip(activity.title or "")
            self.due_table.setItem(row, 0, name_item)
            
            # Category
            cat_text = activity.category.value.title()
            cat_elided = fm.elidedText(cat_text, Qt.TextElideMode.ElideRight, 120)
            category_item = QTableWidgetItem(cat_elided)
            category_item.setToolTip(cat_text)
            self.due_table.setItem(row, 1, category_item)
            
            # Due date
            due_date_str = activity.next_due_date.strftime("%Y-%m-%d")
            date_item = QTableWidgetItem(due_date_str)
            self.due_table.setItem(row, 2, date_item)
            
            # Days left
            days_left = (activity.next_due_date - now).days
            days_item = QTableWidgetItem(str(max(0, days_left)))
            self.due_table.setItem(row, 3, days_item)
            
            # Status
            status_text = "Completed" if activity.is_completed else "Pending"
            status_item = QTableWidgetItem(status_text)
            try:
                if activity.is_completed:
                    icon = IconManager.get_icon('check', size=16, color='#3fb950')
                    status_item.setIcon(icon)
                    status_item.setForeground(QColor('#3fb950'))
                    bg = QColor(35, 150, 80)
                    bg.setAlpha(30)
                    status_item.setBackground(bg)
                else:
                    icon = IconManager.get_icon('warning', size=16, color='#f59e0b')
                    status_item.setIcon(icon)
                    status_item.setForeground(QColor('#f59e0b'))
                    bg = QColor(245, 158, 11)
                    bg.setAlpha(22)
                    status_item.setBackground(bg)
            except Exception:
                # Fallback: color only
                if activity.is_completed:
                    status_item.setForeground(QColor('#3fb950'))
                else:
                    status_item.setForeground(QColor('#f59e0b'))

            self.due_table.setItem(row, 4, status_item)

            # Ensure rows do not wrap and show ellipsis where needed (handled by setWordWrap(False))
    
    def _populate_overdue_table(self, activities):
        """Populate overdue activities table"""
        self.overdue_table.setRowCount(len(activities))
        
        now = datetime.now()
        for row, activity in enumerate(activities):
            fm = QFontMetrics(self.overdue_table.font())
            name_elided = fm.elidedText(activity.title or "", Qt.TextElideMode.ElideRight, 260)
            name_item = QTableWidgetItem(name_elided)
            name_item.setToolTip(activity.title or "")
            self.overdue_table.setItem(row, 0, name_item)
            
            cat_text = activity.category.value.title()
            cat_elided = fm.elidedText(cat_text, Qt.TextElideMode.ElideRight, 120)
            category_item = QTableWidgetItem(cat_elided)
            category_item.setToolTip(cat_text)
            self.overdue_table.setItem(row, 1, category_item)
            
            # Due date
            due_date_str = activity.next_due_date.strftime("%Y-%m-%d")
            date_item = QTableWidgetItem(due_date_str)
            self.overdue_table.setItem(row, 2, date_item)
            
            # Days overdue
            days_overdue = (now - activity.next_due_date).days
            days_item = QTableWidgetItem(str(days_overdue))
            days_item.setForeground(QColor("#f85149"))
            self.overdue_table.setItem(row, 3, days_item)
            
            # Status
            status_item = QTableWidgetItem("Overdue")
            try:
                icon = IconManager.get_icon('error', size=16, color='#f85149')
                status_item.setIcon(icon)
                status_item.setForeground(QColor('#f85149'))
                bg = QColor(248, 81, 73)
                bg.setAlpha(28)
                status_item.setBackground(bg)
            except Exception:
                status_item.setForeground(QColor('#f85149'))
            self.overdue_table.setItem(row, 4, status_item)
    
    def _populate_connected_apps(self):
        """Populate connected applications quick access"""
        # Clear existing widgets
        while self.connected_apps_widget.count():
            item = self.connected_apps_widget.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        session = get_session()
        try:
            apps = ConnectedApplicationManager.get_all_connected_apps(session, active_only=True)
            
            if not apps:
                # Enhanced empty state with icon and helper text
                empty_layout = QHBoxLayout()
                try:
                    icon = IconManager.get_icon("connected_apps", size=28, color="#8b949e")
                    icon_lbl = QLabel()
                    icon_lbl.setPixmap(icon.pixmap(28, 28))
                    empty_layout.addWidget(icon_lbl)
                except:
                    pass
                no_apps_label = QLabel("No connected applications. Add one to get started.")
                no_apps_label.setStyleSheet("color: #8b949e; font-size: 13px;")
                empty_layout.addWidget(no_apps_label)
                empty_widget = QWidget()
                empty_widget.setLayout(empty_layout)
                self.connected_apps_widget.addWidget(empty_widget)
                self.connected_apps_widget.addStretch()
                return
            
            # Show first 5 apps as premium buttons
            for app in apps[:5]:
                app_btn = PremiumButton(f"{app.name}", style=PremiumButton.Style.SECONDARY, icon_name="connected_apps")
                app_btn.setMaximumWidth(220)
                app_btn.setToolTip(f"{app.app_name}\n{app.account_number or ''}")
                app_btn.clicked.connect(lambda checked, app_id=app.id: self._open_connected_app(app_id))
                self.connected_apps_widget.addWidget(app_btn)
            
            if len(apps) > 5:
                # Add "View All" button which emits a signal
                view_all_btn = PremiumButton("View All →", style=PremiumButton.Style.FLAT, icon_name="menu")
                view_all_btn.setMaximumWidth(140)
                view_all_btn.clicked.connect(lambda: self.view_all_clicked.emit())
                self.connected_apps_widget.addWidget(view_all_btn)
            
            self.connected_apps_widget.addStretch()
            
        finally:
            session.close()
    
    def _open_connected_app(self, app_id: int):
        """Open a connected application"""
        import webbrowser
        
        session = get_session()
        try:
            app = ConnectedApplicationManager.get_connected_app(session, app_id)
            if app and (app.login_url or app.website_url):
                url = app.login_url or app.website_url
                if not url.startswith('http'):
                    url = f'https://{url}'
                webbrowser.open(url)
                ConnectedApplicationManager.update_last_accessed(session, app_id)
        finally:
            session.close()

    def _on_insight_action(self, label: str, data: dict):
        """Handle insight action button clicks — emit view_all_clicked for
        navigation (the main window maps this to the correct page)."""
        self.view_all_clicked.emit()
