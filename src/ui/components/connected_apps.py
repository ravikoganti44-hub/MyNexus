"""
Connected Applications Widget
Manage external application logins and access - Premium Design
"""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QLabel, QLineEdit, QTextEdit, QComboBox,
    QMessageBox, QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QCursor, QIcon, QPixmap

from src.database.operations import ConnectedApplicationManager
from src.database.config import get_session
from src.ui.components.premium_button import PremiumButton
from src.ui.styles.icon_manager import IconManager
from src.ui.styles.tokens import token
from src.core.ai_engine import NexusAI
from src.ui.components.ai_insights_panel import AIInsightsPanel

logger = logging.getLogger(__name__)

# Semantic token-backed aliases for the legacy color scheme
PREMIUM_COLORS = {
    "bg_card":       token("color.bg.secondary"),
    "bg_card_hover": token("color.bg.tertiary"),
    "accent_primary":   token("color.accent.primary"),
    "accent_secondary": token("color.accent.secondary"),
    "text_primary":   token("color.text.primary"),
    "text_secondary": token("color.text.secondary"),
    "danger":  token("color.semantic.error"),
    "success": token("color.semantic.success"),
    "muted":   token("color.text.muted"),
}

# Category color mapping for app types
CATEGORY_COLORS = {
    "mortgage": "#7a4cff",
    "banking": "#4c9aff",
    "credit_card": "#ffb74d",
    "investment": "#7ee787",
    "utilities": "#9aa0ff",
    "insurance": "#ff6b6b",
    "medical": "#ff79c6",
    "subscription": "#6dd3b0",
    "other": "#b7c3d9",
}

ICON_SIZE = 20


def _find_action_host(widget, method_name: str):
    """Walk up the parent chain until a widget exposing the given action is found."""
    current = widget.parent()
    while current is not None:
        if hasattr(current, method_name):
            return current
        current = current.parent()
    return None


class ApplicationCardWidget(QFrame):
    """Premium card widget for displaying a single connected application"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.setMinimumHeight(248)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.init_ui()
        self.apply_styling()
    
    def apply_styling(self):
        """Apply premium card styling"""
        category_color = CATEGORY_COLORS.get(self.app.app_type, CATEGORY_COLORS["other"])
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {PREMIUM_COLORS['bg_card']};
                border: 2px solid {token("color.border.default")};
                border-radius: 14px;
                padding: 0px;
            }}
            QFrame:hover {{
                background-color: {PREMIUM_COLORS['bg_card_hover']};
                border: 2px solid {PREMIUM_COLORS['accent_primary']};
            }}
        """)
    
    def init_ui(self):
        """Initialize card UI with enhanced information"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top colored bar (category indicator)
        top_bar = QFrame()
        category_color = CATEGORY_COLORS.get(self.app.app_type, CATEGORY_COLORS["other"])
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {category_color};
                border: none;
                border-radius: 12px 12px 0px 0px;
            }}
        """)
        top_bar.setFixedHeight(4)
        main_layout.addWidget(top_bar)
        
        # Content area with padding
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(14, 12, 14, 12)
        
        # Header: Icon and App Name
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        icon_label = QLabel(self.app.icon_emoji or "📱")
        icon_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        icon_label.setFixedSize(42, 42)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)

        # App info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        # App name
        name_label = QLabel(self.app.name)
        name_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_primary']};")
        info_layout.addWidget(name_label)
        
        # Provider
        provider_label = QLabel(f"👤 {self.app.app_name or 'Unknown Provider'}")
        provider_label.setStyleSheet(f"color: {PREMIUM_COLORS['accent_primary']}; font-size: 10px; font-weight: 500;")
        info_layout.addWidget(provider_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        # Status indicator
        status_indicator = QLabel("✓ Active")
        status_indicator.setStyleSheet(f"color: {PREMIUM_COLORS['success']}; font-size: 9px; font-weight: 600;")
        header_layout.addWidget(status_indicator, alignment=Qt.AlignmentFlag.AlignTop)
        
        content_layout.addLayout(header_layout)
        
        # Divider
        divider = QFrame()
        divider.setStyleSheet(f"background-color: {token('color.border.default')}; border: none;")
        divider.setFixedHeight(1)
        content_layout.addWidget(divider)
        
        # Details Grid
        details_layout = QGridLayout()
        details_layout.setSpacing(8)
        details_layout.setHorizontalSpacing(12)
        details_layout.setColumnStretch(0, 0)  # Labels - fixed width
        details_layout.setColumnStretch(1, 1)  # Values - expandable
        
        row = 0
        
        # Account holder
        if self.app.account_holder:
            holder_label_key = QLabel("👤 Holder:")
            holder_label_key.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 600;")
            holder_label_key.setMinimumWidth(70)
            holder_label_key.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            details_layout.addWidget(holder_label_key, row, 0)
            
            holder_label = QLabel(self.app.account_holder)
            holder_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 500;")
            holder_label.setWordWrap(True)
            holder_label.setMaximumHeight(24)
            details_layout.addWidget(holder_label, row, 1)
            row += 1
        
        # Username (partially masked for security)
        if self.app.username:
            user_label_key = QLabel("🔐 User:")
            user_label_key.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 600;")
            user_label_key.setMinimumWidth(70)
            user_label_key.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            details_layout.addWidget(user_label_key, row, 0)
            
            username_masked = self.mask_username(self.app.username)
            user_label = QLabel(username_masked)
            user_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 500;")
            user_label.setToolTip(f"Username: {self.app.username}")
            user_label.setWordWrap(True)
            user_label.setMaximumHeight(24)
            details_layout.addWidget(user_label, row, 1)
            row += 1
        
        # Account number
        if self.app.account_number:
            account_label_key = QLabel("💳 Account:")
            account_label_key.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 600;")
            account_label_key.setMinimumWidth(70)
            account_label_key.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            details_layout.addWidget(account_label_key, row, 0)
            
            account_masked = self.mask_account(self.app.account_number)
            account_label = QLabel(account_masked)
            account_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 500;")
            account_label.setToolTip(f"Account: {self.app.account_number}")
            account_label.setWordWrap(True)
            account_label.setMaximumHeight(24)
            details_layout.addWidget(account_label, row, 1)
            row += 1
        
        # Category/Type
        if self.app.app_type:
            type_label_key = QLabel("📂 Type:")
            type_label_key.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 600;")
            type_label_key.setMinimumWidth(70)
            type_label_key.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            details_layout.addWidget(type_label_key, row, 0)
            
            type_label = QLabel(self.app.app_type.replace('_', ' ').title())
            category_color = CATEGORY_COLORS.get(self.app.app_type, PREMIUM_COLORS['text_secondary'])
            type_label.setStyleSheet(f"color: {category_color}; font-size: 10px; font-weight: 600;")
            type_label.setWordWrap(True)
            type_label.setMaximumHeight(24)
            details_layout.addWidget(type_label, row, 1)
            row += 1
        
        # Last accessed
        if self.app.last_accessed:
            last_accessed = self.app.last_accessed.strftime("%b %d, %Y")
            time_str = self.app.last_accessed.strftime("%I:%M %p")
        else:
            last_accessed = "Never"
            time_str = "—"
        
        accessed_label_key = QLabel("⏰ Accessed:")
        accessed_label_key.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 600;")
        accessed_label_key.setMinimumWidth(70)
        accessed_label_key.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(accessed_label_key, row, 0)
        
        accessed_label = QLabel(last_accessed)
        accessed_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 500;")
        accessed_label.setWordWrap(True)
        accessed_label.setMaximumHeight(24)
        details_layout.addWidget(accessed_label, row, 1)
        
        content_layout.addLayout(details_layout)
        
        # Notes section (if available)
        if self.app.notes:
            divider2 = QFrame()
            divider2.setStyleSheet(f"background-color: {token('color.border.default')}; border: none;")
            divider2.setFixedHeight(1)
            content_layout.addWidget(divider2)
            
            notes_label = QLabel("📝 Notes:")
            notes_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 9px; font-weight: 600;")
            content_layout.addWidget(notes_label)
            
            notes_text = QLabel(self.app.notes)
            notes_text.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 8px; font-style: italic;")
            notes_text.setWordWrap(True)
            notes_text.setMaximumHeight(32)
            content_layout.addWidget(notes_text)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        # Copy button
        copy_btn = PremiumButton("Copy", style=PremiumButton.Style.FLAT, icon_name="save")
        copy_btn.setToolTip("Copy username to clipboard")
        copy_btn.setFixedHeight(30)
        copy_btn.setMinimumWidth(68)
        copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        copy_btn.clicked.connect(self.copy_username)
        button_layout.addWidget(copy_btn)

        # Connect button — always visible, primary action
        connect_btn = PremiumButton("Connect", style=PremiumButton.Style.PRIMARY, icon_name="connected_apps")
        connect_btn.setToolTip("Open application in browser")
        connect_btn.setFixedHeight(30)
        connect_btn.setMinimumWidth(80)
        connect_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        connect_btn.clicked.connect(self.open_application)
        button_layout.addWidget(connect_btn)

        # Edit button
        edit_btn = PremiumButton("Edit", style=PremiumButton.Style.EDIT, icon_name="edit")
        edit_btn.setToolTip("Edit details")
        edit_btn.setFixedHeight(30)
        edit_btn.setMinimumWidth(68)
        edit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        edit_btn.clicked.connect(self.edit_application)
        button_layout.addWidget(edit_btn)

        # Delete button
        delete_btn = PremiumButton("Delete", style=PremiumButton.Style.GHOST_DANGER, icon_name="delete")
        delete_btn.setToolTip("Delete application")
        delete_btn.setFixedHeight(30)
        delete_btn.setMinimumWidth(76)
        delete_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        delete_btn.clicked.connect(self.delete_application)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()
        content_layout.addLayout(button_layout)

        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)

        self.setLayout(main_layout)
    
    @staticmethod
    def mask_username(username: str) -> str:
        """Mask username for security display"""
        if len(username) <= 3:
            return "*" * len(username)
        first_two = username[:2]
        last_char = username[-1]
        masked_count = len(username) - 3
        return f"{first_two}{'*' * masked_count}{last_char}"
    
    @staticmethod
    def mask_account(account: str) -> str:
        """Mask account number for security display"""
        if len(account) <= 4:
            return "*" * len(account)
        last_four = account[-4:]
        return f"••••••{last_four}"
    
    def copy_username(self):
        """Emit copy signal"""
        host = _find_action_host(self, 'copy_username')
        if host is not None:
            host.copy_username(self.app.id)
    
    def open_application(self):
        """Emit open signal"""
        host = _find_action_host(self, 'open_application')
        if host is not None:
            host.open_application(self.app.id)
    
    def edit_application(self):
        """Emit edit signal"""
        host = _find_action_host(self, 'edit_application')
        if host is not None:
            host.edit_application(self.app.id)
    
    def delete_application(self):
        """Emit delete signal"""
        host = _find_action_host(self, 'delete_application')
        if host is not None:
            host.delete_application(self.app.id)


