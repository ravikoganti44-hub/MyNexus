"""
Main application window
"""
import sys
import os

# Add project root to path
from PyQt6.QtCore import Qt, QTimer, QEvent, QPropertyAnimation
from PyQt6.QtGui import QIcon, QFont, QColor, QShortcut, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QSplitter, QStatusBar, QFrame, QLabel, QGraphicsDropShadowEffect,
    QSystemTrayIcon, QMenu, QGraphicsOpacityEffect
)

FLUENT_CHROME = True  # frameless title bar + QSizeGrip resize

from src.ui.components.dashboard import DashboardWidget
from src.ui.components.activities import ActivitiesWidget
from src.ui.components.integrations import IntegrationsWidget
from src.ui.components.connected_apps import ConnectedAppsWidget
from src.ui.components.document_vault import DocumentVaultWidget
from src.ui.components.budget import BudgetTrackerWidget
from src.ui.components.calendar_view import CalendarViewWidget
from src.ui.components.net_worth import NetWorthWidget
from src.ui.components.settings import SettingsWidget
from src.ui.components.sidebar import SidebarWidget
from src.ui.components.quick_search import QuickSearchDialog
from src.ui.styles.icon_manager import IconManager
from src.ui.styles.theme import get_stylesheet
from src.ui.styles.tokens import token as _main_token
from src.core.reminder_engine import get_reminder_engine
from src.database.config import init_db
from config.settings import APP_NAME, APP_TITLE, APP_VERSION


