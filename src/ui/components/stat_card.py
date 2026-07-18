"""
Premium stat card component for dashboard
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation


class StatCard(QFrame):
    """Premium stat card widget"""
    
    def __init__(self, title: str, value: str, icon_text: str = "", color: str = "#58a6ff"):
        super().__init__()
        self.color = color
        self.setObjectName("statCard")
        self._setup_ui(title, value, icon_text)
    
    def _setup_ui(self, title: str, value: str, icon_text: str):
        """Setup stat card UI"""
        layout = QVBoxLayout()
        # Slightly tighter padding for compact stat presentation
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        
        # Icon and title row
        header_layout = QHBoxLayout()
        
        if icon_text:
            icon_label = QLabel(icon_text)
            icon_label.setFont(QFont("Segoe UI", 16))
            icon_label.setFixedWidth(32)
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        title_label.setStyleSheet("color: #a0adb8;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {self.color};")
        layout.addWidget(value_label)
        
        # Bottom border accent
        border_frame = QFrame()
        border_frame.setFixedHeight(3)
        border_frame.setStyleSheet(f"background-color: {self.color}; border-radius: 1px;")
        layout.addWidget(border_frame)
        
        self.setLayout(layout)
        
        # Store references for updates
        self.value_label = value_label
        self.title_label = title_label
    
    def set_value(self, value: str):
        """Update the value displayed"""
        self.value_label.setText(value)
    
    def set_color(self, color: str):
        """Update the color accent"""
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