class CompactApplicationCardWidget(QFrame):
    """Compact card widget showing minimal information with quick connect button"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.setMinimumHeight(72)
        self.setMaximumHeight(88)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.init_ui()
        self.apply_styling()
    
    def apply_styling(self):
        """Apply compact card styling"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {PREMIUM_COLORS['bg_card']};
                border: 1px solid {token("color.border.default")};
                border-radius: 8px;
            }}
            QFrame:hover {{
                background-color: {PREMIUM_COLORS['bg_card_hover']};
                border: 1px solid {PREMIUM_COLORS['accent_primary']};
            }}
        """)
    
    def init_ui(self):
        """Initialize compact card UI"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left colored bar
        left_bar = QFrame()
        category_color = CATEGORY_COLORS.get(self.app.app_type, CATEGORY_COLORS["other"])
        left_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {category_color};
                border: none;
            }}
        """)
        left_bar.setFixedWidth(4)
        main_layout.addWidget(left_bar)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(3)
        content_layout.setContentsMargins(8, 6, 8, 6)
        
        # Header: Icon and name
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        icon_label = QLabel(self.app.icon_emoji or "📱")
        icon_label.setStyleSheet("font-size: 22px;")
        icon_label.setFixedSize(28, 28)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # Name and provider
        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)
        
        name_label = QLabel(self.app.name)
        name_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_primary']};")
        info_layout.addWidget(name_label)
        
        provider_label = QLabel(self.app.app_name or "Unknown")
        provider_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 8px;")
        info_layout.addWidget(provider_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)
        
        # Quick action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(3)
        
        # Open button (primary) — always visible
        open_btn = PremiumButton("", style=PremiumButton.Style.FLAT, icon_name="connected_apps")
        open_btn.setToolTip("Connect / Open in browser")
        open_btn.setFixedSize(26, 26)
        open_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        open_btn.clicked.connect(self.open_application)
        action_layout.addWidget(open_btn)
        
        # Copy button
        copy_btn = PremiumButton("", style=PremiumButton.Style.FLAT, icon_name="save")
        copy_btn.setToolTip("Copy username")
        copy_btn.setFixedSize(26, 26)
        copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        copy_btn.clicked.connect(self.copy_username)
        action_layout.addWidget(copy_btn)
        
        # Edit button
        edit_btn = PremiumButton("", style=PremiumButton.Style.FLAT, icon_name="edit")
        edit_btn.setToolTip("Edit")
        edit_btn.setFixedSize(26, 26)
        edit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        edit_btn.clicked.connect(self.edit_application)
        action_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = PremiumButton("", style=PremiumButton.Style.GHOST_DANGER, icon_name="delete")
        delete_btn.setToolTip("Delete")
        delete_btn.setFixedSize(26, 26)
        delete_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        delete_btn.clicked.connect(self.delete_application)
        action_layout.addWidget(delete_btn)
        
        action_layout.addStretch()
        content_layout.addLayout(action_layout)
        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)
    
    def copy_username(self):
        host = _find_action_host(self, 'copy_username')
        if host is not None:
            host.copy_username(self.app.id)
    
    def open_application(self):
        host = _find_action_host(self, 'open_application')
        if host is not None:
            host.open_application(self.app.id)
    
    def edit_application(self):
        host = _find_action_host(self, 'edit_application')
        if host is not None:
            host.edit_application(self.app.id)
    
    def delete_application(self):
        host = _find_action_host(self, 'delete_application')
        if host is not None:
            host.delete_application(self.app.id)


class TableApplicationItemWidget(QFrame):
    """Professional table row widget with improved alignment and visibility"""
    
    def __init__(self, app, parent=None, index=1):
        super().__init__(parent)
        self.app = app
        self.index = index
        self.setMinimumHeight(78)
        self.setMaximumHeight(80)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.init_ui()
        self.apply_styling()
    
    def apply_styling(self):
        """Apply professional table row styling with better visibility"""
        # Alternating row colors - more visible
        if self.index % 2 == 0:
            bg_color = token("color.bg.secondary")
            hover_bg = token("color.bg.tertiary")
        else:
            bg_color = token("color.bg.primary")
            hover_bg = token("color.bg.secondary")
        
        # Improved visibility with better contrast
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: none;
                border-radius: 0px;
                padding: 0px;
            }}
            QFrame:hover {{
                background-color: {hover_bg};
                border: none;
            }}
        """)
    
    def init_ui(self):
        """Initialize table row UI with proper column alignment"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(16, 8, 16, 8)
        
        # Column 1: Index (35px) - Row number
        index_label = QLabel(str(self.index))
        index_label.setFixedWidth(35)
        index_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 11px; font-weight: 600; padding: 0px 5px;")
        index_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(index_label)
        
        # Separator
        sep1 = self.create_separator()
        main_layout.addWidget(sep1)
        
        # Column 2: App Icon (45px)
        icon_label = QLabel(self.app.icon_emoji or "📱")
        icon_label.setFixedWidth(45)
        icon_label.setStyleSheet("font-size: 32px; padding: 0px 3px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(icon_label)
        
        # Separator
        sep2 = self.create_separator()
        main_layout.addWidget(sep2)
        
        # Column 3: App Name (200px) - Hierarchical layout
        name_layout = QVBoxLayout()
        name_layout.setSpacing(2)
        name_layout.setContentsMargins(0, 0, 0, 0)
        
        name_label = QLabel(self.app.name)
        name_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_primary']}; padding: 0px; background-color: transparent;")
        name_layout.addWidget(name_label)
        
        provider_text = self.app.app_name or "Unknown Provider"
        provider_label = QLabel(provider_text)
        provider_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 9px; padding: 0px; background-color: transparent;")
        name_layout.addWidget(provider_label)
        
        name_widget = QWidget()
        name_widget.setLayout(name_layout)
        name_widget.setFixedWidth(200)
        main_layout.addWidget(name_widget)
        
        # Separator
        sep3 = self.create_separator()
        main_layout.addWidget(sep3)
        
        # Column 4: Type/Category (100px) - Badge style
        if self.app.app_type:
            type_text = self.app.app_type.replace('_', ' ').title()
            category_color = CATEGORY_COLORS.get(self.app.app_type, PREMIUM_COLORS['text_secondary'])
            
            type_label = QLabel(type_text)
            type_label.setStyleSheet(f"color: {category_color}; font-size: 10px; font-weight: 600; background-color: transparent; padding: 0px 6px;")
            type_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            type_label.setFixedWidth(100)
            main_layout.addWidget(type_label)
        else:
            main_layout.addSpacing(100)
        
        # Separator
        sep4 = self.create_separator()
        main_layout.addWidget(sep4)
        
        # Column 5: Account (120px) - Masked username
        if self.app.username:
            account_masked = self.mask_username(self.app.username)
            account_label = QLabel(account_masked)
        else:
            account_label = QLabel("—")
        
        account_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; background-color: transparent; padding: 0px 6px;")
        account_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        account_label.setFixedWidth(120)
        if self.app.username:
            account_label.setToolTip(f"Username: {self.app.username}")
        main_layout.addWidget(account_label)
        
        # Separator
        sep5 = self.create_separator()
        main_layout.addWidget(sep5)
        
        # Column 6: Last Checked (130px) - Date
        if self.app.last_accessed:
            accessed_str = self.app.last_accessed.strftime("%b %d, %Y")
        else:
            accessed_str = "Never"
        
        accessed_label = QLabel(accessed_str)
        accessed_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; background-color: transparent; padding: 0px 6px;")
        accessed_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        accessed_label.setFixedWidth(130)
        main_layout.addWidget(accessed_label)
        
        # Separator
        sep6 = self.create_separator()
        main_layout.addWidget(sep6)
        
        # Column 7: Status (90px) - Visual indicator
        status_layout = QHBoxLayout()
        status_layout.setSpacing(4)
        status_layout.setContentsMargins(0, 0, 0, 0)

        status_text = QLabel("Active")
        status_text.setStyleSheet(f"color: {PREMIUM_COLORS['success']}; font-size: 10px; font-weight: 600;")
        status_layout.addWidget(status_text, alignment=Qt.AlignmentFlag.AlignCenter)
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        status_widget.setFixedWidth(76)
        main_layout.addWidget(status_widget)
        
        # Separator
        sep7 = self.create_separator()
        main_layout.addWidget(sep7)
        
        # Column 8: Action Buttons (160px)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(4)
        action_layout.setContentsMargins(0, 0, 0, 0)
        
        # Connect/Open button — always visible
        open_btn = PremiumButton("", style=PremiumButton.Style.FLAT, icon_name="connected_apps")
        open_btn.setToolTip("Connect / Open in browser")
        open_btn.setFixedSize(28, 28)
        open_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        open_btn.clicked.connect(self.open_application)
        action_layout.addWidget(open_btn)

        # Edit button
        edit_btn = PremiumButton("", style=PremiumButton.Style.FLAT, icon_name="edit")
        edit_btn.setToolTip("Edit")
        edit_btn.setFixedSize(28, 28)
        edit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        edit_btn.clicked.connect(self.edit_application)
        action_layout.addWidget(edit_btn)

        # Copy button
        copy_btn = PremiumButton("", style=PremiumButton.Style.FLAT, icon_name="save")
        copy_btn.setToolTip("Copy")
        copy_btn.setFixedSize(28, 28)
        copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.copy_btn = copy_btn  # Store reference for visual feedback (Issue #4)
        copy_btn.clicked.connect(self.on_copy_clicked)
        action_layout.addWidget(copy_btn)

        # Delete button
        delete_btn = PremiumButton("", style=PremiumButton.Style.GHOST_DANGER, icon_name="delete")
        delete_btn.setToolTip("Delete")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        delete_btn.clicked.connect(self.delete_application)
        action_layout.addWidget(delete_btn)
        
        action_widget = QWidget()
        action_widget.setLayout(action_layout)
        action_widget.setFixedWidth(202)
        main_layout.addWidget(action_widget)
        
        self.setLayout(main_layout)
    
    def create_separator(self) -> QFrame:
        """Create a column separator line"""
        sep = QFrame()
        sep.setStyleSheet(f"background-color: {token('color.bg.tertiary')};")
        sep.setFixedWidth(1)
        sep.setMinimumHeight(40)
        sep.setMaximumHeight(60)
        return sep
    
    def on_copy_clicked(self):
        """Handle copy button click with visual feedback (Issue #4)"""
        # Visual feedback: button turns green briefly
        original_style = self.copy_btn.styleSheet()
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PREMIUM_COLORS['success']};
                color: {token("color.text.inverse")};
                border: none;
                border-radius: 5px;
                font-weight: 600;
                font-size: 12px;
            }}
        """)
        self.copy_btn.setText("✓")
        
        # Trigger the actual copy action
        self.copy_username()
        
        # Reset button after 1 second
        QTimer.singleShot(1000, lambda: self._reset_copy_button(original_style))
    
    def _reset_copy_button(self, original_style: str):
        """Reset copy button to original state"""
        self.copy_btn.setStyleSheet(original_style)
        self.copy_btn.setText("📋")

    @staticmethod
    def mask_username(username: str) -> str:
        """Mask username for security display"""
        if len(username) <= 3:
            return "*" * len(username)
        first_two = username[:2]
        last_char = username[-1]
        masked_count = len(username) - 3
        return f"{first_two}{'*' * masked_count}{last_char}"
    
    def copy_username(self):
        host = _find_action_host(self, 'copy_username')
        if host is not None:
            host.copy_username(self.app.id)
    
    def open_application(self):
        host = _find_action_host(self, 'open_application')
        if host is not None:
            host.open_application(self.app.id)
    
    def edit_application(self):
        host = _find_action_host(self, 'edit_application')
        if host is not None:
            host.edit_application(self.app.id)
    
    def delete_application(self):
        host = _find_action_host(self, 'delete_application')
        if host is not None:
            host.delete_application(self.app.id)


class ListApplicationItemWidget(QFrame):
    """List view item for applications (deprecated - use TableApplicationItemWidget)"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.setMinimumHeight(60)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.init_ui()
        self.apply_styling()
    
    def apply_styling(self):
        """Apply list item styling"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {PREMIUM_COLORS['bg_card']};
                border: 1px solid {token("color.border.default")};
                border-radius: 6px;
                padding: 0px;
            }}
            QFrame:hover {{
                background-color: {PREMIUM_COLORS['bg_card_hover']};
                border: 1px solid {PREMIUM_COLORS['accent_primary']};
            }}
        """)
    
    def init_ui(self):
        """Initialize list item UI"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 10, 12, 10)
        
        # Icon
        icon_label = QLabel(self.app.icon_emoji or "📱")
        icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(icon_label)
        
        # Info columns
        info_layout = QGridLayout()
        info_layout.setSpacing(4)
        info_layout.setColumnStretch(1, 1)
        
        # Row 0: Name and Provider
        name_label = QLabel(self.app.name)
        name_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_primary']};")
        info_layout.addWidget(name_label, 0, 0)
        
        provider_label = QLabel(self.app.app_name or "")
        provider_label.setStyleSheet(f"color: {PREMIUM_COLORS['accent_primary']}; font-size: 10px;")
        info_layout.addWidget(provider_label, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Row 1: Type and Last Accessed
        if self.app.app_type:
            type_label = QLabel(self.app.app_type.replace('_', ' ').title())
            type_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 9px;")
            info_layout.addWidget(type_label, 1, 0)
        
        if self.app.last_accessed:
            accessed_str = self.app.last_accessed.strftime("%b %d, %H:%M")
        else:
            accessed_str = "Never"
        
        accessed_label = QLabel(f"Last: {accessed_str}")
        accessed_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 9px;")
        info_layout.addWidget(accessed_label, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(info_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(4)
        
        copy_btn = PremiumButton("", style=PremiumButton.Style.FLAT, icon_name="save")
        copy_btn.setToolTip("Copy username")
        copy_btn.setFixedSize(32, 32)
        copy_btn.clicked.connect(self.copy_username)
        action_layout.addWidget(copy_btn)

        open_btn = PremiumButton("", style=PremiumButton.Style.FLAT, icon_name="connected_apps")
        open_btn.setToolTip("Connect / Open in browser")
        open_btn.setFixedSize(32, 32)
        open_btn.clicked.connect(self.open_application)
        action_layout.addWidget(open_btn)

        edit_btn = PremiumButton("", style=PremiumButton.Style.FLAT, icon_name="edit")
        edit_btn.setToolTip("Edit")
        edit_btn.setFixedSize(32, 32)
        edit_btn.clicked.connect(self.edit_application)
        action_layout.addWidget(edit_btn)

        delete_btn = PremiumButton("", style=PremiumButton.Style.GHOST_DANGER, icon_name="delete")
        delete_btn.setToolTip("Delete")
        delete_btn.setFixedSize(32, 32)
        delete_btn.clicked.connect(self.delete_application)
        action_layout.addWidget(delete_btn)
        
        main_layout.addLayout(action_layout)
        self.setLayout(main_layout)
    
    def copy_username(self):
        host = _find_action_host(self, 'copy_username')
        if host is not None:
            host.copy_username(self.app.id)
    
    def open_application(self):
        host = _find_action_host(self, 'open_application')
        if host is not None:
            host.open_application(self.app.id)
    
    def edit_application(self):
        host = _find_action_host(self, 'edit_application')
        if host is not None:
            host.edit_application(self.app.id)
    
    def delete_application(self):
        host = _find_action_host(self, 'delete_application')
        if host is not None:
            host.delete_application(self.app.id)
    """Premium card widget for displaying a single connected application"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.setMinimumHeight(280)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.init_ui()
        self.apply_styling()
    
    def apply_styling(self):
        """Apply premium card styling"""
        category_color = CATEGORY_COLORS.get(self.app.app_type, CATEGORY_COLORS["other"])
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {PREMIUM_COLORS['bg_card']};
                border: 2px solid {token("color.border.default")};
                border-radius: 14px;
                padding: 0px;
            }}
            QFrame:hover {{
                background-color: {PREMIUM_COLORS['bg_card_hover']};
                border: 2px solid {PREMIUM_COLORS['accent_primary']};
            }}
        """)
    
    def init_ui(self):
        """Initialize card UI with enhanced information"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top colored bar (category indicator)
        top_bar = QFrame()
        category_color = CATEGORY_COLORS.get(self.app.app_type, CATEGORY_COLORS["other"])
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {category_color};
                border: none;
                border-radius: 12px 12px 0px 0px;
            }}
        """)
        top_bar.setFixedHeight(4)
        main_layout.addWidget(top_bar)
        
        # Content area with padding
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(16, 14, 16, 14)
        
        # Header: Icon and App Name
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        icon_label = QLabel(self.app.icon_emoji or "📱")
        icon_label.setStyleSheet("font-size: 36px; font-weight: bold;")
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # App info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        
        # App name
        name_label = QLabel(self.app.name)
        name_font = QFont("Segoe UI", 13, QFont.Weight.Bold)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_primary']};")
        info_layout.addWidget(name_label)
        
        # Provider
        provider_label = QLabel(f"👤 {self.app.app_name or 'Unknown Provider'}")
        provider_label.setStyleSheet(f"color: {PREMIUM_COLORS['accent_primary']}; font-size: 11px; font-weight: 500;")
        info_layout.addWidget(provider_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        # Status indicator
        status_indicator = QLabel("✓ Active")
        status_indicator.setStyleSheet(f"color: {PREMIUM_COLORS['success']}; font-size: 10px; font-weight: 600;")
        header_layout.addWidget(status_indicator, alignment=Qt.AlignmentFlag.AlignTop)
        
        content_layout.addLayout(header_layout)
        
        # Divider
        divider = QFrame()
        divider.setStyleSheet(f"background-color: {token('color.border.default')}; border: none;")
        divider.setFixedHeight(1)
        content_layout.addWidget(divider)
        
        # Details Grid
        details_layout = QGridLayout()
        details_layout.setSpacing(10)
        details_layout.setHorizontalSpacing(16)
        
        row = 0
        
        # Account holder
        if self.app.account_holder:
            details_layout.addWidget(QLabel("👤 Holder:"), row, 0)
            holder_label = QLabel(self.app.account_holder)
            holder_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 500;")
            details_layout.addWidget(holder_label, row, 1)
            row += 1
        
        # Username (partially masked for security)
        if self.app.username:
            details_layout.addWidget(QLabel("🔐 User:"), row, 0)
            username_masked = self.mask_username(self.app.username)
            user_label = QLabel(username_masked)
            user_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 500;")
            user_label.setToolTip(f"Username: {self.app.username}")
            details_layout.addWidget(user_label, row, 1)
            row += 1
        
        # Account number
        if self.app.account_number:
            details_layout.addWidget(QLabel("💳 Account:"), row, 0)
            account_masked = self.mask_account(self.app.account_number)
            account_label = QLabel(account_masked)
            account_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 500;")
            account_label.setToolTip(f"Account: {self.app.account_number}")
            details_layout.addWidget(account_label, row, 1)
            row += 1
        
        # Category/Type
        if self.app.app_type:
            details_layout.addWidget(QLabel("📂 Type:"), row, 0)
            type_label = QLabel(self.app.app_type.replace('_', ' ').title())
            category_color = CATEGORY_COLORS.get(self.app.app_type, PREMIUM_COLORS['text_secondary'])
            type_label.setStyleSheet(f"color: {category_color}; font-size: 10px; font-weight: 600;")
            details_layout.addWidget(type_label, row, 1)
            row += 1
        
        # Last accessed
        if self.app.last_accessed:
            last_accessed = self.app.last_accessed.strftime("%b %d, %Y")
            time_str = self.app.last_accessed.strftime("%I:%M %p")
        else:
            last_accessed = "Never"
            time_str = "—"
        
        details_layout.addWidget(QLabel("⏰ Accessed:"), row, 0)
        accessed_label = QLabel(last_accessed)
        accessed_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 500;")
        details_layout.addWidget(accessed_label, row, 1)
        
        content_layout.addLayout(details_layout)
        
        # Notes section (if available)
        if self.app.notes:
            divider2 = QFrame()
            divider2.setStyleSheet(f"background-color: {token('color.border.default')}; border: none;")
            divider2.setFixedHeight(1)
            content_layout.addWidget(divider2)
            
            notes_label = QLabel("📝 Notes:")
            notes_label.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 10px; font-weight: 600;")
            content_layout.addWidget(notes_label)
            
            notes_text = QLabel(self.app.notes)
            notes_text.setStyleSheet(f"color: {PREMIUM_COLORS['text_secondary']}; font-size: 9px; font-style: italic;")
            notes_text.setWordWrap(True)
            notes_text.setMaximumHeight(40)
            content_layout.addWidget(notes_text)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        # Copy button
        copy_btn = PremiumButton("Copy", style=PremiumButton.Style.FLAT, icon_name="save")
        copy_btn.setToolTip("Copy username to clipboard")
        copy_btn.setFixedHeight(32)
        copy_btn.setMinimumWidth(72)
        copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        copy_btn.clicked.connect(self.copy_username)
        button_layout.addWidget(copy_btn)

        # Connect button — always visible
        connect_btn = PremiumButton("Connect", style=PremiumButton.Style.PRIMARY, icon_name="connected_apps")
        connect_btn.setToolTip("Open application in browser")
        connect_btn.setFixedHeight(32)
        connect_btn.setMinimumWidth(80)
        connect_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        connect_btn.clicked.connect(self.open_application)
        button_layout.addWidget(connect_btn)

        # Edit button
        edit_btn = PremiumButton("Edit", style=PremiumButton.Style.EDIT, icon_name="edit")
        edit_btn.setToolTip("Edit details")
        edit_btn.setFixedHeight(32)
        edit_btn.setMinimumWidth(72)
        edit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        edit_btn.clicked.connect(self.edit_application)
        button_layout.addWidget(edit_btn)

        # Delete button
        delete_btn = PremiumButton("Delete", style=PremiumButton.Style.GHOST_DANGER, icon_name="delete")
        delete_btn.setToolTip("Delete application")
        delete_btn.setFixedHeight(32)
        delete_btn.setMinimumWidth(80)
        delete_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        delete_btn.clicked.connect(self.delete_application)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()
        content_layout.addLayout(button_layout)

        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)

        self.setLayout(main_layout)
    
    @staticmethod
    def mask_username(username: str) -> str:
        """Mask username for security display"""
        if len(username) <= 3:
            return "*" * len(username)
        first_two = username[:2]
        last_char = username[-1]
        masked_count = len(username) - 3
        return f"{first_two}{'*' * masked_count}{last_char}"
    
    @staticmethod
    def mask_account(account: str) -> str:
        """Mask account number for security display"""
        if len(account) <= 4:
            return "*" * len(account)
        last_four = account[-4:]
        return f"••••••{last_four}"
    
    def copy_username(self):
        """Emit copy signal"""
        if hasattr(self.parent(), 'copy_username'):
            self.parent().copy_username(self.app.id)
    
    def open_application(self):
        """Emit open signal"""
        if hasattr(self.parent(), 'open_application'):
            self.parent().open_application(self.app.id)
    
    def edit_application(self):
        """Emit edit signal"""
        if hasattr(self.parent(), 'edit_application'):
            self.parent().edit_application(self.app.id)


class ConnectedApplicationDialog(QDialog):
    """Dialog for adding or editing a connected application"""

    CATEGORIES = [
        ("mortgage", "Mortgage"),
        ("banking", "Banking"),
        ("credit_card", "Credit Card"),
        ("investment", "Investment"),
        ("utilities", "Utilities"),
        ("insurance", "Insurance"),
        ("medical", "Medical"),
        ("subscription", "Subscription"),
        ("other", "Other"),
    ]
    EMOJI_SUGGESTIONS = ["🏠", "🏦", "💳", "📈", "⚡", "🛡️", "🏥", "📱", "📋", "🔐"]

    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.setWindowTitle("Edit Application" if app else "Add Application")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        if app:
            self._populate(app)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.setStyleSheet(f"""
            QDialog {{ background-color: {token("color.bg.primary")}; color: {token("color.text.primary")}; }}
            QLabel {{ color: {token("color.text.secondary")}; font-size: 12px; }}
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {token("color.bg.secondary")}; color: {token("color.text.primary")};
                border: 1px solid {token("color.border.default")}; border-radius: 6px;
                padding: 6px 10px; font-size: 12px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 1px solid {token("color.accent.primary")};
            }}
        """)

        def row(label, widget):
            r = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(130)
            r.addWidget(lbl)
            r.addWidget(widget)
            layout.addLayout(r)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. My Mortgage Account")
        row("Name *", self.name_edit)

        self.app_name_edit = QLineEdit()
        self.app_name_edit.setPlaceholderText("e.g. Chase Bank, Better.com")
        row("Provider", self.app_name_edit)

        self.category_combo = QComboBox()
        for key, label in self.CATEGORIES:
            self.category_combo.addItem(label, userData=key)
        row("Category", self.category_combo)

        self.website_edit = QLineEdit()
        self.website_edit.setPlaceholderText("https://www.example.com")
        row("Website URL", self.website_edit)

        self.login_url_edit = QLineEdit()
        self.login_url_edit.setPlaceholderText("https://login.example.com")
        row("Login URL", self.login_url_edit)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("email@example.com")
        row("Username *", self.username_edit)

        # Password field with generate button
        pwd_container = QWidget()
        pwd_container.setStyleSheet("background: transparent; border: none;")
        pwd_layout = QHBoxLayout(pwd_container)
        pwd_layout.setContentsMargins(0, 0, 0, 0)
        pwd_layout.setSpacing(6)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password (stored encrypted)")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_layout.addWidget(self.password_edit)
        toggle_vis_btn = QPushButton("👁")
        toggle_vis_btn.setFixedSize(32, 28)
        toggle_vis_btn.setToolTip("Show/Hide password")
        toggle_vis_btn.setStyleSheet(
            f"QPushButton {{ background: {token('color.bg.secondary')}; border: 1px solid {token('color.border.default')}; border-radius:4px; font-size:13px; }}"
            f"QPushButton:hover {{ background: {token('color.bg.tertiary')}; }}"
        )
        toggle_vis_btn.clicked.connect(lambda: self.password_edit.setEchoMode(
            QLineEdit.EchoMode.Normal if self.password_edit.echoMode() == QLineEdit.EchoMode.Password
            else QLineEdit.EchoMode.Password
        ))
        pwd_layout.addWidget(toggle_vis_btn)
        gen_btn = QPushButton("🔑 Generate")
        gen_btn.setFixedHeight(28)
        gen_btn.setStyleSheet(
            f"QPushButton {{ background: rgba(63,185,80,0.12); color: {token('color.semantic.success')}; border: 1px solid rgba(63,185,80,0.4); "
            "border-radius:4px; padding: 0 8px; font-size:11px; font-weight:600; }"
            f"QPushButton:hover {{ background: rgba(63,185,80,0.25); }}"
        )
        gen_btn.clicked.connect(self._generate_password)
        pwd_layout.addWidget(gen_btn)
        row("Password", pwd_container)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Alternative email")
        row("Email", self.email_edit)

        self.account_num_edit = QLineEdit()
        self.account_num_edit.setPlaceholderText("Account / reference number")
        row("Account Number", self.account_num_edit)

        self.holder_edit = QLineEdit()
        self.holder_edit.setPlaceholderText("Name on account")
        row("Account Holder", self.holder_edit)

        emoji_row = QHBoxLayout()
        emoji_lbl = QLabel("Icon Emoji")
        emoji_lbl.setFixedWidth(130)
        self.emoji_edit = QLineEdit()
        self.emoji_edit.setPlaceholderText("🏠")
        self.emoji_edit.setMaximumWidth(60)
        emoji_row.addWidget(emoji_lbl)
        emoji_row.addWidget(self.emoji_edit)
        for em in self.EMOJI_SUGGESTIONS:
            btn = QPushButton(em)
            btn.setFixedSize(32, 28)
            btn.setStyleSheet(f"QPushButton {{ background: {token('color.bg.secondary')}; border: 1px solid {token('color.border.default')}; border-radius:4px; font-size:14px; }}"
                              f"QPushButton:hover {{ background: {token('color.bg.tertiary')}; }}")
            btn.clicked.connect(lambda _, e=em: self.emoji_edit.setText(e))
            emoji_row.addWidget(btn)
        emoji_row.addStretch()
        layout.addLayout(emoji_row)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Notes, reminders, or anything useful...")
        self.notes_edit.setFixedHeight(70)
        notes_row = QHBoxLayout()
        notes_lbl = QLabel("Notes")
        notes_lbl.setFixedWidth(130)
        notes_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        notes_row.addWidget(notes_lbl)
        notes_row.addWidget(self.notes_edit)
        layout.addLayout(notes_row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = PremiumButton("Cancel", style=PremiumButton.Style.SECONDARY)
        cancel_btn.setFixedHeight(36)
        cancel_btn.setMinimumWidth(90)
        cancel_btn.clicked.connect(self.reject)
        save_btn = PremiumButton("Save", style=PremiumButton.Style.PRIMARY)
        save_btn.setFixedHeight(36)
        save_btn.setMinimumWidth(90)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _populate(self, app):
        self.name_edit.setText(app.name or "")
        self.app_name_edit.setText(app.app_name or "")
        # Set category combo
        cat_key = app.app_type or (app.category or "other")
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == cat_key:
                self.category_combo.setCurrentIndex(i)
                break
        self.website_edit.setText(app.website_url or "")
        self.login_url_edit.setText(app.login_url or "")
        self.username_edit.setText(app.username or "")
        # Decrypt password for editing
        if app.password_encrypted:
            try:
                from src.core.encryption import get_encryption_manager
                em = get_encryption_manager()
                if em:
                    self.password_edit.setText(em.decrypt(app.password_encrypted))
                else:
                    self.password_edit.setPlaceholderText("(encrypted — unlock to view)")
            except Exception:
                self.password_edit.setPlaceholderText("(encrypted — unlock to view)")
        self.email_edit.setText(app.email or "")
        self.account_num_edit.setText(app.account_number or "")
        self.holder_edit.setText(app.account_holder or "")
        self.emoji_edit.setText(app.icon_emoji or "")
        self.notes_edit.setPlainText(app.notes or "")

    def _on_save(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Application name is required.")
            return
        if not self.username_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Username is required.")
            return
        self.accept()

    def _generate_password(self):
        """Generate a strong random password."""
        import secrets
        import string
        chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        pwd = ''.join(secrets.choice(chars) for _ in range(20))
        # Ensure at least one of each category
        pwd = (secrets.choice(string.ascii_uppercase)
               + secrets.choice(string.ascii_lowercase)
               + secrets.choice(string.digits)
               + secrets.choice("!@#$%^&*()-_=+")
               + pwd[4:])
        self.password_edit.setText(pwd)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)

    def get_form_data(self) -> dict:
        cat_key = self.category_combo.currentData()
        # Encrypt password if encryption is available
        raw_password = self.password_edit.text().strip()
        encrypted_password = None
        if raw_password:
            try:
                from src.core.encryption import get_encryption_manager
                em = get_encryption_manager()
                if em:
                    encrypted_password = em.encrypt(raw_password)
                else:
                    encrypted_password = raw_password  # fallback: store as-is
            except Exception:
                encrypted_password = raw_password
        return {
            "name": self.name_edit.text().strip(),
            "app_name": self.app_name_edit.text().strip() or None,
            "app_type": cat_key,
            "category": cat_key,
            "website_url": self.website_edit.text().strip() or None,
            "login_url": self.login_url_edit.text().strip() or None,
            "username": self.username_edit.text().strip(),
            "password_encrypted": encrypted_password,
            "email": self.email_edit.text().strip() or None,
            "account_number": self.account_num_edit.text().strip() or None,
            "account_holder": self.holder_edit.text().strip() or None,
            "icon_emoji": self.emoji_edit.text().strip() or None,
            "notes": self.notes_edit.toPlainText().strip() or None,
        }


class ConnectedAppsWidget(QWidget):
    """Widget for managing connected applications - Modern Premium UI"""
    
    # View modes
    VIEW_CARD = "card"
    VIEW_LIST = "list"
    VIEW_GRID = "grid"
    VIEW_COMPACT = "compact"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = get_session()
        self.card_layout = None
        self.current_view = self.VIEW_CARD  # Default view
        self.view_buttons = {}
        self.selected_category = "all"
        self.search_query = ""
        # Debounce timer for search performance (Issue #3)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
        self.init_ui()  # init_ui applies initial view mode and loads apps
    
    def init_ui(self):
        """Initialize UI with enhanced design"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)
        
        # Header section styled to match the Integrations page
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-bottom: 1px solid {token("color.border.default")};
                padding-bottom: 10px;
                border-radius: 0px;
            }}
        """)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        title = QLabel("Connected Apps")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setObjectName("titleLabel")
        title.setStyleSheet(f"color: {PREMIUM_COLORS['accent_primary']};")
        header_layout.addWidget(title)
        header_layout.addStretch()

        add_btn = PremiumButton("Add Application", style=PremiumButton.Style.PRIMARY, icon_name="add")
        add_btn.setFixedHeight(44)
        add_btn.setMinimumWidth(154)
        add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        add_btn.clicked.connect(self.add_application)
        header_layout.addWidget(add_btn)

        refresh_btn = PremiumButton("Refresh", style=PremiumButton.Style.SECONDARY, icon_name="refresh")
        refresh_btn.setFixedHeight(44)
        refresh_btn.setMinimumWidth(132)
        refresh_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        refresh_btn.clicked.connect(self.refresh_apps)
        header_layout.addWidget(refresh_btn)

        export_btn = PremiumButton("Export", style=PremiumButton.Style.FLAT, icon_name="download")
        export_btn.setFixedHeight(44)
        export_btn.setMinimumWidth(100)
        export_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        export_btn.clicked.connect(self._export_apps)
        header_layout.addWidget(export_btn)

        import_browser_btn = PremiumButton("Import from Browser", style=PremiumButton.Style.FLAT, icon_name="upload")
        import_browser_btn.setFixedHeight(44)
        import_browser_btn.setMinimumWidth(160)
        import_browser_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        import_browser_btn.clicked.connect(self._import_from_browser)
        header_layout.addWidget(import_browser_btn)

        self.total_stat = QLabel("0")
        self.total_stat.hide()
        self.secured_stat = QLabel("0")
        self.secured_stat.hide()
        
        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)
        
        # Combined control strip: search, filter, view mode, and actions
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(26, 26, 46, 0.92), stop:1 rgba(13, 17, 23, 0.78));
                border: 2px solid {token("color.border.default")};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        controls_layout = QVBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)

        search_row_layout = QHBoxLayout()
        search_row_layout.setContentsMargins(0, 0, 0, 0)
        search_row_layout.setSpacing(8)
        search_row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Search input with modern styling - Enhanced
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by app name, provider, or username...")
        self.search_input.setFixedHeight(36)
        self.search_input.setMinimumWidth(260)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {token("color.bg.secondary")};
                color: {PREMIUM_COLORS['text_primary']};
                border: 2px solid {token("color.border.default")};
                border-radius: 10px;
                padding: 7px 12px;
                font-size: 11px;
                selection-background-color: {PREMIUM_COLORS['accent_primary']};
            }}
            QLineEdit:focus {{
                border: 2px solid {PREMIUM_COLORS['accent_primary']};
                background-color: {token("color.bg.secondary")};
            }}
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        search_row_layout.addWidget(self.search_input, 1)

        controls_layout.addLayout(search_row_layout)

        options_row_layout = QHBoxLayout()
        options_row_layout.setContentsMargins(0, 0, 0, 0)
        options_row_layout.setSpacing(8)
        options_row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Filter group frame - compact grouped controls
        filter_group_frame = QFrame()
        filter_group_frame.setFixedHeight(36)
        filter_group_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(26, 26, 46, 0.8);
                border: 2px solid {token("color.border.default")};
                border-radius: 10px;
                padding: 1px;
            }}
        """)
        filter_group_layout = QHBoxLayout()
        filter_group_layout.setContentsMargins(8, 0, 8, 0)
        filter_group_layout.setSpacing(6)
        filter_group_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        cat_label = QLabel("📂 Filter:")
        cat_label.setStyleSheet(f"color: {PREMIUM_COLORS['accent_primary']}; font-size: 11px; font-weight: 600;")
        cat_label.setToolTip("Filter by category")
        filter_group_layout.addWidget(cat_label)

        self.category_combo = QComboBox()
        self.category_combo.setFixedHeight(28)
        self.category_combo.setMinimumWidth(140)
        self.category_combo.setMaximumWidth(176)
        self.category_combo.addItem("All Categories", "all")
        for cat_key in CATEGORY_COLORS.keys():
            self.category_combo.addItem(cat_key.replace("_", " ").title(), cat_key)
        self.category_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {token("color.bg.secondary")};
                color: {PREMIUM_COLORS['text_primary']};
                border: 1px solid {token("color.border.default")};
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 11px;
                font-weight: 500;
            }}
            QComboBox:focus {{
                border: 2px solid {PREMIUM_COLORS['accent_primary']};
                background-color: {token("color.bg.secondary")};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 18px;
            }}
        """)
        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        filter_group_layout.addWidget(self.category_combo)

        sep = QFrame()
        sep.setStyleSheet(f"background-color: {token('color.border.default')};")
        sep.setFixedWidth(1)
        sep.setFixedHeight(18)
        filter_group_layout.addWidget(sep)

        sort_label = QLabel("📊 Sort:")
        sort_label.setStyleSheet(f"color: {PREMIUM_COLORS['accent_primary']}; font-size: 11px; font-weight: 600;")
        sort_label.setToolTip("Sort results")
        filter_group_layout.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.setFixedHeight(28)
        self.sort_combo.setMinimumWidth(132)
        self.sort_combo.setMaximumWidth(168)
        self.sort_combo.addItems(["Name (A-Z)", "Recently Used", "Date Added"])
        self.sort_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {token("color.bg.secondary")};
                color: {PREMIUM_COLORS['text_primary']};
                border: 1px solid {token("color.border.default")};
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 11px;
                font-weight: 500;
            }}
            QComboBox:focus {{
                border: 2px solid {PREMIUM_COLORS['accent_primary']};
                background-color: {token("color.bg.secondary")};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 18px;
            }}
        """)
        self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)
        filter_group_layout.addWidget(self.sort_combo)

        filter_group_frame.setLayout(filter_group_layout)
        options_row_layout.addWidget(filter_group_frame, 1)

        # View mode selector - compact segmented control
        view_group_frame = QFrame()
        view_group_frame.setFixedHeight(34)
        view_group_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {token("color.bg.secondary")};
                border: 1px solid {token("color.border.default")};
                border-radius: 8px;
                padding: 1px;
            }}
        """)
        view_group_layout = QHBoxLayout()
        view_group_layout.setContentsMargins(3, 0, 3, 0)
        view_group_layout.setSpacing(2)
        view_group_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        card_btn = PremiumButton("Cards", style=PremiumButton.Style.FLAT, icon_name="dashboard")
        card_btn.setFixedHeight(28)
        card_btn.setMinimumWidth(72)
        card_btn.setToolTip("Card View - Large cards with full details (best for detail review)")
        card_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        card_btn.clicked.connect(lambda: self.set_view_mode(self.VIEW_CARD))
        self.view_buttons[self.VIEW_CARD] = card_btn
        view_group_layout.addWidget(card_btn)

        list_btn = PremiumButton("List", style=PremiumButton.Style.FLAT, icon_name="activities")
        list_btn.setFixedHeight(28)
        list_btn.setMinimumWidth(68)
        list_btn.setToolTip("List View - Professional table format (best for scanning)")
        list_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        list_btn.clicked.connect(lambda: self.set_view_mode(self.VIEW_LIST))
        self.view_buttons[self.VIEW_LIST] = list_btn
        view_group_layout.addWidget(list_btn)

        grid_btn = PremiumButton("Grid", style=PremiumButton.Style.FLAT, icon_name="menu")
        grid_btn.setFixedHeight(28)
        grid_btn.setMinimumWidth(68)
        grid_btn.setToolTip("Grid View - Compact 3-column grid (best for overview)")
        grid_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        grid_btn.clicked.connect(lambda: self.set_view_mode(self.VIEW_GRID))
        self.view_buttons[self.VIEW_GRID] = grid_btn
        view_group_layout.addWidget(grid_btn)

        compact_btn = PremiumButton("Compact", style=PremiumButton.Style.FLAT, icon_name="menu")
        compact_btn.setFixedHeight(28)
        compact_btn.setMinimumWidth(84)
        compact_btn.setToolTip("Compact View - Dense 4-column display (best for space)")
        compact_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        compact_btn.clicked.connect(lambda: self.set_view_mode(self.VIEW_COMPACT))
        self.view_buttons[self.VIEW_COMPACT] = compact_btn
        view_group_layout.addWidget(compact_btn)

        view_group_frame.setLayout(view_group_layout)
        options_row_layout.addWidget(view_group_frame, 0)
        options_row_layout.addStretch(1)

        controls_layout.addLayout(options_row_layout)

        controls_frame.setLayout(controls_layout)
        main_layout.addWidget(controls_frame)
        
        # Content area with scrolling
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {token("color.bg.primary")};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {PREMIUM_COLORS['bg_card']};
                border-radius: 6px;
                min-height: 50px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {PREMIUM_COLORS['accent_primary']};
            }}
        """)
        
        # Container for cards
        self.cards_container = QWidget()
        self.card_layout = QGridLayout()
        self.card_layout.setSpacing(20)
        
        # Pagination state
        self._page = 0
        self._page_size = 8
        self._filtered_apps = []
        self._build_pager()
        main_layout.addWidget(self._pager_widget)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_container.setLayout(self.card_layout)
        
        content_scroll.setWidget(self.cards_container)
        main_layout.addWidget(content_scroll, 1)

        # ── AI Security Insights ──────────────────────────────────────────
        sep_ai = QFrame()
        sep_ai.setFixedHeight(1)
        sep_ai.setStyleSheet(f"background-color: {token('color.border.default')};")
        main_layout.addWidget(sep_ai)
        self.security_ai_panel = AIInsightsPanel()
        main_layout.addWidget(self.security_ai_panel)
        
        # Empty state label (styled better)
        self.empty_label = QLabel()
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"""
            color: {PREMIUM_COLORS['text_secondary']};
            font-size: 14px;
            padding: 60px;
        """)
        self.empty_label.hide()
        
        self.setLayout(main_layout)
        
        # Apply initial active state to default view button
        self.set_view_mode(self.current_view)

    def _import_from_browser(self):
        """Open the browser password CSV import dialog."""
        from src.ui.components.data_importers import BrowserPasswordImportDialog
        dlg = BrowserPasswordImportDialog(self)
        if dlg.exec():
            self.refresh_apps()

    def on_search_changed(self, text):
        """Handle search input changes with debouncing (Issue #3)"""
        self.search_query = text.lower()
        # Debounce search to prevent performance issues
        self.search_timer.stop()
        self.search_timer.start(300)  # Wait 300ms before searching
    
    def _perform_search(self):
        """Perform the actual search after debounce"""
        # Reset sort when searching (Issue #5)
        if self.search_query and self.sort_combo.currentIndex() != 0:
            self.sort_combo.setCurrentIndex(0)  # Reset to Name A-Z
        self.refresh_apps()
    
    def on_category_changed(self, index):
        """Handle category filter changes"""
        self.selected_category = self.category_combo.currentData() or "all"
        self.refresh_apps()
    
    def on_sort_changed(self, index):
        """Handle sort order changes"""
        self.refresh_apps()

    def _build_pager(self):
        self._pager_widget = QWidget()
        p = QHBoxLayout(self._pager_widget)
        p.setContentsMargins(0, 8, 0, 0)
        p.setSpacing(8)

        self._prev_btn = PremiumButton("◀ Prev", style=PremiumButton.Style.SECONDARY, icon_name="calendar_view")
        self._prev_btn.clicked.connect(self._prev_page)
        p.addWidget(self._prev_btn)

        self._page_label = QLabel("Page 1")
        self._page_label.setStyleSheet(f"color: {token('color.text.secondary')}; font-size: 11px;")
        p.addWidget(self._page_label)

        self._next_btn = PremiumButton("Next ▶", style=PremiumButton.Style.PRIMARY, icon_name="dashboard")
        self._next_btn.clicked.connect(self._next_page)
        p.addWidget(self._next_btn)

        self._update_pager()

    def _update_pager(self):
        total_pages = max(1, (len(self._filtered_apps) + self._page_size - 1) // self._page_size)
        self._page = min(self._page, total_pages - 1)
        self._page_label.setText(f"Page {self._page + 1} / {total_pages}")
        self._prev_btn.setEnabled(self._page > 0)
        self._next_btn.setEnabled(self._page < total_pages - 1)

    def _prev_page(self):
        if self._page > 0:
            self._page -= 1
            self._render_page()

    def _next_page(self):
        total_pages = max(1, (len(self._filtered_apps) + self._page_size - 1) // self._page_size)
        if self._page < total_pages - 1:
            self._page += 1
            self._render_page()

    def _render_page(self):
        self._update_pager()
        start = self._page * self._page_size
        page_apps = self._filtered_apps[start:start + self._page_size]

        if self.current_view == self.VIEW_CARD:
            self.render_card_view(page_apps)
        elif self.current_view == self.VIEW_LIST:
            self.render_list_view(page_apps)
        elif self.current_view == self.VIEW_GRID:
            self.render_grid_view(page_apps)
        elif self.current_view == self.VIEW_COMPACT:
            self.render_compact_view(page_apps)

    def refresh_apps(self):
        """Refresh the applications display based on current view mode"""
        # Clear existing items
        while self.card_layout.count():
            widget = self.card_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        
        # Handle database errors (Issue #2)
        try:
            apps = ConnectedApplicationManager.get_all_connected_apps(self.session, active_only=True)
            if apps is None:
                self.empty_label.setText("⚠️ Error loading applications. Please check your database connection and try again.")
                self.empty_label.show()
                self.card_layout.addWidget(self.empty_label, 0, 0)
                return
        except Exception as e:
            logger.error(f"Error fetching applications: {e}")
            self.empty_label.setText(f"⚠️ Error loading applications: {str(e)[:100]}")
            self.empty_label.show()
            self.card_layout.addWidget(self.empty_label, 0, 0)
            return
        
        # Apply filters
        filtered_apps = []
        for app in apps:
            # Filter by category
            if self.selected_category != "all" and app.app_type != self.selected_category:
                continue
            
            # Filter by search query
            if self.search_query:
                search_matches = (
                    self.search_query in app.name.lower() or
                    self.search_query in (app.app_name or "").lower() or
                    self.search_query in (app.account_holder or "").lower() or
                    self.search_query in (app.account_number or "").lower()
                )
                if not search_matches:
                    continue
            
            filtered_apps.append(app)
        
        # Apply sorting
        sort_index = self.sort_combo.currentIndex()
        if sort_index == 0:  # Name A-Z
            filtered_apps.sort(key=lambda x: x.name.lower())
        elif sort_index == 1:  # Recently used
            filtered_apps.sort(key=lambda x: x.last_accessed or datetime.min, reverse=True)
        elif sort_index == 2:  # Date added
            filtered_apps.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
        
        # Update stats
        self.total_stat.setText(str(len(apps)))
        self.secured_stat.setText(str(len(filtered_apps)))
        self._filtered_apps = filtered_apps
        
        if not filtered_apps:
            if self.search_query or self.selected_category != "all":
                self.empty_label.setText("🔍 No applications match your search or filter criteria.\n\nTry adjusting your search or filters.")
            else:
                self.empty_label.setText("📭 No connected applications yet.\n\nClick 'Add Application' to get started!")
            self.empty_label.show()
            self.card_layout.addWidget(self.empty_label, 0, 0)
            self._page = 0
            self._update_pager()
            return
        
        self.empty_label.hide()
        self._page = 0
        self._render_page()
        
        # ── AI Security Insights refresh ──────────────────────────────
        try:
            security_insights = NexusAI.analyse_security(self.session)
            self.security_ai_panel.set_insights(security_insights)
        except Exception:
            pass

    def _export_apps(self):
        """Export connected applications to JSON."""
        import json as _json
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Connected Apps", "connected_apps_export.json", "JSON Files (*.json)"
        )
        if not path:
            return
        session = get_session()
        try:
            apps = ConnectedApplicationManager.get_all_connected_apps(session, active_only=False)
            data = []
            for app in apps:
                data.append({
                    "name": app.name,
                    "provider": app.app_name,
                    "category": app.category,
                    "website_url": app.website_url,
                    "login_url": app.login_url,
                    "username": app.username,
                    "email": app.email,
                    "account_number": app.account_number,
                    "account_holder": app.account_holder,
                    "notes": app.notes,
                    "icon_emoji": app.icon_emoji,
                    "created_at": str(app.created_at) if app.created_at else None,
                })
            with open(path, "w", encoding="utf-8") as f:
                _json.dump(data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Export", f"Exported {len(data)} apps to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
        finally:
            session.close()

    def get_view_button_style(self, active: bool) -> str:
        """Get styling for view button based on active state - DEPRECATED"""
        if active:
            return f"""
                QPushButton {{
                    background-color: {PREMIUM_COLORS['accent_primary']};
                    color: {token("color.text.inverse")};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: 600;
                    font-size: 11px;
                }}
                QPushButton:hover {{ background-color: {token("color.accent.hover")}; color: {token("color.text.inverse")}; }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {PREMIUM_COLORS['text_secondary']};
                    border: 1px solid {token("color.border.default")};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: 500;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {token("color.bg.tertiary")};
                    border: 1px solid {token("color.border.default")};
                    color: {PREMIUM_COLORS['text_primary']};
                }}
            """
    
    def get_view_button_segmented_style(self, active: bool) -> str:
        """Get segmented-control style for view buttons"""
        if active:
            return f"""
                QPushButton {{
                    background-color: {PREMIUM_COLORS['accent_primary']};
                    color: {token("color.text.inverse")};
                    border: 1px solid {PREMIUM_COLORS['accent_primary']};
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 12px;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                    background-color: {token("color.accent.hover")};
                    border: 1px solid {token("color.accent.hover")};
                    color: {token("color.text.inverse")};
                }}
                QPushButton:pressed {{
                    background-color: {token("color.accent.pressed")};
                    color: {token("color.text.inverse")};
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {PREMIUM_COLORS['text_secondary']};
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: rgba(88, 166, 255, 0.1);
                    color: {PREMIUM_COLORS['accent_primary']};
                    border: 1px solid rgba(88, 166, 255, 0.3);
                }}
                QPushButton:pressed {{
                    background-color: rgba(88, 166, 255, 0.2);
                }}
            """
    
    def set_view_mode(self, view_mode: str):
        """Change the view mode and update UI"""
        self.current_view = view_mode
        
        # Update button styles: active = filled accent, inactive = flat
        for mode, btn in self.view_buttons.items():
            if mode == view_mode:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {PREMIUM_COLORS['accent_primary']};
                        color: {token("color.text.inverse")};
                        border: 1px solid {PREMIUM_COLORS['accent_primary']};
                        border-radius: 6px;
                        padding: 4px 10px;
                        font-size: 12px;
                        font-weight: 700;
                    }}
                    QPushButton:hover {{
                        background-color: {token("color.accent.hover")};
                        color: {token("color.text.inverse")};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {PREMIUM_COLORS['text_secondary']};
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 6px;
                        padding: 4px 10px;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(88, 166, 255, 0.1);
                        color: {PREMIUM_COLORS['accent_primary']};
                        border: 1px solid rgba(88, 166, 255, 0.3);
                    }}
                """)
        
        # Update view info label
        view_names = {
            self.VIEW_CARD: "Card View",
            self.VIEW_LIST: "List View", 
            self.VIEW_GRID: "Grid View",
            self.VIEW_COMPACT: "Compact View"
        }
        if hasattr(self, 'view_info_label'):
            self.view_info_label.setText(view_names.get(view_mode, "View"))
        
        # Refresh with new view
        self.refresh_apps()
    
    def refresh_apps(self):
        """Refresh the applications display based on current view mode"""
        # Clear existing items
        while self.card_layout.count():
            widget = self.card_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        
        # Handle database errors (Issue #2)
        try:
            apps = ConnectedApplicationManager.get_all_connected_apps(self.session, active_only=True)
            if apps is None:
                self.empty_label.setText("⚠️ Error loading applications. Please check your database connection and try again.")
                self.empty_label.show()
                self.card_layout.addWidget(self.empty_label, 0, 0)
                return
        except Exception as e:
            logger.error(f"Error fetching applications: {e}")
            self.empty_label.setText(f"⚠️ Error loading applications: {str(e)[:100]}")
            self.empty_label.show()
            self.card_layout.addWidget(self.empty_label, 0, 0)
            return
        
        # Apply filters
        filtered_apps = []
        for app in apps:
            # Filter by category
            if self.selected_category != "all" and app.app_type != self.selected_category:
                continue
            
            # Filter by search query
            if self.search_query:
                search_matches = (
                    self.search_query in app.name.lower() or
                    self.search_query in (app.app_name or "").lower() or
                    self.search_query in (app.account_holder or "").lower() or
                    self.search_query in (app.account_number or "").lower()
                )
                if not search_matches:
                    continue
            
            filtered_apps.append(app)
        
        # Apply sorting
        sort_index = self.sort_combo.currentIndex()
        if sort_index == 0:  # Name A-Z
            filtered_apps.sort(key=lambda x: x.name.lower())
        elif sort_index == 1:  # Recently used
            filtered_apps.sort(key=lambda x: x.last_accessed or datetime.min, reverse=True)
        elif sort_index == 2:  # Date added
            filtered_apps.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
        
        # Update stats
        self.total_stat.setText(str(len(apps)))
        self.secured_stat.setText(str(len(filtered_apps)))
        
        if not filtered_apps:
            if self.search_query or self.selected_category != "all":
                self.empty_label.setText("🔍 No applications match your search or filter criteria.\n\nTry adjusting your search or filters.")
            else:
                self.empty_label.setText("📭 No connected applications yet.\n\nClick 'Add Application' to get started!")
            self.empty_label.show()
            self.card_layout.addWidget(self.empty_label, 0, 0)
            return
        
        self.empty_label.hide()
        
        # Render based on view mode
        if self.current_view == self.VIEW_CARD:
            self.render_card_view(filtered_apps)
        elif self.current_view == self.VIEW_LIST:
            self.render_list_view(filtered_apps)
        elif self.current_view == self.VIEW_GRID:
            self.render_grid_view(filtered_apps)
        elif self.current_view == self.VIEW_COMPACT:
            self.render_compact_view(filtered_apps)

        # ── AI Security Insights refresh ──────────────────────────────
        try:
            security_insights = NexusAI.analyse_security(self.session)
            self.security_ai_panel.set_insights(security_insights)
        except Exception:
            pass
    
    def render_card_view(self, apps):
        """Render applications in card view (responsive width)."""
        self.card_layout.setHorizontalSpacing(20)
        self.card_layout.setVerticalSpacing(20)
        self.card_layout.setColumnStretch(0, 1)
        self.card_layout.setColumnStretch(1, 1)
        for col in range(2, 10):
            self.card_layout.setColumnStretch(col, 0)

        max_card_width = 340
        container = getattr(self, 'cards_container', None)
        if container is not None:
            container_width = container.width()
            if container_width > 0:
                max_card_width = max(260, (container_width // 2) - 30)

        row, col = 0, 0
        for app in apps:
            card = ApplicationCardWidget(app, self)
            card.setMaximumWidth(max_card_width)
            card.setMinimumWidth(min(240, max_card_width))
            self.card_layout.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1
    
    def render_list_view(self, apps):
        """Render applications in professional table view with proper alignment"""
        container = QWidget()
        list_layout = QVBoxLayout()
        list_layout.setSpacing(0)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # Professional Table Container with border
        table_container = QFrame()
        table_container.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: 2px solid {token("color.border.default")};
                border-radius: 10px;
                padding: 0px;
            }}
        """)
        
        table_layout = QVBoxLayout()
        table_layout.setSpacing(0)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Professional Table Header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {token("color.bg.secondary")},
                    stop:1 {token("color.bg.primary")}
                );
                border: none;
                border-bottom: 2px solid {token("color.border.default")};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 0px;
            }}
        """)
        header_frame.setMinimumHeight(52)
        header_frame.setMaximumHeight(52)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Define column specifications (text, width, alignment)
        columns = [
            ("#", 35, Qt.AlignmentFlag.AlignCenter),
            ("APP", 45, Qt.AlignmentFlag.AlignCenter),
            ("NAME", 200, Qt.AlignmentFlag.AlignLeft),
            ("TYPE", 100, Qt.AlignmentFlag.AlignCenter),
            ("ACCOUNT", 120, Qt.AlignmentFlag.AlignCenter),
            ("LAST ACCESSED", 130, Qt.AlignmentFlag.AlignCenter),
            ("STATUS", 76, Qt.AlignmentFlag.AlignCenter),
            ("ACTIONS", 202, Qt.AlignmentFlag.AlignCenter),
        ]
        
        for col_text, col_width, alignment in columns:
            # Create separator between columns
            if col_text != "#":
                sep = QFrame()
                sep.setStyleSheet(f"background-color: {token('color.bg.tertiary')}; min-width: 1px;")
                sep.setFixedWidth(1)
                sep.setMinimumHeight(30)
                header_layout.addWidget(sep)
            
            # Column header
            col_label = QLabel(col_text)
            col_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
            col_label.setFont(col_font)
            col_label.setStyleSheet(f"""
                color: {PREMIUM_COLORS['accent_primary']};
                font-weight: 700;
                text-transform: uppercase;
                font-size: 11px;
                letter-spacing: 0.8px;
                background-color: transparent;
                padding: 0px 8px;
            """)
            col_label.setFixedWidth(col_width)
            col_label.setAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
            header_layout.addWidget(col_label)
        
        header_frame.setLayout(header_layout)
        table_layout.addWidget(header_frame)
        
        # Table Rows Container
        rows_container = QWidget()
        rows_layout = QVBoxLayout()
        rows_layout.setSpacing(1)  # 1px separator between rows
        rows_layout.setContentsMargins(0, 0, 0, 0)
        
        if apps:
            for index, app in enumerate(apps, 1):
                item = TableApplicationItemWidget(app, rows_container, index)
                rows_layout.addWidget(item)
        
        rows_layout.addStretch()
        rows_container.setLayout(rows_layout)
        
        rows_scroll = QScrollArea()
        rows_scroll.setWidget(rows_container)
        rows_scroll.setWidgetResizable(True)
        rows_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {token("color.bg.secondary")};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {token("color.bg.tertiary")};
                border-radius: 5px;
                min-height: 40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {PREMIUM_COLORS['accent_primary']};
            }}
        """)
        
        table_layout.addWidget(rows_scroll, 1)
        
        table_container.setLayout(table_layout)
        list_layout.addWidget(table_container, 1)
        
        container.setLayout(list_layout)
        self.card_layout.addWidget(container, 0, 0, 1, 2)
    
    def render_grid_view(self, apps):
        """Render applications in grid view (3-column compact grid)"""
        self.card_layout.setHorizontalSpacing(14)
        self.card_layout.setVerticalSpacing(14)
        self.card_layout.setColumnStretch(0, 1)
        self.card_layout.setColumnStretch(1, 1)
        self.card_layout.setColumnStretch(2, 1)
        self.card_layout.setColumnStretch(3, 0)
        row, col = 0, 0
        for app in apps:
            card = CompactApplicationCardWidget(app, self)
            self.card_layout.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    def render_compact_view(self, apps):
        """Render applications in compact view (4-column minimal grid)"""
        self.card_layout.setHorizontalSpacing(12)
        self.card_layout.setVerticalSpacing(12)
        self.card_layout.setColumnStretch(0, 1)
        self.card_layout.setColumnStretch(1, 1)
        self.card_layout.setColumnStretch(2, 1)
        self.card_layout.setColumnStretch(3, 1)
        row, col = 0, 0
        for app in apps:
            card = CompactApplicationCardWidget(app, self)
            self.card_layout.addWidget(card, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1
    
    def add_application(self):
        """Add a new connected application"""
        dialog = ConnectedApplicationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_form_data()
            
            if not data['name'] or not data['username']:
                QMessageBox.warning(self, "Validation Error", "Application name and username are required")
                return
            
            try:
                ConnectedApplicationManager.create_connected_app(self.session, **data)
                logger.info(f"Added connected application: {data['name']}")
                self.refresh_apps()
                QMessageBox.information(self, "Success", f"Application '{data['name']}' added successfully!")
            except Exception as e:
                logger.error(f"Error adding application: {e}")
                QMessageBox.critical(self, "Error", f"Failed to add application: {str(e)}")
    
    def edit_application(self, app_id: int):
        """Edit a connected application"""
        app = ConnectedApplicationManager.get_connected_app(self.session, app_id)
        if not app:
            QMessageBox.warning(self, "Error", "Application not found")
            return
        
        dialog = ConnectedApplicationDialog(self, app)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_form_data()
            
            try:
                ConnectedApplicationManager.update_connected_app(self.session, app_id, **data)
                logger.info(f"Updated connected application: {data['name']}")
                self.refresh_apps()
                QMessageBox.information(self, "Success", f"Application '{data['name']}' updated successfully!")
            except Exception as e:
                logger.error(f"Error updating application: {e}")
                QMessageBox.critical(self, "Error", f"Failed to update application: {str(e)}")
    
    def delete_application(self, app_id: int):
        """Delete a connected application"""
        app = ConnectedApplicationManager.get_connected_app(self.session, app_id)
        if not app:
            return
        
        # Improved confirmation message (Issue #6)
        account_info = f" ({app.username})" if app.username else ""
        confirm_msg = (
            f"Delete {app.name}{account_info}?\n\n"
            f"All saved credentials and access tokens will be permanently deleted.\n"
            f"This action cannot be undone."
        )
        
        reply = QMessageBox.question(
            self, 
            "Confirm Delete",
            confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                ConnectedApplicationManager.delete_connected_app(self.session, app_id)
                logger.info(f"Deleted connected application: {app.name}")
                self.refresh_apps()
                QMessageBox.information(self, "Success", "Application deleted successfully!")
            except Exception as e:
                logger.error(f"Error deleting application: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete application: {str(e)}")
    
    def open_application(self, app_id: int):
        """Open/access a connected application"""
        import webbrowser
        
        app = ConnectedApplicationManager.get_connected_app(self.session, app_id)
        if not app:
            return
        
        url = app.login_url or app.website_url
        if not url:
            QMessageBox.information(
                self, "No URL",
                f"No website or login URL is saved for '{app.name}'.\n\n"
                "Click 'Edit' to add a Website URL or Login URL."
            )
            return
        
        if not url.startswith('http'):
            url = f'https://{url}'
        
        try:
            webbrowser.open(url)
            ConnectedApplicationManager.update_last_accessed(self.session, app_id)
            logger.info(f"Opened: {app.name} - {url}")
        except Exception as e:
            logger.error(f"Error opening URL: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open URL: {str(e)}")
    
    def copy_username(self, app_id: int):
        """Copy username to clipboard"""
        from PyQt6.QtWidgets import QApplication
        
        app = ConnectedApplicationManager.get_connected_app(self.session, app_id)
        if not app or not app.username:
            QMessageBox.warning(self, "No Username", "No username stored for this application")
            return
        
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(app.username)
            
            # FIXED: No plaintext shown in alert (Issue #1 - SECURITY)
            QMessageBox.information(self, "✓ Copied", "Username copied to clipboard securely.")
            logger.info(f"Copied username for: {app.name}")
        except Exception as e:
            logger.error(f"Error copying username: {e}")
            QMessageBox.critical(self, "Error", f"Failed to copy username: {str(e)}")
