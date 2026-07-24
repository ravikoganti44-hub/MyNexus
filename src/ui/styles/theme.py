"""
MyNexus Theme Engine
--------------------
Generates QSS from THEME_TOKEN_MAP and keeps one source of truth.
"""

from src.ui.styles.tokens import get_tokens, THEME_TOKEN_MAP


_DARK_SHELL_BG = (
    "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0f141b,stop:0.55 #0d1218,stop:1 #0a0f14)"
)
_LIGHT_SHELL_BG = (
    "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #f0f3f6,stop:0.55 #e8ecf0,stop:1 #dfe4ea)"
)
_DARK_SHELL_BORDER = "#1e2a38"
_LIGHT_SHELL_BORDER = "#c8d1da"
_DARK_STATUS_BG = (
    "qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 rgba(18,24,34,0.96),stop:1 rgba(10,14,21,0.99))"
)
_LIGHT_STATUS_BG = (
    "qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 rgba(240,243,246,0.96),stop:1 rgba(230,234,238,0.99))"
)
_DARK_MAIN_BG = "#070b11"
_LIGHT_MAIN_BG = "#f6f8fa"
_DARK_STATUS_LABEL = "#889ab3"
_LIGHT_STATUS_LABEL = "#57606a"


def _shell_values(theme_name: str):
    is_light = theme_name == "light"
    return {
        "bg": _LIGHT_SHELL_BG if is_light else _DARK_SHELL_BG,
        "border": _LIGHT_SHELL_BORDER if is_light else _DARK_SHELL_BORDER,
        "status_bg": _LIGHT_STATUS_BG if is_light else _DARK_STATUS_BG,
        "main_bg": _LIGHT_MAIN_BG if is_light else _DARK_MAIN_BG,
        "status_label": _LIGHT_STATUS_LABEL if is_light else _DARK_STATUS_LABEL,
        "is_light": is_light,
    }