class MainWindow(QMainWindow):
    """Main application window"""
    
    IDLE_LOCK_MINUTES = 15  # Lock after 15 minutes of inactivity
    
    def __init__(self):
        super().__init__()
        self.reminder_engine = get_reminder_engine()
        self._locked = False
        
        # Initialize database
        init_db()
        
        # Window chrome
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(IconManager.get_icon("my_nexus", size=64, color=_main_token("color.accent.primary")))
        if FLUENT_CHROME:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)
        
        # Premium hover lift for the main window (implemented in global stylesheet)
        
        # Set stylesheet
        self.setStyleSheet(get_stylesheet())
        
        # Setup UI
        self._setup_ui()
        
        # Global shortcuts
        search_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        search_shortcut.activated.connect(self._open_quick_search)

        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self._show_shortcuts)

        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self._refresh_current_page)

        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)

        backup_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        backup_shortcut.activated.connect(self._quick_backup)

        # Idle-lock timer
        self._idle_timer = QTimer(self)
        self._idle_timer.setSingleShot(True)
        self._idle_timer.timeout.connect(self._on_idle_lock)
        self._reset_idle_timer()
        self.installEventFilter(self)
        
        # Start reminder engine
        self.reminder_engine.start()
        
        # Tray icon
        self._init_tray()
    
    def _setup_ui(self):
        """Setup user interface"""
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setObjectName("centralWidget")
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(0)

        self.shell_frame = QFrame()
        self.shell_frame.setObjectName("appShell")

        shell_shadow = QGraphicsDropShadowEffect(self)
        shell_shadow.setBlurRadius(38)
        shell_shadow.setOffset(0, 10)
        shell_shadow.setColor(QColor(4, 8, 15, 190))
        self.shell_frame.setGraphicsEffect(shell_shadow)

        shell_layout = QVBoxLayout(self.shell_frame)
        shell_layout.setContentsMargins(1, 1, 1, 1)
        shell_layout.setSpacing(0)

        body_frame = QFrame()
        body_frame.setObjectName("appBody")
        body_layout = QHBoxLayout(body_frame)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.page_changed.connect(self._on_page_changed)
        
        # Stacked widget for pages
        self.pages = QStackedWidget()
        
        # Dashboard
        self.dashboard = DashboardWidget()
        self.pages.addWidget(self.dashboard)
        
        # Activities
        self.activities = ActivitiesWidget()
        self.pages.addWidget(self.activities)
        
        # Integrations
        self.integrations = IntegrationsWidget()
        self.pages.addWidget(self.integrations)
        
        # Connected Applications
        self.connected_apps = ConnectedAppsWidget()
        self.pages.addWidget(self.connected_apps)
        
        # Document Vault
        self.document_vault = DocumentVaultWidget()
        self.pages.addWidget(self.document_vault)

        # Budget Tracker  (index 5)
        self.budget_tracker = BudgetTrackerWidget()
        self.pages.addWidget(self.budget_tracker)

        # Calendar View  (index 6)
        self.calendar_view = CalendarViewWidget()
        self.pages.addWidget(self.calendar_view)

        # Net Worth  (index 7)
        self.net_worth = NetWorthWidget()
        self.pages.addWidget(self.net_worth)

        # Settings  (index 8)
        self.settings = SettingsWidget()
        self.pages.addWidget(self.settings)
        
        # Add to shell layout
        body_layout.addWidget(self.sidebar)
        body_layout.addWidget(self.pages, 1)

        shell_layout.addWidget(body_frame, 1)
        status_frame = QFrame()
        status_frame.setObjectName("windowStatusBar")
        status_frame.setFixedHeight(34)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(16, 0, 16, 0)
        status_layout.setSpacing(10)

        self.window_status_label = QLabel("Ready")
        self.window_status_label.setObjectName("windowStatusLabel")
        status_layout.addWidget(self.window_status_label)
        status_layout.addStretch()

        # Notification bell in status bar
        from src.ui.components.notification_center import NotificationBell
        self._notif_bell = NotificationBell()
        status_layout.addWidget(self._notif_bell)

        # Ctrl+K search hint
        search_hint = QLabel("Ctrl+K Search")
        search_hint.setObjectName("windowStatusLabel")
        search_hint.setStyleSheet(
            f"color: {_main_token('color.text.tertiary')}; font-size: 9px;"
        )
        status_layout.addWidget(search_hint)

        shell_layout.addWidget(status_frame)
        
        # Frameless chrome
        if FLUENT_CHROME:
            try:
                from src.ui.components.window_chrome import TitleBar, QSizeGrip
                self._title_bar = TitleBar(self, self)
                shell_layout.insertWidget(0, self._title_bar)
                grip = QSizeGrip(self)
                grip.setFixedSize(12, 12)
                shell_layout.addWidget(grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
            except Exception:
                pass

        main_layout.addWidget(self.shell_frame, 1)

    def _refresh_current_page_layout(self):
        """Refresh active page layout after window geometry changes settle."""
        current_page = self.pages.currentWidget()
        if hasattr(current_page, "refresh_layout"):
            QTimer.singleShot(0, current_page.refresh_layout)
    
    def _on_page_changed(self, page_index: int):
        """Handle page change with lightweight motion.
        
        Strategy:
        - Fade out old page -> switch index -> fade in new page.
        - No geometry or visibility-based animation.
        """
        previous = self.pages.currentWidget()
        new = self.pages.widget(page_index)
        if previous is None or previous is new:
            self.pages.setCurrentIndex(page_index)
            self._refresh_current_page_layout()
            if 0 <= page_index < len(page_names):
                self.window_status_label.setText(f"Viewing: {page_names[page_index]}")
            return

        old_effect = QGraphicsOpacityEffect(previous)
        old_effect.setOpacity(1.0)
        previous.setGraphicsEffect(old_effect)
        new_effect = QGraphicsOpacityEffect(new)
        new_effect.setOpacity(0.0)
        new.setGraphicsEffect(new_effect)

        fade_out = QPropertyAnimation(old_effect, b"opacity", self)
        fade_out.setDuration(140)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        fade_in = QPropertyAnimation(new_effect, b"opacity", self)
        fade_in.setDuration(140)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)

        def switch_start():
            self.pages.setCurrentIndex(page_index)
            self._refresh_current_page_layout()
            if 0 <= page_index < len(page_names):
                self.window_status_label.setText(f"Viewing: {page_names[page_index]}")
            fade_in.start()

        fade_out.finished.connect(switch_start)
        fade_out.start()

    def resizeEvent(self, event):
        """Handle responsive layout changes on resize"""
        result = super().resizeEvent(event)
        width = self.width()
        try:
            if width < 1024:
                self.sidebar.collapse()
            else:
                self.sidebar.expand()
        except Exception:
            pass
        self._refresh_current_page_layout()
        return result

    def changeEvent(self, event):
        """Refresh page layout after maximize/restore window state changes."""
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self._refresh_current_page_layout()

    # ── Idle-lock ───────────────────────────────────────────────────
    def _reset_idle_timer(self):
        self._idle_timer.start(self.IDLE_LOCK_MINUTES * 60 * 1000)

    def eventFilter(self, obj, event):
        """Reset idle timer on any user interaction."""
        if event.type() in (
            QEvent.Type.MouseMove, QEvent.Type.MouseButtonPress,
            QEvent.Type.KeyPress, QEvent.Type.Wheel,
        ):
            if not self._locked:
                self._reset_idle_timer()
        return super().eventFilter(obj, event)

    def _on_idle_lock(self):
        """Lock the app after idle timeout."""
        from src.core.encryption import is_passphrase_set
        if not is_passphrase_set():
            return  # No passphrase configured — skip locking
        self._locked = True
        self.setEnabled(False)
        from src.ui.components.onboarding import MasterPassphraseDialog
        dlg = MasterPassphraseDialog(first_time=False)
        dlg.setWindowTitle("Session Locked — Enter Passphrase")
        if dlg.exec():
            self._locked = False
            self.setEnabled(True)
            self._reset_idle_timer()
        else:
            # User dismissed — close app
            self.close()
    
    # ── Tray ─────────────────────────────────────────────────────
    def _init_tray(self):
        tray_icon = IconManager.get_icon("my_nexus", size=32, color=_main_token("color.accent.primary"))
        tray = QSystemTrayIcon(self)
        tray.setIcon(tray_icon)

        menu = QMenu(self)
        restore_action = menu.addAction("Restore")
        restore_action.triggered.connect(self._restore_window)
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.close)

        tray.setContextMenu(menu)
        tray.activated.connect(self._tray_activated)
        tray.show()
        self._tray = tray

    def _tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.DoubleClick, QSystemTrayIcon.ActivationReason.Trigger):
            self._restore_window()

    def _restore_window(self):
        if self.isMinimized() or self.isMaximized():
            self.showNormal()
        self.show()
        self.raise_()
        self.activateWindow()

    def _on_page_changed(self, page_index: int):
        """Handle page change with lightweight motion.
        
        Strategy:
        - Fade out old page -> switch index -> fade in new page.
        - No geometry or visibility-based animation.
        """
        previous = self.pages.currentWidget()
        new = self.pages.widget(page_index)
        if previous is None or previous is new:
            self.pages.setCurrentIndex(page_index)
            self._refresh_current_page_layout()
            return

        old_effect = QGraphicsOpacityEffect(previous)
        old_effect.setOpacity(1.0)
        previous.setGraphicsEffect(old_effect)
        new_effect = QGraphicsOpacityEffect(new)
        new_effect.setOpacity(0.0)
        new.setGraphicsEffect(new_effect)

        fade_out = QPropertyAnimation(old_effect, b"opacity", self)
        fade_out.setDuration(140)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        fade_in = QPropertyAnimation(new_effect, b"opacity", self)
        fade_in.setDuration(140)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)

        def switch_start():
            self.pages.setCurrentIndex(page_index)
            self._refresh_current_page_layout()
            fade_in.start()

        fade_out.finished.connect(switch_start)
        fade_out.start()

        page_names = ["Dashboard", "Activities", "Integrations", "Connected Apps",
                       "Document Vault", "Budget Tracker", "Calendar View", "Net Worth", "Settings"]
        if 0 <= page_index < len(page_names):
            self.window_status_label.setText(f"Viewing: {page_names[page_index]}")

    def closeEvent(self, event):
        """Handle window close event"""
        # Auto-backup on close
        try:
            from src.core.backup import create_backup, prune_old_backups
            create_backup(label="auto")
            prune_old_backups(keep=10)
        except Exception:
            pass
        # Stop reminder engine
        self.reminder_engine.stop()
        event.accept()

    # ── Quick Search ────────────────────────────────────────────────────
    def _open_quick_search(self):
        dlg = QuickSearchDialog(self, on_navigate=self._navigate_to_item)
        dlg.exec()

    def _navigate_to_item(self, item_type: str, item_id: int):
        """Navigate to a specific item from quick search."""
        page_map = {
            "activity": 1,
            "connected_app": 3,
            "document": 4,
        }
        page_idx = page_map.get(item_type)
        if page_idx is not None:
            self.sidebar._on_button_clicked(
                self.sidebar._buttons[page_idx][0], page_idx
            )

    def _show_shortcuts(self):
        from src.ui.components.shortcuts_overlay import ShortcutsOverlay
        ShortcutsOverlay(self).exec()

    def _refresh_current_page(self):
        """F5 – refresh the active page data."""
        page = self.pages.currentWidget()
        if hasattr(page, "refresh_data"):
            page.refresh_data()

    def _quick_backup(self):
        """Ctrl+B – silent background backup."""
        try:
            from src.core.backup import create_backup
            create_backup(label="quick")
            self.window_status_label.setText("Backup saved")
            QTimer.singleShot(3000, lambda: self.window_status_label.setText("Ready"))
        except Exception:
            pass


def _show_onboarding_if_needed():
    """Show onboarding wizard for first-time users.
    Passphrase setup is no longer forced on first launch.
    Users can set it later from Settings > Security.
    """
    from src.ui.components.onboarding import OnboardingWizard

    onboarding_flag = os.path.join(os.path.expanduser("~"), ".mynexus", ".onboarded")
    if not os.path.exists(onboarding_flag):
        wiz = OnboardingWizard()
        wiz.exec()
        os.makedirs(os.path.dirname(onboarding_flag), exist_ok=True)
        with open(onboarding_flag, "w") as f:
            f.write("1")


def main():
    """Main entry point"""
    app = None
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        app.setWindowIcon(IconManager.get_icon("my_nexus", size=64, color=_main_token("color.accent.primary")))

        # Onboarding & passphrase setup
        _show_onboarding_if_needed()
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Run event loop
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
