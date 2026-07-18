"""
Professional modern stylesheet for ProJ Connect - Premium Design
"""

DARK_THEME = {
    "bg_primary": "#0d1117",      # Ultra dark background
    "bg_secondary": "#161b22",    # Dark surface
    "bg_tertiary": "#21262d",     # Lighter surface
    "bg_hover": "#30363d",        # Hover surface
    "accent_primary": "#58a6ff",  # Premium blue
    "accent_secondary": "#79c0ff", # Lighter blue
    "accent_light": "#6e40c9",    # Purple accent for variety
    "text_primary": "#ffffff",    # White
    "text_secondary": "#b0bbc9",  # Readable gray (WCAG AA compliant)
    "text_tertiary": "#6b7280",   # Darker gray (disabled only)
    "border_color": "#30363d",    # Subtle border
    "border_light": "#444c56",    # Light border
    "success": "#3fb950",         # Green
    "success_light": "#3fb950",
    "warning": "#d29922",         # Amber
    "error": "#f85149",           # Red
    "info": "#79c0ff",            # Light blue
    "surface_overlay": "rgba(22, 27, 34, 0.8)",  # Overlay
}

LIGHT_THEME = {
    "bg_primary": "#ffffff",
    "bg_secondary": "#f6f8fa",
    "bg_tertiary": "#eaeef2",
    "bg_hover": "#d0d7de",
    "accent_primary": "#0969da",
    "accent_secondary": "#0550ae",
    "accent_light": "#8250df",
    "text_primary": "#1f2328",
    "text_secondary": "#656d76",
    "text_tertiary": "#8b949e",
    "border_color": "#d0d7de",
    "border_light": "#afb8c1",
    "success": "#1a7f37",
    "success_light": "#1a7f37",
    "warning": "#9a6700",
    "error": "#cf222e",
    "info": "#0969da",
    "surface_overlay": "rgba(255, 255, 255, 0.85)",
}

THEMES = {"dark": DARK_THEME, "light": LIGHT_THEME}

_current_theme_name = "dark"


def set_current_theme(name: str):
    global _current_theme_name
    _current_theme_name = name if name in THEMES else "dark"


def get_current_theme_name() -> str:
    return _current_theme_name


def get_current_theme() -> dict:
    return THEMES.get(_current_theme_name, DARK_THEME)


