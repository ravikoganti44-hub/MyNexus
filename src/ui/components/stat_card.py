"""
Premium stat card component for dashboard
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPixmap
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation

from src.ui.styles.tokens import token as _tok
from src.ui.styles.icon_manager import IconManager


class StatCard(QFrame):
    """Premium stat card widget"""

    def __init__(self, title: str, value: str, icon_text: str = "", color: str = _tok("color.accent.primary"), icon_name: str = None):
        super().__init__()
        self.color = color
        self.setObjectName("statCard")
        self._setup_ui(title, value, icon_text, icon_name)

    def _setup_ui(self, title: str, value: str, icon_text: str, icon_name: str = None):
        """Setup stat card UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        header_layout = QHBoxLayout()

        if icon_name:
            try:
                icon = IconManager.get_icon(icon_name, size=20, color=self.color)
                icon_label = QLabel()
                icon_label.setPixmap(icon.pixmap(20, 20))
                icon_label.setFixedWidth(32)
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                header_layout.addWidget(icon_label)
            except Exception:
                # Fallback to emoji if icon fails
                if icon_text:
                    fallback = QLabel(icon_text)
                    fallback.setFont(QFont("Segoe UI", 16))
                    fallback.setFixedWidth(32)
                    header_layout.addWidget(fallback)
        elif icon_text:
            icon_label = QLabel(icon_text)
            icon_label.setFont(QFont("Segoe UI", 16))
            icon_label.setFixedWidth(32)
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        title_label.setStyleSheet(f"color: {_tok('color.text.secondary')};")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {self.color};")
        layout.addWidget(value_label)
        
        border_frame = QFrame()
        border_frame.setFixedHeight(3)
        border_frame.setStyleSheet(f"background-color: {self.color}; border-radius: 1px;")
        layout.addWidget(border_frame)
        
        self.setLayout(layout)
        
        self.value_label = value_label
        self.title_label = title_label
    
    def set_value(self, value: str):
        self.value_label.setText(value)
    
    def set_color(self, color: str):
        self.color = color
        self.value_label.setStyleSheet(f"color: {color};")

    def enterEvent(self, event):
        """Add subtle elevation on hover"""
        try:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(18)
            shadow.setOffset(0, 6)
            shadow.setColor(QColor(0, 0, 0, 140))
            self.setGraphicsEffect(shadow)
        except Exception:
            pass
        return super().enterEvent(event)

    def leaveEvent(self, event):
        """Remove elevation when not hovered"""
        try:
            self.setGraphicsEffect(None)
        except Exception:
            pass
        return super().leaveEvent(event)
