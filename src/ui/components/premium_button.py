"""
Premium custom button component
"""
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from src.ui.styles.icon_manager import IconManager


class PremiumButton(QPushButton):
    """A premium styled button with customizable appearance"""
    
    class Style:
        PRIMARY = "primary"
        SECONDARY = "secondary"
        DANGER = "danger"
        SUCCESS = "success"
        FLAT = "flat"
        GHOST_DANGER = "ghost_danger"
        EDIT = "edit"
    
    def __init__(self, text: str = "", style: str = "primary", icon_name: str = None):
        super().__init__(text)
        self.button_style = style
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        # Set minimum height
        self.setMinimumHeight(36)
        # If this is an icon-only button (no text) use compact sizing
        if not text or not text.strip():
            # compact square icon button
            self.setFixedSize(36, 36)
        else:
            self.setMinimumWidth(100)

        # Add icon if provided
        if icon_name:
            try:
                color_map = {
                    self.Style.PRIMARY: "#ffffff",
                    self.Style.SECONDARY: "#58a6ff",
                    self.Style.DANGER: "#ffffff",
                    self.Style.SUCCESS: "#ffffff",
                    self.Style.FLAT: "#c5ccd6",
                    self.Style.GHOST_DANGER: "#f87171",
                    self.Style.EDIT: "#58a6ff",
                }
                color = color_map.get(style, "#58a6ff")
                icon = IconManager.get_icon(icon_name, size=20, color=color)
                self.setIcon(icon)
                self.setIconSize(QSize(18, 18))
            except:
                pass
        
        # Apply style
        self._apply_style()
    
    def _apply_style(self):
        """Apply style based on button type"""
        styles = {
            self.Style.PRIMARY: """
                QPushButton {
                    background-color: #2563eb;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #3b82f6;
                    color: #ffffff;
                }
                QPushButton:pressed {
                    background-color: #1d4ed8;
                    color: #ffffff;
                }
                QPushButton:disabled {
                    background-color: #30363d;
                    color: #6b7280;
                }
            """,
            self.Style.SECONDARY: """
                QPushButton {
                    background-color: transparent;
                    color: #58a6ff;
                    border: 2px solid #58a6ff;
                    border-radius: 8px;
                    padding: 6px 14px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: rgba(88, 166, 255, 0.1);
                    border: 2px solid #79c0ff;
                    color: #79c0ff;
                }
                QPushButton:pressed {
                    background-color: rgba(88, 166, 255, 0.2);
                }
                QPushButton:disabled {
                    border: 2px solid #30363d;
                    color: #6b7280;
                }
            """,
            self.Style.DANGER: """
                QPushButton {
                    background-color: #dc2626;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #ef4444;
                    color: #ffffff;
                }
                QPushButton:pressed {
                    background-color: #b91c1c;
                    color: #ffffff;
                }
                QPushButton:disabled {
                    background-color: #30363d;
                    color: #6b7280;
                }
            """,
            self.Style.SUCCESS: """
                QPushButton {
                    background-color: #16a34a;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #22c55e;
                    color: #ffffff;
                }
                QPushButton:pressed {
                    background-color: #15803d;
                    color: #ffffff;
                }
                QPushButton:disabled {
                    background-color: #30363d;
                    color: #6b7280;
                }
            """,
            self.Style.FLAT: """
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.05);
                    color: #c5ccd6;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: rgba(88, 166, 255, 0.15);
                    color: #79c0ff;
                    border: 1px solid rgba(88, 166, 255, 0.3);
                }
                QPushButton:pressed {
                    background-color: rgba(88, 166, 255, 0.25);
                    color: #58a6ff;
                }
                QPushButton:disabled {
                    color: #6b7280;
                    border: 1px solid transparent;
                }
            """,
            self.Style.GHOST_DANGER: """
                QPushButton {
                    background-color: transparent;
                    color: #f87171;
                    border: 1px solid rgba(248, 113, 113, 0.35);
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: rgba(248, 113, 113, 0.15);
                    color: #ef4444;
                    border: 1px solid rgba(248, 113, 113, 0.6);
                }
                QPushButton:pressed {
                    background-color: rgba(248, 113, 113, 0.25);
                    color: #dc2626;
                }
                QPushButton:disabled {
                    color: #6b7280;
                    border: 1px solid transparent;
                }
            """,
            self.Style.EDIT: """
                QPushButton {
                    background-color: rgba(88, 166, 255, 0.08);
                    color: #58a6ff;
                    border: 1px solid rgba(88, 166, 255, 0.45);
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: rgba(88, 166, 255, 0.18);
                    color: #79c0ff;
                    border: 1px solid rgba(88, 166, 255, 0.75);
                }
                QPushButton:pressed {
                    background-color: rgba(88, 166, 255, 0.28);
                    color: #58a6ff;
                }
                QPushButton:disabled {
                    color: #6b7280;
                    border: 1px solid transparent;
                    background-color: transparent;
                }
            """,
        }
        
        self.setStyleSheet(styles.get(self.button_style, styles[self.Style.PRIMARY]))
    
    def set_style(self, style: str):
        """Change button style"""
        self.button_style = style
        self._apply_style()
