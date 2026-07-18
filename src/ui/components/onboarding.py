"""
Onboarding wizard for first-time users and master passphrase dialog.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QStackedWidget, QWidget, QFrame, QMessageBox,
    QCheckBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QIcon

from src.core.encryption import (
    is_passphrase_set, verify_passphrase, save_key_check, init_encryption
)


class MasterPassphraseDialog(QDialog):
    """Dialog for entering or creating a master passphrase."""

    def __init__(self, parent=None, first_time: bool = False):
        super().__init__(parent)
        self._first_time = first_time
        self._passphrase: str | None = None
        self.setWindowTitle("MyNexus — Unlock")
        self.setFixedSize(440, 320 if first_time else 240)
        self.setStyleSheet(self._get_style())
        self._setup_ui()

    # ── public accessors ────────────────────────────────────────────────
    @property
    def passphrase(self) -> str | None:
        return self._passphrase

    # ── UI ──────────────────────────────────────────────────────────────
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("Create Master Passphrase" if self._first_time else "Unlock MyNexus")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #58a6ff;")
        layout.addWidget(title)

        if self._first_time:
            hint = QLabel(
                "Choose a strong passphrase to protect your passwords and "
                "sensitive data. You will need this every time you open MyNexus."
            )
            hint.setWordWrap(True)
            hint.setFont(QFont("Segoe UI", 9))
            hint.setStyleSheet("color: #b0bbc9;")
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
        show_cb.setStyleSheet("color: #6b7280; font-size: 10px;")
        show_cb.toggled.connect(self._toggle_vis)
        layout.addWidget(show_cb)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        submit = QPushButton("Create" if self._first_time else "Unlock")
        submit.setFixedSize(120, 36)
        submit.setCursor(Qt.CursorShape.PointingHandCursor)
        submit.setStyleSheet(
            "QPushButton { background-color: #58a6ff; color: #fff; border: none; "
            "border-radius: 8px; font-weight: bold; } "
            "QPushButton:hover { background-color: #79c0ff; }"
        )
        submit.clicked.connect(self._on_submit)
        btn_row.addWidget(submit)

        if not self._first_time:
            skip = QPushButton("Skip")
            skip.setFixedSize(80, 36)
            skip.setCursor(Qt.CursorShape.PointingHandCursor)
            skip.setStyleSheet(
                "QPushButton { background-color: transparent; color: #6b7280; "
                "border: 1px solid #30363d; border-radius: 8px; } "
                "QPushButton:hover { background-color: #21262d; }"
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

    def _get_style(self) -> str:
        return """
            QDialog { background-color: #0d1117; }
            QLineEdit {
                background-color: #161b22;
                color: #ffffff;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #58a6ff; }
        """


class OnboardingWizard(QDialog):
    """Multi-step welcome wizard for first-time users."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to MyNexus")
        self.setFixedSize(600, 460)
        self.setStyleSheet(self._style())
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
        nav.setStyleSheet("background: #161b22; border-top: 1px solid #21262d;")
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(24, 0, 24, 0)

        self._dots = QLabel()
        self._dots.setStyleSheet("color: #58a6ff; font-size: 18px;")
        nav_layout.addWidget(self._dots)
        nav_layout.addStretch()

        self._back_btn = QPushButton("Back")
        self._back_btn.setFixedSize(80, 34)
        self._back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._back_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #6b7280; border: 1px solid #30363d; border-radius: 8px; }"
            "QPushButton:hover { background: #21262d; }"
        )
        self._back_btn.clicked.connect(self._go_back)
        nav_layout.addWidget(self._back_btn)

        self._next_btn = QPushButton("Next")
        self._next_btn.setFixedSize(100, 34)
        self._next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._next_btn.setStyleSheet(
            "QPushButton { background: #58a6ff; color: #fff; border: none; border-radius: 8px; font-weight: bold; }"
            "QPushButton:hover { background: #79c0ff; }"
        )
        self._next_btn.clicked.connect(self._go_next)
        nav_layout.addWidget(self._next_btn)

        layout.addWidget(nav)
        self._update_nav()

    # ── Pages ───────────────────────────────────────────────────────────
    def _welcome_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 48, 48, 24)
        layout.setSpacing(16)
        layout.addStretch()

        icon = QLabel("🚀")
        icon.setFont(QFont("Segoe UI Emoji", 48))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("Welcome to MyNexus")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #58a6ff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "Your all-in-one personal organizer.\n"
            "Manage activities, budgets, documents, credentials,\n"
            "net worth, and more — all in one secure place."
        )
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet("color: #b0bbc9;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()
        return page

    def _features_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 36, 48, 24)
        layout.setSpacing(12)

        title = QLabel("What you can do")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)

        features = [
            ("📋", "Activities & Reminders", "Never miss a payment or deadline"),
            ("🔐", "Credential Vault", "Store app passwords encrypted & safe"),
            ("📁", "Document Vault", "Organize passports, tax docs, certificates"),
            ("💰", "Budget Tracker", "Monthly spending with category limits"),
            ("📈", "Net Worth Dashboard", "Track wealth, FIRE progress, analytics"),
            ("📅", "Calendar View", "Visual overview of upcoming activities"),
        ]
        for emoji, name, desc in features:
            row = QHBoxLayout()
            row.setSpacing(12)
            lbl_emoji = QLabel(emoji)
            lbl_emoji.setFont(QFont("Segoe UI Emoji", 18))
            lbl_emoji.setFixedWidth(36)
            row.addWidget(lbl_emoji)
            col = QVBoxLayout()
            col.setSpacing(2)
            lbl_name = QLabel(name)
            lbl_name.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            lbl_name.setStyleSheet("color: #e8eefb;")
            col.addWidget(lbl_name)
            lbl_desc = QLabel(desc)
            lbl_desc.setFont(QFont("Segoe UI", 9))
            lbl_desc.setStyleSheet("color: #6b7280;")
            col.addWidget(lbl_desc)
            row.addLayout(col, 1)
            layout.addLayout(row)

        layout.addStretch()
        return page

    def _ready_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 48, 48, 24)
        layout.setSpacing(16)
        layout.addStretch()

        icon = QLabel("✅")
        icon.setFont(QFont("Segoe UI Emoji", 48))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("You're all set!")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #3fb950;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "Start by adding your first activity or exploring\n"
            "the Dashboard. You can access Settings at any time\n"
            "to customize your experience."
        )
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet("color: #b0bbc9;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()
        return page

    # ── Navigation ──────────────────────────────────────────────────────
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

    def _style(self) -> str:
        return """
            QDialog { background-color: #0d1117; }
            QWidget { background: transparent; color: #ffffff; }
        """