def get_stylesheet(theme_name: str | None = None) -> str:
    tokens = get_tokens(theme_name)
    sv = _shell_values(theme_name or "dark")

    return f"""\
/* ======================== MAIN APPLICATION ======================== */
QMainWindow {{
    background-color: {sv['main_bg']};
    border: none;
}}

QWidget {{
    background-color: {tokens["color.bg.primary"]};
    color: {tokens["color.text.primary"]};
}}

QWidget#centralWidget {{
    background-color: {sv['main_bg']};
}}

QFrame#appShell {{
    background: {sv['bg']};
    border: 1px solid {sv['border']};
    border-top: 2px solid {tokens["color.accent.primary"]};
    border-radius: {tokens["radius.xl"]};
}}

QFrame#appBody {{
    background-color: transparent;
    border: none;
    border-top-left-radius: {tokens["radius.xl"]};
    border-top-right-radius: {tokens["radius.xl"]};
}}

QFrame#windowStatusBar {{
    background: {sv['status_bg']};
    border: none;
    border-top: 1px solid {sv['border']};
    border-bottom-left-radius: {tokens["radius.xl"]};
    border-bottom-right-radius: {tokens["radius.xl"]};
}}

QLabel#windowStatusLabel {{
    color: {sv['status_label']};
    font-size: {tokens["type.scale.caption"]};
    font-weight: {tokens["type.weight.semibold"]};
    letter-spacing: 0.2px;
}}

/* ======================== CARDS & CONTAINERS ======================== */
QFrame {{
    background-color: {tokens["color.bg.secondary"]};
    border: 1px solid {tokens["color.border.default"]};
    border-radius: {tokens["radius.lg"]};
}}

QFrame#card {{
    background-color: {tokens["color.bg.secondary"]};
    border: 1px solid {tokens["color.border.light"]};
    border-radius: {tokens["radius.md"]};
    padding: {tokens["space.4"]};
}}

QFrame#statCard {{
    background-color: {tokens["color.bg.tertiary"]};
    border: 1px solid {tokens["color.border.default"]};
    border-radius: {tokens["radius.md"]};
    padding: {tokens["space.5"]};
}}
QFrame#statCard:hover {{
    background-color: {tokens["color.bg.hover"]};
    border: 1px solid {tokens["color.accent.primary"]};
}}

QFrame#statsFrame {{
    background-color: transparent;
}}

/* ======================== BUTTONS ======================== */
QPushButton {{
    background-color: {tokens["color.accent.primary"]};
    color: {tokens["color.text.inverse"]};
    border: none;
    border-radius: {tokens["radius.md"]};
    padding: {tokens["space.3"]} {tokens["space.5"]};
    font-weight: {tokens["type.weight.semibold"]};
    font-size: {tokens["type.scale.body"]};
}}

QPushButton:hover {{
    background-color: {tokens["color.accent.secondary"]};
    border: none;
}}

QPushButton:pressed {{
    background-color: {tokens["color.accent.light"]};
}}

QPushButton:disabled {{
    background-color: {tokens["color.bg.tertiary"]};
    color: {tokens["color.text.tertiary"]};
}}

/* Secondary Button */
QPushButton#secondaryButton {{
    background-color: transparent;
    color: {tokens["color.accent.primary"]};
    border: 2px solid {tokens["color.accent.primary"]};
    border-radius: {tokens["radius.md"]};
    padding: {tokens["space.2"]} {tokens["space.4"]};
    font-weight: {tokens["type.weight.semibold"]};
}}

QPushButton#secondaryButton:hover {{
    background-color: {tokens["color.accent.primary"]};
    color: {tokens["color.text.inverse"]};
    border: 2px solid {tokens["color.accent.primary"]};
}}

/* Danger Button */
QPushButton#dangerButton {{
    background-color: {tokens["color.semantic.error"]};
    color: {tokens["color.text.inverse"]};
    border: none;
    border-radius: {tokens["radius.md"]};
    padding: {tokens["space.3"]} {tokens["space.5"]};
    font-weight: {tokens["type.weight.semibold"]};
}}

QPushButton#dangerButton:hover {{
    background-color: #ff6b6b;
}}

/* Icon Buttons */
QPushButton#iconButton {{
    background-color: transparent;
    color: {tokens["color.accent.primary"]};
    border: none;
    border-radius: {tokens["radius.sm"]};
    padding: {tokens["space.2"]};
    font-size: 14px;
}}

QPushButton#iconButton:hover {{
    background-color: {tokens["color.bg.hover"]};
}}

/* ======================== INPUT FIELDS ======================== */
QLineEdit, QTextEdit {{
    background-color: {tokens["color.bg.tertiary"]};
    color: {tokens["color.text.primary"]};
    border: 1px solid {tokens["color.border.default"]};
    border-radius: {tokens["radius.md"]};
    padding: 8px 12px;
    selection-background-color: {tokens["color.accent.primary"]};
    font-size: {tokens["type.scale.body"]};
}}

QLineEdit:focus, QTextEdit:focus {{
    border: 2px solid {tokens["color.accent.primary"]};
    padding: 7px 11px;
}}

/* Combo Box */
QComboBox {{
    background-color: {tokens["color.bg.tertiary"]};
    color: {tokens["color.text.primary"]};
    border: 1px solid {tokens["color.border.default"]};
    border-radius: {tokens["radius.md"]};
    padding: 8px 12px;
    font-size: {tokens["type.scale.body"]};
}}

QComboBox::drop-down {{
    border: none;
    border-left: 1px solid {tokens["color.border.default"]};
    width: 30px;
}}

QComboBox QAbstractItemView {{
    background-color: {tokens["color.bg.tertiary"]};
    color: {tokens["color.text.primary"]};
    selection-background-color: {tokens["color.accent.primary"]};
    border: 1px solid {tokens["color.border.default"]};
    border-radius: {tokens["radius.md"]};
}}

/* ======================== CHECKBOXES & RADIO ======================== */
QCheckBox {{
    color: {tokens["color.text.primary"]};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid {tokens["color.border.light"]};
}}

QCheckBox::indicator:hover {{
    border: 2px solid {tokens["color.accent.primary"]};
}}

QCheckBox::indicator:checked {{
    background-color: {tokens["color.accent.primary"]};
    border: 2px solid {tokens["color.accent.primary"]};
}}

/* Radio Button */
QRadioButton {{
    color: {tokens["color.text.primary"]};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid {tokens["color.border.light"]};
}}

QRadioButton::indicator:hover {{
    border: 2px solid {tokens["color.accent.primary"]};
}}

QRadioButton::indicator:checked {{
    background-color: {tokens["color.accent.primary"]};
    border: 2px solid {tokens["color.accent.primary"]};
}}

/* ======================== LABELS ======================== */
QLabel {{
    color: {tokens["color.text.primary"]};
    background-color: transparent;
    border: none;
    border-radius: 0px;
}}

QLabel#titleLabel {{
    font-size: {tokens["type.scale.h1"]};
    font-weight: {tokens["type.weight.bold"]};
    color: {tokens["color.accent.primary"]};
}}

QLabel#subtitleLabel {{
    font-size: {tokens["type.scale.body"]};
    color: {tokens["color.text.secondary"]};
}}

QLabel#brandBadge {{
    color: {"#1f2328" if sv['is_light'] else "#eef4ff"};
    background: {"rgba(9, 105, 218, 0.08)" if sv['is_light'] else "rgba(255,255,255,0.08)"};
    border: 1px solid {"rgba(9, 105, 218, 0.20)" if sv['is_light'] else "rgba(189,211,255,0.30)"};
    min-width: 44px;
    min-height: 44px;
    border-radius: {tokens["radius.lg"]};
    padding: 0px;
}}

QFrame#sidebarBrandPanel {{
    background: {"rgba(246, 248, 250, 0.9)" if sv['is_light'] else "rgba(18,24,34,0.9)"};
    border: 1px solid {"rgba(9, 105, 218, 0.12)" if sv['is_light'] else "rgba(138, 174, 252, 0.12)"};
    border-radius: {tokens["radius.lg"]};
}}

QLabel#sidebarBrandCaption {{
    color: {"#57606a" if sv['is_light'] else "#7f93b0"};
    font-size: {tokens["type.scale.caption"]};
    letter-spacing: 1.1px;
    font-weight: {tokens["type.weight.bold"]};
}}

QLabel#footerMetaLabel {{
    color: {"#656d76" if sv['is_light'] else "#7f90a7"};
    font-size: {tokens["type.scale.caption"]};
    font-weight: {tokens["type.weight.medium"]};
}}

QLabel#footerVersionLabel {{
    color: {"#1f2328" if sv['is_light'] else "#dbe6fb"};
    font-size: {tokens["type.scale.caption"]};
    font-weight: {tokens["type.weight.bold"]};
    letter-spacing: 0.6px;
}}

QLabel#headingLabel {{
    font-size: {tokens["type.scale.h2"]};
    font-weight: {tokens["type.weight.bold"]};
    color: {tokens["color.text.primary"]};
}}

/* ======================== TABLES ======================== */
QTableWidget, QTableView {{
    background-color: {tokens["color.bg.secondary"]};
    alternate-background-color: {tokens["color.bg.tertiary"]};
    gridline-color: {tokens["color.border.default"]};
    border: 1px solid {tokens["color.border.default"]};
    border-radius: {tokens["radius.lg"]};
    font-size: {tokens["type.scale.body"]};
}}

QTableWidget::item {{
    padding: 12px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {tokens["color.accent.primary"]};
    color: {tokens["color.text.primary"]};
}}

QTableWidget::item:hover {{
    background-color: {tokens["color.bg.hover"]};
}}

QHeaderView::section {{
    background-color: {tokens["color.bg.tertiary"]};
    color: {tokens["color.text.primary"]};
    padding: 10px 8px;
    border: none;
    border-bottom: 2px solid {tokens["color.border.default"]};
    font-weight: {tokens["type.weight.bold"]};
    font-size: {tokens["type.scale.caption"]};
}}

QPushButton:focus {{
    border: 2px solid {tokens["color.accent.primary"]};
    outline: none;
}}

QTableCornerButton::section {{
    background-color: {tokens["color.bg.secondary"]};
    border: none;
}}

/* ======================== SCROLL BARS ======================== */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 12px;
}}

QScrollBar::handle:vertical {{
    background: {tokens["color.border.light"]};
    border-radius: 6px;
    min-height: 28px;
}}

QScrollBar::handle:vertical:hover {{
    background: {tokens["color.accent.primary"]};
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
    background: {tokens["color.border.light"]};
    border-radius: 6px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {tokens["color.accent.primary"]};
}}

/* ======================== MENUS ======================== */
QMenuBar {{
    background-color: {tokens["color.bg.secondary"]};
    color: {tokens["color.text.primary"]};
    border-bottom: 1px solid {tokens["color.border.default"]};
}}

QMenuBar::item:selected {{
    background-color: {tokens["color.accent.primary"]};
    color: {tokens["color.text.primary"]};
}}

QMenu {{
    background-color: {tokens["color.bg.secondary"]};
    color: {tokens["color.text.primary"]};
    border: 1px solid {tokens["color.border.default"]};
    border-radius: {tokens["radius.md"]};
}}

QMenu::item:selected {{
    background-color: {tokens["color.accent.primary"]};
    color: {tokens["color.text.primary"]};
}}

/* ======================== TABS ======================== */
QTabWidget::pane {{
    border: 1px solid {tokens["color.border.default"]};
    border-radius: {tokens["radius.md"]};
}}

QTabBar::tab {{
    background-color: {tokens["color.bg.secondary"]};
    color: {tokens["color.text.tertiary"]};
    border: none;
    border-bottom: 2px solid transparent;
    padding: {tokens["space.3"]} {tokens["space.4"]};
    margin: 0 2px;
    font-weight: {tokens["type.weight.semibold"]};
    font-size: {tokens["type.scale.caption"]};
}}

QTabBar::tab:hover {{
    color: {tokens["color.text.primary"]};
    border-bottom-color: {tokens["color.border.light"]};
}}

QTabBar::tab:selected {{
    color: {tokens["color.accent.primary"]};
    border-bottom-color: {tokens["color.accent.primary"]};
}}

/* ======================== SPIN BOXES ======================== */
QSpinBox, QDoubleSpinBox {{
    background-color: {tokens["color.bg.tertiary"]};
    color: {tokens["color.text.primary"]};
    border: 1px solid {tokens["color.border.default"]};
    border-radius: {tokens["radius.md"]};
    padding: 6px;
    font-size: {tokens["type.scale.body"]};
}}

/* ======================== DATE/TIME ======================== */
QDateEdit, QTimeEdit, QDateTimeEdit {{
    background-color: {tokens["color.bg.tertiary"]};
    color: {tokens["color.text.primary"]};
    border: 1px solid {tokens["color.border.default"]};
    border-radius: {tokens["radius.md"]};
    padding: 8px 12px;
    font-size: {tokens["type.scale.body"]};
}}

/* ======================== GROUP BOX ======================== */
QGroupBox {{
    color: {tokens["color.text.primary"]};
    border: 1px solid {tokens["color.border.default"]};
    border-radius: {tokens["radius.md"]};
    margin-top: 12px;
    padding-top: 10px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px 0 4px;
    color: {tokens["color.accent.primary"]};
    font-weight: {tokens["type.weight.bold"]};
}}

/* ======================== PROGRESS BAR ======================== */
QProgressBar {{
    background-color: {tokens["color.bg.tertiary"]};
    border: 1px solid {tokens["color.border.default"]};
    border-radius: 6px;
    text-align: center;
    color: {tokens["color.text.primary"]};
    height: 8px;
}}

QProgressBar::chunk {{
    background-color: {tokens["color.accent.primary"]};
    border-radius: 6px;
}}

/* ======================== SPLITTER ======================== */
QSplitter::handle {{
    background-color: {tokens["color.border.default"]};
    border: none;
}}

QSplitter::handle:hover {{
    background-color: {tokens["color.accent.primary"]};
}}
"""