def get_stylesheet(theme_name: str | None = None):
    """Generate QSS stylesheet for the application with premium design"""
    if theme_name is None:
        theme_name = _current_theme_name
    T = THEMES.get(theme_name, DARK_THEME)
    is_light = (theme_name == "light")

    # Derived colours for shell / status bar (light-theme aware)
    _shell_bg = (
        "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #f0f3f6,stop:0.55 #e8ecf0,stop:1 #dfe4ea)"
        if is_light else
        "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0f141b,stop:0.55 #0d1218,stop:1 #0a0f14)"
    )
    _shell_border = "#c8d1da" if is_light else "#1e2a38"
    _status_bg = (
        "qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 rgba(240,243,246,0.96),stop:1 rgba(230,234,238,0.99))"
        if is_light else
        "qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 rgba(18,24,34,0.96),stop:1 rgba(10,14,21,0.99))"
    )
    _main_bg = "#f6f8fa" if is_light else "#070b11"
    _status_label_color = "#57606a" if is_light else "#889ab3"

    style = f"""
    /* ======================== MAIN APPLICATION ======================== */
    QMainWindow {{
        background-color: {_main_bg};
        border: none;
    }}
    
    QWidget {{
        background-color: {T['bg_primary']};
        color: {T['text_primary']};
    }}
    
    QWidget#centralWidget {{
        background-color: {_main_bg};
    }}

    QFrame#appShell {{
        background: {_shell_bg};
        border: 1px solid {_shell_border};
        border-radius: 18px;
    }}

    QFrame#appBody {{
        background-color: transparent;
        border: none;
        border-top-left-radius: 17px;
        border-top-right-radius: 17px;
    }}

    QFrame#windowStatusBar {{
        background: {_status_bg};
        border: none;
        border-top: 1px solid {_shell_border};
        border-bottom-left-radius: 17px;
        border-bottom-right-radius: 17px;
    }}

    QLabel#windowStatusLabel {{
        color: {_status_label_color};
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.2px;
    }}
    
    /* ======================== CARDS & CONTAINERS ======================== */
    QFrame {{
        background-color: {T['bg_secondary']};
        border: 1px solid {T['border_color']};
        border-radius: 12px;
    }}
    
    QFrame#card {{
        background-color: {T['bg_secondary']};
        border: 1px solid {T['border_light']};
        border-radius: 10px;
        padding: 16px;
    }}
    
    QFrame#statCard {{
        background-color: {T['bg_tertiary']};
        border: 1px solid {T['border_color']};
        border-radius: 10px;
        padding: 20px;
    }}
    QFrame#statCard:hover {{
        background-color: #1b2026;
        border: 1px solid {T['accent_primary']};
    }}
    
    QFrame#statsFrame {{
        background-color: transparent;
    }}
    
    /* ======================== BUTTONS ======================== */
    QPushButton {{
        background-color: {T['accent_primary']};
        color: {T['text_primary']};
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 12px;
    }}
    
    QPushButton:hover {{
        background-color: {T['accent_secondary']};
        border: none;
    }}
    
    QPushButton:pressed {{
        background-color: {T['accent_light']};
    }}
    
    QPushButton:disabled {{
        background-color: {T['bg_tertiary']};
        color: {T['text_tertiary']};
    }}
    
    /* Secondary Button */
    QPushButton#secondaryButton {{
        background-color: transparent;
        color: {T['accent_primary']};
        border: 2px solid {T['accent_primary']};
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
    }}
    
    QPushButton#secondaryButton:hover {{
        background-color: {T['accent_primary']};
        color: {T['text_primary']};
        border: 2px solid {T['accent_primary']};
    }}
    
    /* Danger Button */
    QPushButton#dangerButton {{
        background-color: {T['error']};
        color: {T['text_primary']};
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }}
    
    QPushButton#dangerButton:hover {{
        background-color: #ff6b6b;
    }}
    
    /* Icon Buttons */
    QPushButton#iconButton {{
        background-color: transparent;
        color: {T['accent_primary']};
        border: none;
        border-radius: 6px;
        padding: 8px;
        font-size: 14px;
    }}
    
    QPushButton#iconButton:hover {{
        background-color: {T['bg_hover']};
    }}
    
    /* ======================== INPUT FIELDS ======================== */
    QLineEdit, QTextEdit {{
        background-color: {T['bg_tertiary']};
        color: {T['text_primary']};
        border: 1px solid {T['border_color']};
        border-radius: 10px;
        padding: 8px 12px;
        selection-background-color: {T['accent_primary']};
        font-size: 12px;
    }}
    
    QLineEdit:focus, QTextEdit:focus {{
        border: 2px solid {T['accent_primary']};
        padding: 7px 11px;
    }}
    
    /* Combo Box */
    QComboBox {{
        background-color: {T['bg_tertiary']};
        color: {T['text_primary']};
        border: 1px solid {T['border_color']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 11px;
    }}
    
    QComboBox::drop-down {{
        border: none;
        border-left: 1px solid {T['border_color']};
        width: 30px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {T['bg_tertiary']};
        color: {T['text_primary']};
        selection-background-color: {T['accent_primary']};
        border: 1px solid {T['border_color']};
        border-radius: 8px;
    }}
    
    /* ======================== CHECKBOXES & RADIO ======================== */
    QCheckBox {{
        color: {T['text_primary']};
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {T['border_light']};
    }}
    
    QCheckBox::indicator:hover {{
        border: 2px solid {T['accent_primary']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {T['accent_primary']};
        border: 2px solid {T['accent_primary']};
    }}
    
    /* Radio Button */
    QRadioButton {{
        color: {T['text_primary']};
        spacing: 8px;
    }}
    
    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 9px;
        border: 2px solid {T['border_light']};
    }}
    
    QRadioButton::indicator:hover {{
        border: 2px solid {T['accent_primary']};
    }}
    
    QRadioButton::indicator:checked {{
        background-color: {T['accent_primary']};
        border: 2px solid {T['accent_primary']};
    }}
    
    /* ======================== LABELS ======================== */
    QLabel {{
        color: {T['text_primary']};
        background-color: transparent;
        border: none;
        border-radius: 0px;
    }}
    
    QLabel#titleLabel {{
        font-size: 20px;
        font-weight: bold;
        color: {T['accent_primary']};
    }}
    
    QLabel#subtitleLabel {{
        font-size: 12px;
        color: {T['text_secondary']};
    }}

    QLabel#brandBadge {{
        color: {"#1f2328" if is_light else "#eef4ff"};
        background: {"rgba(9, 105, 218, 0.08)" if is_light else "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(255,255,255,0.08),stop:0.35 rgba(88,121,188,0.18),stop:1 rgba(14,20,33,0.3))"};
        border: 1px solid {"rgba(9, 105, 218, 0.20)" if is_light else "rgba(189, 211, 255, 0.30)"};
        min-width: 44px;
        min-height: 44px;
        border-radius: 14px;
        padding: 0px;
    }}

    QFrame#sidebarBrandPanel {{
        background: {"rgba(246, 248, 250, 0.9)" if is_light else "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(18,24,34,0.9),stop:1 rgba(12,17,24,0.96))"};
        border: 1px solid {"rgba(9, 105, 218, 0.12)" if is_light else "rgba(138, 174, 252, 0.12)"};
        border-radius: 14px;
    }}

    QLabel#sidebarBrandCaption {{
        color: {"#57606a" if is_light else "#7f93b0"};
        font-size: 9px;
        letter-spacing: 1.1px;
        font-weight: 700;
    }}

    QLabel#footerMetaLabel {{
        color: {"#656d76" if is_light else "#7f90a7"};
        font-size: 9px;
        font-weight: 500;
    }}

    QLabel#footerVersionLabel {{
        color: {"#1f2328" if is_light else "#dbe6fb"};
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.6px;
    }}
    
    QLabel#headingLabel {{
        font-size: 16px;
        font-weight: bold;
        color: {T['text_primary']};
    }}
    
    /* ======================== TABLES ======================== */
    QTableWidget, QTableView {{
        background-color: {T['bg_secondary']};
        alternate-background-color: {T['bg_tertiary']};
        gridline-color: {T['border_color']};
        border: 1px solid {T['border_color']};
        border-radius: 10px;
        font-size: 12px;
    }}
    
    QTableWidget::item {{
        padding: 14px 12px;
        border: none;
    }}
    
    QTableWidget::item:selected {{
        background-color: {T['accent_primary']};
        color: {T['text_primary']};
    }}
    
    QTableWidget::item:hover {{
        background-color: {T['bg_hover']};
    }}
    
    QHeaderView::section {{
        background-color: {T['bg_tertiary']};
        color: {T['text_primary']};
        padding: 10px 8px;
        border: none;
        border-bottom: 2px solid {T['border_color']};
        font-weight: bold;
        font-size: 11px;
    }}
        /* Focus outlines for accessibility */
        QPushButton:focus {{
            border: 2px solid {T['accent_primary']};
            outline: none;
        }}
    
        /* Corner button for tables */
        QTableCornerButton::section {{
            background-color: {T['bg_secondary']};
            border: none;
        }}
    
    /* ======================== SCROLL BARS ======================== */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 12px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {T['border_light']};
        border-radius: 6px;
        min-height: 28px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {T['accent_primary']};
    }}
    
    QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {{
        border: none;
        background: none;
    }}
    
    QScrollBar:horizontal {{
        border: none;
        background: transparent;
        height: 12px;
    }}
    
    QScrollBar::handle:horizontal {{
        background: {T['border_light']};
        border-radius: 6px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: {T['accent_primary']};
    }}
    
    /* ======================== MENUS ======================== */
    QMenuBar {{
        background-color: {T['bg_secondary']};
        color: {T['text_primary']};
        border-bottom: 1px solid {T['border_color']};
    }}
    
    QMenuBar::item:selected {{
        background-color: {T['accent_primary']};
        color: {T['text_primary']};
    }}
    
    QMenu {{
        background-color: {T['bg_secondary']};
        color: {T['text_primary']};
        border: 1px solid {T['border_color']};
        border-radius: 8px;
    }}
    
    QMenu::item:selected {{
        background-color: {T['accent_primary']};
        color: {T['text_primary']};
    }}
    
    /* ======================== TABS ======================== */
    QTabWidget::pane {{
        border: 1px solid {T['border_color']};
        border-radius: 8px;
    }}
    
    QTabBar::tab {{
        background-color: transparent;
        color: {T['text_secondary']};
        border: none;
        padding: 10px 16px;
        margin: 0 2px;
        font-weight: 600;
        font-size: 11px;
    }}
    
    QTabBar::tab:hover {{
        color: {T['accent_primary']};
    }}
    
    QTabBar::tab:selected {{
        background-color: transparent;
        color: {T['accent_primary']};
        border-bottom: 3px solid {T['accent_primary']};
    }}
    
    /* ======================== SPIN BOXES ======================== */
    QSpinBox, QDoubleSpinBox {{
        background-color: {T['bg_tertiary']};
        color: {T['text_primary']};
        border: 1px solid {T['border_color']};
        border-radius: 8px;
        padding: 6px;
        font-size: 11px;
    }}
    
    /* ======================== DATE/TIME ======================== */
    QDateEdit, QTimeEdit, QDateTimeEdit {{
        background-color: {T['bg_tertiary']};
        color: {T['text_primary']};
        border: 1px solid {T['border_color']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 11px;
    }}
    
    /* ======================== GROUP BOX ======================== */
    QGroupBox {{
        color: {T['text_primary']};
        border: 1px solid {T['border_color']};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 10px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 4px 0 4px;
        color: {T['accent_primary']};
        font-weight: bold;
    }}
    
    /* ======================== PROGRESS BAR ======================== */
    QProgressBar {{
        background-color: {T['bg_tertiary']};
        border: 1px solid {T['border_color']};
        border-radius: 6px;
        text-align: center;
        color: {T['text_primary']};
        height: 8px;
    }}
    
    QProgressBar::chunk {{
        background-color: {T['accent_primary']};
        border-radius: 6px;
    }}
    
    /* ======================== SPLITTER ======================== */
    QSplitter::handle {{
        background-color: {T['border_color']};
        border: none;
    }}
    
    QSplitter::handle:hover {{
        background-color: {T['accent_primary']};
    }}
    """
    
    return style
