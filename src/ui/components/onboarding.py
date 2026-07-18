"""
Onboarding wizard for first-time users and master passphrase dialog.
Passphrase setup is optional and offered at the end of onboarding,
not forced on first launch.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QStackedWidget, QWidget, QFrame, QMessageBox,
    QCheckBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QIcon

from src.ui.styles.tokens import token as _tok
from src.ui.styles.tokens import spacing as _sp

from src.core.encryption import (
    is_passphrase_set, verify_passphrase, save_key_check, init_encryption
)


def _apply_token_style(widget, palette):
    """Apply token-backed stylesheet to a generic dialog/wizard container."""
    widget.setStyleSheet(f"""
        QDialog, QWidget {{
            background-color: {palette["bg.primary"]};
            color: {palette["text.primary"]};
        }}
        QLineEdit {{
            background-color: {palette["bg.secondary"]};
            color: {palette["text.primary"]};
            border: 1px solid {palette["border.default"]};
            border-radius: {palette["radius.md"]};
            padding: 8px 12px;
            font-size: 13px;
        }}
        QLineEdit:focus {{ border-color: {palette["accent.primary"]}; }}
        QCheckBox {{ color: {palette["text.secondary"]}; font-size: 10px; }}
    """)

_PALETTE = {
    "bg.primary": _tok("color.bg.primary"),
    "bg.secondary": _tok("color.bg.secondary"),
    "text.primary": _tok("color.text.primary"),
    "text.secondary": _tok("color.text.secondary"),
    "border.default": _tok("color.border.default"),
    "radius.md": _tok("radius.md"),
    "accent.primary": _tok("color.accent.primary"),
    "accent.secondary": _tok("color.accent.secondary"),
}


class MasterPassphraseDialog(QDialog):
    """Dialog for entering or creating a master passphrase."""

    def __init__(self, parent=None, first_time: bool = False):
        super().__init__(parent)
        self._first_time = first_time
        self._passphrase: str | None = None
        self.setWindowTitle("MyNexus — Unlock")
        self.setFixedSize(460, 320 if first_time else 240)
        _apply_token_style(self, _PALETTE)
        self._setup_ui()

    @property
    def passphrase(self) -> str | None:
        return self._passphrase

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(_sp("space.gap.sm"))

        # Title
        title = QLabel("Create Master Passphrase" if self._first_time else "Unlock MyNexus")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {_PALETTE['accent.primary']};")
        layout.addWidget(title)

        if self._first_time:
            hint = QLabel(
                "Choose a strong passphrase to protect your passwords and "
                "sensitive data. You can also enable this later from Settings → Security."
            )
            hint.setWordWrap(True)
            hint.setFont(QFont("Segoe UI", 9))
            hint.setStyleSheet(f"color: {_PALETTE['text.secondary']};")
            layout.addWidget(hint)

        # Passphrase input
        self._input = QLineEdit()
        self._input.setPlaceholderText("Enter passphrase…")
        self._input.setEchoMode(QLineEdit.EchoMode.Password)
        self._input.setMinimumHeight(38)
        self._input.returnPressed.connect(self._on_submit)
        layout.addWidget(self._input)

        if self._first_time:
            self._confirm_input = QLineEdit()
            self._confirm_input.setPlaceholderText("Confirm passphrase…")
            self._confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self._confirm_input.setMinimumHeight(38)
            self._confirm_input.returnPressed.connect(self._on_submit)
            layout.addWidget(self._confirm_input)

        # Show password toggle
        show_cb = QCheckBox("Show passphrase")
        show_cb.toggled.connect(self._toggle_vis)
        layout.addWidget(show_cb)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        submit = QPushButton("Create" if self._first_time else "Unlock")
        submit.setFixedSize(120, 36)
        submit.setCursor(Qt.CursorShape.PointingHandCursor)
        submit.setStyleSheet(
            f"QPushButton {{ background-color: {_PALETTE['accent.primary']}; color: #fff; border: none; "
            f"border-radius: {_PALETTE['radius.md']}; font-weight: bold; }} "
            f"QPushButton:hover {{ background-color: {_PALETTE['accent.secondary']}; }}"
        )
        submit.clicked.connect(self._on_submit)
        btn_row.addWidget(submit)

        if not self._first_time:
            skip = QPushButton("Skip")
            skip.setFixedSize(80, 36)
            skip.setCursor(Qt.CursorShape.PointingHandCursor)
            skip.setStyleSheet(
                f"QPushButton {{ background-color: transparent; color: {_PALETTE['text.secondary']}; "
                f"border: 1px solid {_PALETTE['border.default']}; border-radius: {_PALETTE['radius.md']}; }} "
                f"QPushButton:hover {{ background-color: {_PALETTE['bg.secondary']}; }}"
            )
            skip.clicked.connect(self.reject)
            btn_row.addWidget(skip)

        layout.addLayout(btn_row)
        self._input.setFocus()

    def _toggle_vis(self, checked: bool):
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self._input.setEchoMode(mode)
        if self._first_time:
            self._confirm_input.setEchoMode(mode)

    def _on_submit(self):
        passphrase = self._input.text().strip()
        if len(passphrase) < 4:
            QMessageBox.warning(self, "Too short", "Passphrase must be at least 4 characters.")
            return

        if self._first_time:
            confirm = self._confirm_input.text().strip()
            if passphrase != confirm:
                QMessageBox.warning(self, "Mismatch", "Passphrases do not match.")
                return
            save_key_check(passphrase)
            init_encryption(passphrase)
            self._passphrase = passphrase
            self.accept()
        else:
            if verify_passphrase(passphrase):
                init_encryption(passphrase)
                self._passphrase = passphrase
                self.accept()
            else:
                QMessageBox.warning(self, "Wrong passphrase", "The passphrase is incorrect. Try again.")
                self._input.clear()
                self._input.setFocus()


class OnboardingWizard(QDialog):
    """Multi-step welcome wizard for first-time users."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to MyNexus")
        self.setFixedSize(620, 480)
        _apply_token_style(self, _PALETTE)
        self.setStyleSheet(f"""
            QDialog, QWidget {{
                background-color: {_PALETTE['bg.primary']};
                color: {_PALETTE['text.primary']};
            }}
        """)
        self._step = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._welcome_page())
        self._stack.addWidget(self._features_page())
        self._stack.addWidget(self._ready_page())
        layout.addWidget(self._stack, 1)

        # Bottom navigation
        nav = QFrame()
        nav.setFixedHeight(56)
        nav.setStyleSheet(
            f"background: {_PALETTE['bg.secondary']}; border-top: 1px solid {_PALETTE['border.default']};"
        )
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(24, 0, 24, 0)

        self._dots = QLabel()
        self._dots.setStyleSheet(f"color: {_PALETTE['accent.primary']}; font-size: 18px;")
        nav_layout.addWidget(self._dots)
        nav_layout.addStretch()

        self._back_btn = QPushButton("Back")
        self._back_btn.setFixedSize(80, 34)
        self._back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._back_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {_PALETTE['text.secondary']}; "
            f"border: 1px solid {_PALETTE['border.default']}; border-radius: {_PALETTE['radius.md']}; }}"
            f"QPushButton:hover {{ background: {_PALETTE['bg.secondary']}; }}"
        )
        self._back_btn.clicked.connect(self._go_back)
        nav_layout.addWidget(self._back_btn)

        self._next_btn = QPushButton("Next")
        self._next_btn.setFixedSize(100, 34)
        self._next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._next_btn.setStyleSheet(
            f"QPushButton {{ background: {_PALETTE['accent.primary']}; color: #fff; border: none; "
            f"border-radius: {_PALETTE['radius.md']}; font-weight: bold; }} "
            f"QPushButton:hover {{ background: {_PALETTE['accent.secondary']}; }}"
        )
        self._next_btn.clicked.connect(self._go_next)
        nav_layout.addWidget(self._next_btn)

        layout.addWidget(nav)
        self._update_nav()

    def _section_title(self, text, size=24):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", size, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {_PALETTE['accent.primary']};")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lbl

    def _body_label(self, text, color="text.secondary", size=11, wrap=True):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", size))
        lbl.setStyleSheet(f"color: {_PALETTE[color]};")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if wrap:
            lbl.setWordWrap(True)
        return lbl

    # ── Pages ───────────────────────────────────────────────────────────
    def _welcome_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 48, 48, 24)
        layout.setSpacing(_sp("space.gap.md"))
        layout.addStretch()

        icon = QLabel()
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedHeight(64)
        icon.setStyleSheet(f"font-size: 48px; color: {_PALETTE['accent.primary']};")
        icon.setText("N")
        icon.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        layout.addWidget(icon)

        layout.addWidget(self._section_title("Welcome to MyNexus"))
        layout.addWidget(self._body_label(
            "Your private personal OS for Windows.\n"
            "Tasks, money, documents, credentials — offline and encrypted by default."
        ))
        layout.addStretch()
        return page

    def _features_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 36, 48, 24)
        layout.setSpacing(_sp("space.gap.sm"))

        layout.addWidget(QLabel("What you can do"))
        layout.itemAt(layout.count()-1).widget().setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        layout.itemAt(layout.count()-1).widget().setStyleSheet(f"color: {_PALETTE['text.primary']};")

        features = [
            ("Activities & Reminders", "Never miss a payment or deadline"),
            ("Credential Vault", "Encrypted local storage for logins"),
            ("Document Vault", "Track expiry on passports, tax docs, certificates"),
            ("Budget Tracker", "Spending limits by category"),
            ("Net Worth", "Wealth, FIRE progress, and cash buffer"),
            ("Calendar", "Visual month overview with due dates"),
        ]
        for name, desc in features:
            row = QHBoxLayout()
            row.setSpacing(_sp("space.3"))
            dot = QLabel("•")
            dot.setFixedWidth(12)
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setStyleSheet(f"color: {_PALETTE['accent.primary']};")
            row.addWidget(dot)

            col = QVBoxLayout()
            col.setSpacing(2)
            n = QLabel(name)
            n.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            n.setStyleSheet(f"color: {_PALETTE['text.primary']};")
            col.addWidget(n)
            d = QLabel(desc)
            d.setFont(QFont("Segoe UI", 9))
            d.setStyleSheet(f"color: {_PALETTE['text.secondary']};")
            col.addWidget(d)
            row.addLayout(col, 1)
            layout.addLayout(row)

        layout.addStretch()
        return page

    def _ready_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 48, 48, 24)
        layout.setSpacing(_sp("space.gap.md"))
        layout.addStretch()

        icon = QLabel("✓")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedHeight(64)
        icon.setFont(QFont("Segoe UI", 52, QFont.Weight.Bold))
        icon.setStyleSheet(f"color: {_PALETTE['text.primary']};")
        layout.addWidget(icon)

        layout.addWidget(self._section_title("You're all set"))
        layout.addWidget(self._body_label(
            "Choose a first action to build momentum.\n"
            "You can always change these later in Settings → Security."
        ))

        actions = QHBoxLayout()
        actions.setSpacing(_sp("space.gap.md"))
        add_activity = QPushButton("Add your first activity")
        add_activity.setCursor(Qt.CursorShape.PointingHandCursor)
        add_activity.setFixedHeight(36)
        add_activity.setStyleSheet(
            f"QPushButton {{ background: {_PALETTE['accent.primary']}; color: #fff; border: none; "
            f"border-radius: {_PALETTE['radius.md']}; font-weight: bold; }} "
            f"QPushButton:hover {{ background: {_PALETTE['accent.secondary']}; }}"
        )
        add_activity.clicked.connect(self.accept)

        security = QPushButton("Enable security")
        security.setCursor(Qt.CursorShape.PointingHandCursor)
        security.setFixedHeight(36)
        security.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {_PALETTE['text.secondary']}; "
            f"border: 1px solid {_PALETTE['border.default']}; border-radius: {_PALETTE['radius.md']}; }} "
            f"QPushButton:hover {{ background: {_PALETTE['bg.secondary']}; }}"
        )
        security.clicked.connect(self.accept)

        actions.addWidget(add_activity)
        actions.addWidget(security)
        layout.addLayout(actions)
        layout.addStretch()
        return page

    # ── Navigation helpers ──────────────────────────────────────────────
    def _update_nav(self):
        total = self._stack.count()
        dots = "  ".join("●" if i == self._step else "○" for i in range(total))
        self._dots.setText(dots)
        self._back_btn.setVisible(self._step > 0)
        self._next_btn.setText("Get Started" if self._step == total - 1 else "Next")

    def _go_next(self):
        if self._step < self._stack.count() - 1:
            self._step += 1
            self._stack.setCurrentIndex(self._step)
            self._update_nav()
        else:
            self.accept()

    def _go_back(self):
        if self._step > 0:
            self._step -= 1
            self._stack.setCurrentIndex(self._step)
            self._update_nav()
