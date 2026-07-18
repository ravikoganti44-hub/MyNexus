"""
Sidebar navigation component with premium design
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy,
    QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor
from src.ui.styles.icon_manager import IconManager
from src.ui.styles.tokens import token, spacing
from src.ui.styles.motion import duration as _motion_duration, easing as _motion_easing
from config.settings import APP_NAME, APP_TAGLINE, APP_VERSION


class SidebarWidget(QWidget):
    """Sidebar navigation widget with premium design"""

    EXPANDED_WIDTH = 216
    COLLAPSED_WIDTH = 76
    
    page_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(self.EXPANDED_WIDTH)
        self.current_button = None
        self._collapsed = False
        self._buttons = []
        self._setup_ui()
    
    def _create_nav_button(self, icon_name: str, text: str, page_index: int) -> QPushButton:
        """Create a navigation button with icon"""
        btn = QPushButton()
        btn.setText(text)
        btn.setFixedHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        btn.setIconSize(QSize(18, 18))
        btn.setObjectName("navButton")
        
        # Set icon
        try:
            icon = IconManager.get_icon(icon_name, size=20, color=token("color.accent.primary"))
            btn.setIcon(icon)
        except Exception:
            pass
        
        btn.clicked.connect(lambda: self._on_button_clicked(btn, page_index))
        self._buttons.append((btn, text))
        return btn
    
    def _nav_base_style(self) -> str:
        return f"""
            QPushButton#navButton {{
                background-color: transparent;
                color: {token("color.text.secondary")};
                border: 1px solid transparent;
                border-radius: {token("radius.md")};
                padding: 8px 12px;
                text-align: left;
                font-weight: {token("type.weight.medium")};
            }}
            QPushButton#navButton:hover {{
                background-color: {token("color.bg.hover")};
                border: 1px solid {token("color.border.light")};
                color: {token("color.text.primary")};
            }}
        """

    def _active_style(self) -> str:
        return f"""
            QPushButton#navButton {{
                background-color: {token("color.accent.primary")};
                color: {token("color.text.inverse")};
                border: 1px solid {token("color.accent.primary")};
                border-radius: {token("radius.md")};
                padding: 8px 12px;
                text-align: left;
                font-weight: {token("type.weight.bold")};
            }}
            QPushButton#navButton:hover {{
                background-color: {token("color.accent.secondary")};
            }}
        """
    
    def _on_button_clicked(self, button: QPushButton, page_index: int):
        """Handle button click"""
        if self.current_button:
            self.current_button.setStyleSheet(self._nav_base_style())
        
        button.setStyleSheet(self._active_style())
        self.current_button = button
        self.page_changed.emit(page_index)
    
    def _setup_ui(self):
        """Setup sidebar UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(12)
        
        # Header Frame
        header_frame = QFrame()
        header_frame.setObjectName("sidebarBrandPanel")
        header_frame.setMinimumHeight(96)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(10, 12, 10, 12)
        header_layout.setSpacing(8)

        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(0, 0, 0, 0)
        brand_row.setSpacing(10)

        badge = QLabel()
        badge.setObjectName("brandBadge")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedSize(36, 36)
        badge_icon = IconManager.get_icon("my_nexus", size=24, color=token("color.text.inverse"))
        badge_pixmap = badge_icon.pixmap(24, 24)
        if not badge_pixmap.isNull():
            badge.setPixmap(badge_pixmap)
        else:
            badge.setText("N")
            badge.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        brand_row.addWidget(badge)

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setContentsMargins(0, 0, 0, 0)
        brand_text_layout.setSpacing(1)

        caption = QLabel("PERSONAL HUB")
        caption.setObjectName("sidebarBrandCaption")
        caption.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        caption.setMinimumHeight(16)
        brand_text_layout.addWidget(caption)

        # Logo / Title
        title = QLabel(APP_NAME)
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setObjectName("titleLabel")
        title.setMinimumHeight(24)
        brand_text_layout.addWidget(title)

        brand_row.addLayout(brand_text_layout, 1)
        header_layout.addLayout(brand_row)

        subtitle = QLabel(APP_TAGLINE)
        subtitle.setFont(QFont("Segoe UI", 8))
        subtitle.setObjectName("subtitleLabel")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # Separator
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {token('color.border.default')};")
        layout.addWidget(separator)
        
        # Navigation section label
        nav_label = QLabel("NAVIGATION")
        nav_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        nav_label.setObjectName("subtitleLabel")
        nav_label.setContentsMargins(12, 0, 0, 0)
        layout.addWidget(nav_label)

        # ── Nav buttons in a tight sub-layout ──────
        nav_widget = QWidget()
        nav_widget.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(spacing("space.2"))

        btn_dashboard = self._create_nav_button("dashboard", "Dashboard", 0)
        nav_layout.addWidget(btn_dashboard)
        self.current_button = btn_dashboard
        btn_dashboard.click()  # Set as active by default

        btn_activities = self._create_nav_button("activities", "My Activities", 1)
        nav_layout.addWidget(btn_activities)

        btn_integrations = self._create_nav_button("integrations", "Integrations", 2)
        nav_layout.addWidget(btn_integrations)

        btn_connected_apps = self._create_nav_button("connected_apps", "Connected Apps", 3)
        nav_layout.addWidget(btn_connected_apps)

        btn_document_vault = self._create_nav_button("document_vault", "Document Vault", 4)
        nav_layout.addWidget(btn_document_vault)

        btn_budget = self._create_nav_button("budget", "Budget Tracker", 5)
        nav_layout.addWidget(btn_budget)

        btn_calendar = self._create_nav_button("calendar_view", "Calendar View", 6)
        nav_layout.addWidget(btn_calendar)

        btn_net_worth = self._create_nav_button("net_worth", "Net Worth", 7)
        nav_layout.addWidget(btn_net_worth)

        btn_settings = self._create_nav_button("settings", "Settings", 8)
        nav_layout.addWidget(btn_settings)

        layout.addWidget(nav_widget)

        # Spacer
        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        
        # Footer separator
        footer_separator = QFrame()
        footer_separator.setStyleSheet(f"background-color: {token('color.border.default')};")
        layout.addWidget(footer_separator)
        
        # Footer meta
        developed_by_label = QLabel("Developed by Sesank Koganti")
        developed_by_label.setObjectName("footerMetaLabel")
        developed_by_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        developed_by_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
        layout.addWidget(developed_by_label)

        version_label = QLabel(APP_VERSION)
        version_label.setObjectName("footerVersionLabel")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        layout.addWidget(version_label)
        
        self.setLayout(layout)

    def _animate_width_to(self, target_width: int):
        """Animated sidebar width change."""
        if not hasattr(self, "_width_anim"):
            self._width_anim = QPropertyAnimation(self, b"maximumWidth", self)
            self._width_anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))
        else:
            self._width_anim.stop()
        self._width_anim.setDuration(_motion_duration("base"))
        self._width_anim.setStartValue(self.maximumWidth())
        self._width_anim.setEndValue(target_width)
        self._width_anim.finished.connect(lambda: self.setFixedWidth(target_width))
        self._width_anim.start()

    def collapse(self):
        """Collapse sidebar to icons-only"""
        if self._collapsed:
            return
        self._collapsed = True
        self._animate_width_to(self.COLLAPSED_WIDTH)
        for btn, text in self._buttons:
            try:
                btn.setText("")
                btn.setToolTip(text)
            except Exception:
                pass

    def expand(self):
        """Expand sidebar to full width"""
        if not self._collapsed:
            return
        self._collapsed = False
        self._animate_width_to(self.EXPANDED_WIDTH)
        for btn, text in self._buttons:
            try:
                btn.setText(text)
                btn.setToolTip("")
            except Exception:
                pass
