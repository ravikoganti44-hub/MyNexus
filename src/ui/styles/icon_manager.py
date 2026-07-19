"""
Icon manager for handling SVG and other icons throughout the application
"""
from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, QByteArray, QRectF

from src.ui.styles.tokens import token

try:
    from PyQt6.QtSvg import QSvgRenderer
except ImportError:  # pragma: no cover - optional dependency in some environments
    QSvgRenderer = None


class IconManager:
    """Manager for application icons"""
    
    # Icon paths
    ICON_DIR = Path(__file__).resolve().parents[3] / "assets" / "icons"
    
    # Available icons
    ICONS = {
        "my_nexus": "my_nexus.svg",
        "dashboard": "dashboard.svg",
        "activities": "activities.svg",
        "integrations": "integrations.svg",
        "connected_apps": "connected_apps.svg",
        "document_vault": "document_vault.svg",
        "settings": "settings.svg",
        "refresh": "refresh.svg",
        "add": "add.svg",
        "delete": "delete.svg",
        "edit": "edit.svg",
        "calendar": "calendar.svg",
        "warning": "warning.svg",
        "check": "check.svg",
        "error": "error.svg",
        "search": "search.svg",
        "close": "close.svg",
        "menu": "menu.svg",
        "download": "download.svg",
        "upload": "upload.svg",
        "save": "save.svg",
        "mail": "mail.svg",
        "budget": "budget.svg",
        "net_worth": "net_worth.svg",
        "calendar_view": "calendar.svg",
    }
    
    @classmethod
    def get_icon(cls, icon_name: str, size: int = 24, color: str = "#00d4ff") -> QIcon:
        """
        Get a colored icon by name
        
        Args:
            icon_name: Name of the icon (key from ICONS dict)
            size: Size of the icon in pixels
            color: Color for the icon (hex format)
            
        Returns:
            QIcon object
        """
        if icon_name not in cls.ICONS:
            return QIcon()
        
        icon_path = cls.ICON_DIR / cls.ICONS[icon_name]
        
        if not icon_path.exists():
            return QIcon()

        with open(icon_path, 'r', encoding='utf-8') as f:
            svg_content = f.read().replace('currentColor', color)

        if QSvgRenderer is not None:
            renderer = QSvgRenderer(QByteArray(svg_content.encode('utf-8')))
            if renderer.isValid():
                pixmap = QPixmap(size, size)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                try:
                    renderer.render(painter, QRectF(0, 0, size, size))
                finally:
                    painter.end()
                return QIcon(pixmap)

        return QIcon(str(icon_path))
    
    @classmethod
    def get_icon_path(cls, icon_name: str) -> str:
        """
        Get the file path of an icon
        
        Args:
            icon_name: Name of the icon
            
        Returns:
            Full path to the icon file
        """
        if icon_name not in cls.ICONS:
            return ""
        
        icon_path = cls.ICON_DIR / cls.ICONS[icon_name]
        return str(icon_path) if icon_path.exists() else ""


# Preload common icons with primary accent color
ICON_PRIMARY = lambda name: IconManager.get_icon(name, size=24, color=token("color.accent.primary"))
ICON_SECONDARY = lambda name: IconManager.get_icon(name, size=24, color=token("color.accent.secondary"))
ICON_SUCCESS = lambda name: IconManager.get_icon(name, size=24, color=token("color.semantic.success"))
ICON_WARNING = lambda name: IconManager.get_icon(name, size=24, color=token("color.semantic.warning"))
ICON_ERROR = lambda name: IconManager.get_icon(name, size=24, color=token("color.semantic.error"))
ICON_WHITE = lambda name: IconManager.get_icon(name, size=24, color=token("color.text.inverse"))
ICON_GRAY = lambda name: IconManager.get_icon(name, size=24, color=token("color.text.muted"))
