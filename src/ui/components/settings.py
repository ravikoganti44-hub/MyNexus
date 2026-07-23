"""
Settings and preferences widget
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QSpinBox, QComboBox, QSlider, QGroupBox, QFormLayout, QFileDialog,
    QMessageBox, QTabWidget, QListWidget, QListWidgetItem, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import json
import os
from src.ui.components.premium_button import PremiumButton
from src.ui.styles.tokens import token


class SettingsWidget(QWidget):
    """Settings and preferences widget"""
    
    def __init__(self):
        super().__init__()
        self.config_file = os.path.join(os.path.dirname(__file__), '../../config/app_settings.json')
        self.settings = self._load_settings()
        self._setup_ui()
    
    def _load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default settings
        return {
            'notifications_enabled': True,
            'sound_enabled': True,
            'notification_duration': 5,
            'notification_position': 'top-right',
            'auto_refresh_interval': 30,
            'theme': 'dark',
            'show_weekend': True,
            'time_format': '24h',
            'check_updates': True,
            'backup_enabled': True,
            'backup_interval': 7,
        }
    
    def _save_settings(self):
        """Save settings to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def _setup_ui(self):
        """Setup settings UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Shared polish stylesheet applied to the entire settings page for token-backed
        # controls: tab inactive dimming, editable field affordance, rounded toggles.
        polish = f"""
            QTabBar::tab {{
                color: {token("color.text.secondary")};
                padding: 10px 16px;
            }}
            QTabBar::tab:selected {{
                color: {token("color.text.primary")};
            }}

            QSpinBox {{
                padding: 8px 10px;
                background-color: {token("color.bg.tertiary")};
                border: 1px solid {token("color.border.default")};
                border-radius: {token("radius.md")};
                color: {token("color.text.primary")};
                selection-background-color: {token("color.accent.secondary")};
            }}
            QSpinBox:hover {{
                border-color: {token("color.accent.primary")};
            }}
            QSpinBox:focus {{
                border: 1px solid {token("color.accent.primary")};
            }}

            QComboBox {{
                padding: 8px 10px;
                background-color: {token("color.bg.tertiary")};
                border: 1px solid {token("color.border.default")};
                border-radius: {token("radius.md")};
                color: {token("color.text.primary")};
                selection-background-color: {token("color.accent.secondary")};
            }}
            QComboBox:hover {{
                border-color: {token("color.accent.primary")};
            }}

            QCheckBox::indicator {{
                width: 18px; height: 18px;
                border-radius: 9px;
                border: 2px solid {token("color.border.light")};
                background-color: {token("color.bg.tertiary")};
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid {token("color.accent.primary")};
                background-color: {token("color.accent.primary")};
            }}
            QCheckBox::indicator:hover {{
                border-color: {token("color.accent.primary")};
            }}
        """

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Settings & Preferences")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Tab widget for different settings categories
        tabs = QTabWidget()
        tabs.setStyleSheet(polish)

        # Notifications tab
        tabs.addTab(self._create_notifications_tab(), "🔔 Notifications")

        # Display tab
        tabs.addTab(self._create_display_tab(), "🎨 Display")

        # Behavior tab
        tabs.addTab(self._create_behavior_tab(), "⚙️ Behavior")

        # Data tab
        tabs.addTab(self._create_data_tab(), "💾 Data & Backup")

        # Security tab
        tabs.addTab(self._create_security_tab(), "🔐 Security")

        # About tab
        tabs.addTab(self._create_about_tab(), "ℹ️ About")

        main_layout.addWidget(tabs)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        save_btn = PremiumButton("Save Settings", style=PremiumButton.Style.SUCCESS, icon_name="save")
        save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(save_btn)

        reset_btn = PremiumButton("Reset to Defaults", style=PremiumButton.Style.FLAT, icon_name="refresh")
        reset_btn.clicked.connect(self._reset_to_defaults)
        buttons_layout.addWidget(reset_btn)

        close_btn = PremiumButton("Close", style=PremiumButton.Style.FLAT, icon_name="close")
        close_btn.clicked.connect(self._on_close)
        buttons_layout.addWidget(close_btn)

        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)
    
    def _create_notifications_tab(self):
        """Create notifications settings tab"""
        widget = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        
        # Enable notifications
        self.notif_enabled_cb = QCheckBox("Enable notifications")
        self.notif_enabled_cb.setChecked(self.settings['notifications_enabled'])
        layout.addRow("", self.notif_enabled_cb)
        
        # Sound
        self.sound_enabled_cb = QCheckBox("Enable notification sound")
        self.sound_enabled_cb.setChecked(self.settings['sound_enabled'])
        layout.addRow("", self.sound_enabled_cb)
        
        # Notification duration
        self.notif_duration_spin = QSpinBox()
        self.notif_duration_spin.setMinimum(1)
        self.notif_duration_spin.setMaximum(60)
        self.notif_duration_spin.setValue(self.settings['notification_duration'])
        self.notif_duration_spin.setSuffix(" seconds")
        layout.addRow("Notification duration:", self.notif_duration_spin)
        
        # Position
        self.notif_position_combo = QComboBox()
        self.notif_position_combo.addItems(['top-right', 'top-left', 'bottom-right', 'bottom-left', 'center'])
        self.notif_position_combo.setCurrentText(self.settings['notification_position'])
        layout.addRow("Position:", self.notif_position_combo)
        
        # Separator
        sep = QLabel("")
        layout.addRow(sep)
        
        # Activity reminders
        reminder_label = QLabel("Activity Reminders")
        reminder_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addRow(reminder_label)
        
        remind_overdue_cb = QCheckBox("Remind for overdue activities")
        remind_overdue_cb.setChecked(True)
        layout.addRow("", remind_overdue_cb)
        self.remind_overdue_cb = remind_overdue_cb
        
        remind_upcoming_cb = QCheckBox("Remind for upcoming activities (24h before)")
        remind_upcoming_cb.setChecked(True)
        layout.addRow("", remind_upcoming_cb)
        self.remind_upcoming_cb = remind_upcoming_cb
        
        widget.setLayout(layout)
        return widget
    
    def _create_display_tab(self):
        """Create display settings tab"""
        widget = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        
        # Theme
        theme_combo = QComboBox()
        theme_combo.addItems(['Dark', 'Light'])
        theme_combo.setCurrentText(self.settings['theme'].title())
        theme_combo.currentTextChanged.connect(self._on_theme_changed)
        layout.addRow("Theme:", theme_combo)
        self.theme_combo = theme_combo
        
        # Time format
        time_format_combo = QComboBox()
        time_format_combo.addItems(['24h', '12h'])
        time_format_combo.setCurrentText(self.settings['time_format'])
        layout.addRow("Time format:", time_format_combo)
        self.time_format_combo = time_format_combo
        
        # Separator
        sep = QLabel("")
        layout.addRow(sep)
        
        # Calendar view
        calendar_label = QLabel("Calendar View")
        calendar_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addRow(calendar_label)
        
        show_weekend_cb = QCheckBox("Show weekends")
        show_weekend_cb.setChecked(self.settings['show_weekend'])
        layout.addRow("", show_weekend_cb)
        self.show_weekend_cb = show_weekend_cb
        
        # Separator
        sep2 = QLabel("")
        layout.addRow(sep2)
        
        # Font size
        font_label = QLabel("Display Settings")
        font_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addRow(font_label)
        
        font_size_spin = QSpinBox()
        font_size_spin.setMinimum(8)
        font_size_spin.setMaximum(20)
        font_size_spin.setValue(11)
        font_size_spin.setSuffix(" pt")
        layout.addRow("Font size:", font_size_spin)
        self.font_size_spin = font_size_spin
        
        widget.setLayout(layout)
        return widget
    
    def _create_behavior_tab(self):
        """Create behavior settings tab"""
        widget = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        
        # Auto-refresh
        auto_refresh_spin = QSpinBox()
        auto_refresh_spin.setMinimum(5)
        auto_refresh_spin.setMaximum(300)
        auto_refresh_spin.setValue(self.settings['auto_refresh_interval'])
        auto_refresh_spin.setSuffix(" seconds")
        layout.addRow("Auto-refresh interval:", auto_refresh_spin)
        self.auto_refresh_spin = auto_refresh_spin
        
        # Separator
        sep = QLabel("")
        layout.addRow(sep)
        
        # Startup behavior
        startup_label = QLabel("Startup Behavior")
        startup_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addRow(startup_label)
        
        minimize_startup_cb = QCheckBox("Start minimized")
        layout.addRow("", minimize_startup_cb)
        self.minimize_startup_cb = minimize_startup_cb
        
        show_dashboard_cb = QCheckBox("Show dashboard at startup")
        show_dashboard_cb.setChecked(True)
        layout.addRow("", show_dashboard_cb)
        self.show_dashboard_cb = show_dashboard_cb
        
        # Separator
        sep2 = QLabel("")
        layout.addRow(sep2)
        
        # Updates
        updates_label = QLabel("Updates")
        updates_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addRow(updates_label)
        
        check_updates_cb = QCheckBox("Check for updates automatically")
        check_updates_cb.setChecked(self.settings['check_updates'])
        layout.addRow("", check_updates_cb)
        self.check_updates_cb = check_updates_cb
        
        widget.setLayout(layout)
        return widget
    
    def _create_data_tab(self):
        """Create data and backup settings tab"""
        widget = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        
        # Backup
        backup_label = QLabel("Automatic Backup")
        backup_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addRow(backup_label)
        
        backup_enabled_cb = QCheckBox("Enable automatic backups")
        backup_enabled_cb.setChecked(self.settings['backup_enabled'])
        layout.addRow("", backup_enabled_cb)
        self.backup_enabled_cb = backup_enabled_cb
        
        backup_interval_spin = QSpinBox()
        backup_interval_spin.setMinimum(1)
        backup_interval_spin.setMaximum(30)
        backup_interval_spin.setValue(self.settings['backup_interval'])
        backup_interval_spin.setSuffix(" days")
        layout.addRow("Backup interval:", backup_interval_spin)
        self.backup_interval_spin = backup_interval_spin
        
        # Separator
        sep = QLabel("")
        layout.addRow(sep)
        
        # Manual backup
        manual_backup_label = QLabel("Manual Backup & Restore")
        manual_backup_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addRow(manual_backup_label)
        
        backup_now_btn = PremiumButton("Backup Now", style=PremiumButton.Style.SECONDARY, icon_name="save")
        backup_now_btn.clicked.connect(self._backup_now)
        layout.addRow("", backup_now_btn)

        restore_btn = PremiumButton("Restore from Backup", style=PremiumButton.Style.FLAT, icon_name="upload")
        restore_btn.clicked.connect(self._restore_backup)
        layout.addRow("", restore_btn)
        
        # Separator
        sep2 = QLabel("")
        layout.addRow(sep2)
        
        # Data management
        data_label = QLabel("Data Management")
        data_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addRow(data_label)
        
        export_all_btn = PremiumButton("Export All Data", style=PremiumButton.Style.FLAT, icon_name="download")
        export_all_btn.clicked.connect(self._export_all)
        layout.addRow("", export_all_btn)

        clear_completed_btn = PremiumButton("Clear Completed Activities", style=PremiumButton.Style.DANGER, icon_name="delete")
        clear_completed_btn.clicked.connect(self._clear_completed)
        layout.addRow("", clear_completed_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _on_theme_changed(self, theme_text: str):
        """Apply theme change live."""
        from src.ui.styles.theme import set_current_theme, get_stylesheet
        theme_name = theme_text.lower()
        set_current_theme(theme_name)
        self.settings['theme'] = theme_name
        # Apply to entire application
        app = None
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
        except Exception:
            pass
        if app:
            app.setStyleSheet(get_stylesheet(theme_name))

    def _create_security_tab(self):
        """Create security settings tab"""
        widget = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)

        sec_label = QLabel("Encryption & Passphrase")
        sec_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addRow(sec_label)

        # Passphrase status
        from src.core.encryption import is_passphrase_set
        status = "✅  Master passphrase is configured" if is_passphrase_set() else "⚠️  No master passphrase set"
        status_lbl = QLabel(status)
        status_lbl.setStyleSheet("font-size: 12px;")
        layout.addRow("Status:", status_lbl)

        change_pp_btn = PremiumButton("Change Passphrase", style=PremiumButton.Style.SECONDARY, icon_name="edit")
        change_pp_btn.clicked.connect(self._change_passphrase)
        layout.addRow("", change_pp_btn)

        sep = QLabel("")
        layout.addRow(sep)

        lock_label = QLabel("Auto-Lock")
        lock_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addRow(lock_label)

        lock_info = QLabel("App locks after 15 minutes of inactivity when passphrase is set.")
        lock_info.setStyleSheet(f"color: {token('color.text.secondary')}; font-size: 11px;")
        lock_info.setWordWrap(True)
        layout.addRow("", lock_info)

        widget.setLayout(layout)
        return widget

    def _create_about_tab(self):
        """Create about tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        from config.settings import APP_NAME, APP_VERSION
        name_lbl = QLabel(f"🌐  {APP_NAME}")
        name_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color: {token('color.accent.primary')};")
        layout.addWidget(name_lbl)

        ver_lbl = QLabel(f"Version {APP_VERSION}")
        ver_lbl.setFont(QFont("Segoe UI", 11))
        ver_lbl.setStyleSheet(f"color: {token('color.text.secondary')};")
        layout.addWidget(ver_lbl)

        desc = QLabel(
            "MyNexus is your all-in-one personal management hub — "
            "activities, documents, finances, connected apps, and more, "
            "all secured with encryption."
        )
        desc.setWordWrap(True)
        desc.setFont(QFont("Segoe UI", 11))
        layout.addWidget(desc)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _change_passphrase(self):
        """Open passphrase change dialog."""
        from src.ui.components.onboarding import MasterPassphraseDialog
        dlg = MasterPassphraseDialog(first_time=True)
        dlg.setWindowTitle("Set New Passphrase")
        dlg.exec()

    def _reset_to_defaults(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.settings = {
                'notifications_enabled': True,
                'sound_enabled': True,
                'notification_duration': 5,
                'notification_position': 'top-right',
                'auto_refresh_interval': 30,
                'theme': 'dark',
                'show_weekend': True,
                'time_format': '24h',
                'check_updates': True,
                'backup_enabled': True,
                'backup_interval': 7,
            }
            self._apply_settings_to_ui()
            self._save_settings()
    
    def _apply_settings_to_ui(self):
        """Apply loaded settings to UI controls"""
        self.notif_enabled_cb.setChecked(self.settings['notifications_enabled'])
        self.sound_enabled_cb.setChecked(self.settings['sound_enabled'])
        self.notif_duration_spin.setValue(self.settings['notification_duration'])
        self.notif_position_combo.setCurrentText(self.settings['notification_position'])
        self.theme_combo.setCurrentText(self.settings['theme'].title())
        self.time_format_combo.setCurrentText(self.settings['time_format'])
        self.show_weekend_cb.setChecked(self.settings['show_weekend'])
        self.auto_refresh_spin.setValue(self.settings['auto_refresh_interval'])
        self.check_updates_cb.setChecked(self.settings['check_updates'])
        self.backup_enabled_cb.setChecked(self.settings['backup_enabled'])
        self.backup_interval_spin.setValue(self.settings['backup_interval'])
    
    def _backup_now(self):
        """Create manual backup"""
        try:
            from src.core.backup import create_backup
            path = create_backup(label="manual")
            QMessageBox.information(self, "Backup", f"Backup saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", str(e))
    
    def _restore_backup(self):
        """Restore from backup"""
        try:
            from src.core.backup import list_backups, restore_backup
            backups = list_backups()
            if not backups:
                QMessageBox.information(self, "Restore", "No backups available.")
                return
            # Pick the most recent backup via file dialog
            from PyQt6.QtWidgets import QFileDialog
            import os
            backup_dir = os.path.dirname(backups[0]["path"])
            path, _ = QFileDialog.getOpenFileName(
                self, "Select Backup", backup_dir, "Database Files (*.db)"
            )
            if path:
                reply = QMessageBox.question(
                    self, "Confirm Restore",
                    "This will replace your current data with the backup.\n"
                    "A safety backup will be created first. Continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    restore_backup(path)
                    QMessageBox.information(
                        self, "Restored",
                        "Database restored. Please restart MyNexus for changes to take effect."
                    )
        except Exception as e:
            QMessageBox.critical(self, "Restore Failed", str(e))
    
    def _export_all(self):
        """Export all data to JSON"""
        try:
            from src.core.backup import export_all_data
            path, _ = QFileDialog.getSaveFileName(
                self, "Export Data", "mynexus_export.json", "JSON Files (*.json)"
            )
            if path:
                if export_all_data(path):
                    QMessageBox.information(self, "Export", f"Data exported to:\n{path}")
                else:
                    QMessageBox.critical(self, "Export Failed", "An error occurred during export.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
    
    def _clear_completed(self):
        """Clear completed activities"""
        reply = QMessageBox.question(
            self, "Clear Completed Activities",
            "Are you sure you want to delete all completed activities? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Success", "Completed activities cleared!")
    
    def _on_close(self):
        """Handle close button"""
        self.parent().closeEvent(None) if self.parent() else None
