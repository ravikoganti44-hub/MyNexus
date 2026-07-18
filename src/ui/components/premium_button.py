"""
Premium custom button component
"""
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from src.ui.styles.icon_manager import IconManager
from src.ui.styles.tokens import token


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
        self.setMinimumHeight(36)
        if not text or not text.strip():
            self.setFixedSize(36, 36)
        else:
            self.setMinimumWidth(100)

        if icon_name:
            try:
                color_map = {
                    self.Style.PRIMARY: token("color.text.inverse"),
                    self.Style.SECONDARY: token("color.accent.primary"),
                    self.Style.DANGER: token("color.text.inverse"),
                    self.Style.SUCCESS: token("color.text.inverse"),
                    self.Style.FLAT: token("color.text.tertiary"),
                    self.Style.GHOST_DANGER: token("color.semantic.high"),
                    self.Style.EDIT: token("color.accent.primary"),
                }
                color = color_map.get(style, token("color.accent.primary"))
                icon = IconManager.get_icon(icon_name, size=20, color=color)
                self.setIcon(icon)
                self.setIconSize(QSize(18, 18))
            except Exception:
                pass

        self._apply_style()

    def _apply_style(self):
        """Apply style based on button type"""
        c = token
        styles = {
            self.Style.PRIMARY: f"""
                QPushButton {{
                    background-color: {c("color.accent.bold")}; color: {c("color.text.inverse")};
                    border: none; border-radius: 8px; padding: 8px 16px;
                    font-weight: 600; font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {c("color.accent.hover")}; color: {c("color.text.inverse")};
                }}
                QPushButton:pressed {{
                    background-color: {c("color.accent.pressed")}; color: {c("color.text.inverse")};
                }}
                QPushButton:disabled {{
                    background-color: {c("color.border.default")}; color: {c("color.text.secondary")};
                }}
            """,
            self.Style.SECONDARY: f"""
                QPushButton {{
                    background-color: transparent; color: {c("color.accent.primary")};
                    border: 2px solid {c("color.accent.primary")}; border-radius: 8px;
                    padding: 6px 14px; font-weight: 600; font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {c("color.bg.hover")}; color: {c("color.accent.secondary")};
                    border-color: {c("color.accent.secondary")};
                }}
                QPushButton:pressed {{
                    background-color: {c("color.bg.hover")};
                }}
                QPushButton:disabled {{
                    border-color: {c("color.border.default")}; color: {c("color.text.secondary")};
                }}
            """,
            self.Style.DANGER: f"""
                QPushButton {{
                    background-color: {c("color.semantic.high")}; color: {c("color.text.inverse")};
                    border: none; border-radius: 8px; padding: 8px 16px;
                    font-weight: 600; font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {c("color.semantic.hover")}; color: {c("color.text.inverse")};
                }}
                QPushButton:pressed {{
                    background-color: {c("color.semantic.pressed")}; color: {c("color.text.inverse")};
                }}
                QPushButton:disabled {{
                    background-color: {c("color.border.default")}; color: {c("color.text.secondary")};
                }}
            """,
            self.Style.SUCCESS: f"""
                QPushButton {{
                    background-color: {c("color.semantic.success")}; color: {c("color.text.inverse")};
                    border: none; border-radius: 8px; padding: 8px 16px;
                    font-weight: 600; font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {c("color.semantic.success")}; color: {c("color.text.inverse")};
                }}
                QPushButton:pressed {{
                    background-color: {c("color.semantic.success")}; color: {c("color.text.inverse")};
                }}
                QPushButton:disabled {{
                    background-color: {c("color.border.default")}; color: {c("color.text.secondary")};
                }}
            """,
            self.Style.FLAT: f"""
                QPushButton {{
                    background-color: transparent; color: {c("color.text.tertiary")};
                    border: 1px solid {c("color.border.default")}; border-radius: 6px;
                    padding: 6px 12px; font-weight: 500; font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {c("color.bg.hover")}; color: {c("color.accent.primary")};
                    border-color: {c("color.accent.primary")};
                }}
                QPushButton:pressed {{
                    background-color: {c("color.bg.tertiary")}; color: {c("color.accent.primary")};
                }}
                QPushButton:disabled {{
                    color: {c("color.text.secondary")}; border-color: transparent;
                }}
            """,
            self.Style.GHOST_DANGER: f"""
                QPushButton {{
                    background-color: transparent; color: {c("color.semantic.high")};
                    border: 1px solid {c("color.semantic.high")}; border-radius: 6px;
                    padding: 6px 12px; font-weight: 500; font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: rgba(248, 113, 113, 0.15); color: {c("color.semantic.hover")};
                    border-color: {c("color.semantic.hover")};
                }}
                QPushButton:pressed {{
                    background-color: rgba(248, 113, 113, 0.25); color: {c("color.semantic.pressed")};
                }}
                QPushButton:disabled {{
                    color: {c("color.text.secondary")}; border-color: transparent;
                }}
            """,
            self.Style.EDIT: f"""
                QPushButton {{
                    background-color: {c("color.bg.hover")}; color: {c("color.accent.primary")};
                    border: 1px solid {c("color.accent.primary")}; border-radius: 6px;
                    padding: 6px 12px; font-weight: 600; font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {c("color.bg.hover")}; color: {c("color.accent.primary")};
                    border-color: {c("color.accent.secondary")};
                }}
                QPushButton:pressed {{
                    background-color: {c("color.bg.tertiary")}; color: {c("color.accent.primary")};
                }}
                QPushButton:disabled {{
                    color: {c("color.text.secondary")}; border-color: transparent;
                    background-color: transparent;
                }}
            """,
        }
        self.setStyleSheet(styles.get(self.button_style, styles[self.Style.PRIMARY]))

    def set_style(self, style: str):
        """Change button style"""
        self.button_style = style
        self._apply_style()
