"""
Integrations management widget
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QDialog, QLineEdit, QComboBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont


def _btn_cell(btn):
    """Wrap a button in a centered container for clean table cell sizing."""
    from PyQt6.QtWidgets import QWidget, QHBoxLayout
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(4, 2, 4, 2)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(btn)
    return container

from src.database.config import get_session
from src.database.operations import IntegrationManager
from src.ui.components.premium_button import PremiumButton
from src.ui.styles.tokens import token
from src.ui.styles.icon_manager import IconManager
from config.settings import APP_NAME


class IntegrationsWidget(QWidget):
    """Integrations management widget"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.refresh_integrations()
    
    def _setup_ui(self):
        """Setup integrations UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Integrations")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Action buttons
        add_btn = PremiumButton("Add Integration", style=PremiumButton.Style.PRIMARY, icon_name="add")
        add_btn.clicked.connect(self.add_integration)
        header_layout.addWidget(add_btn)

        refresh_btn = PremiumButton("Refresh", style=PremiumButton.Style.SECONDARY, icon_name="refresh")
        refresh_btn.clicked.connect(self.refresh_integrations)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Info box
        info_label = QLabel(
            f"Connect your applications to {APP_NAME} for automated synchronization. "
            "Your credentials are securely stored locally."
        )
        info_label.setWordWrap(True)
        info_label.setObjectName("subtitleLabel")
        main_layout.addWidget(info_label)
        
        # Integrations table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Type", "Status", "Last Synced", "Edit", "Delete"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {token("color.bg.secondary")};
                alternate-background-color: {token("color.bg.tertiary")};
                gridline-color: {token("color.border.default")};
                border: 1px solid {token("color.border.default")}; border-radius: 8px;
            }}
            QHeaderView::section {{
                background-color: {token("color.bg.tertiary")}; color: {token("color.text.secondary")}; padding: 10px 8px;
                border: none; border-bottom: 2px solid {token("color.border.default")};
                font-weight: 700; font-size: 11px;
            }}
        """)
        from PyQt6.QtWidgets import QHeaderView
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 160)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
    
    @pyqtSlot()
    def refresh_integrations(self):
        """Refresh integrations table"""
        session = get_session()
        try:
            integrations = IntegrationManager.get_all_integrations(session, active_only=False)
            self.table.setRowCount(len(integrations))
            
            for row, integration in enumerate(integrations):
                # Name
                self.table.setItem(row, 0, QTableWidgetItem(integration.name))
                
                # Type
                self.table.setItem(row, 1, QTableWidgetItem(integration.app_type.upper()))
                
                # Status
                status = "Active" if integration.is_active else "Inactive"
                status_item = QTableWidgetItem(status)
                self.table.setItem(row, 2, status_item)
                
                # Last synced
                last_synced = integration.last_synced.strftime("%Y-%m-%d %H:%M") if integration.last_synced else "Never"
                self.table.setItem(row, 3, QTableWidgetItem(last_synced))
                
                # Edit button — labeled, blue ghost style
                edit_btn = PremiumButton("Edit", style=PremiumButton.Style.EDIT, icon_name="edit")
                edit_btn.setFixedSize(88, 34)
                edit_btn.setToolTip("Edit integration")
                edit_btn.clicked.connect(lambda checked, iid=integration.id: self.edit_integration(iid))
                self.table.setCellWidget(row, 4, _btn_cell(edit_btn))

                # Delete button — labeled, red ghost style
                delete_btn = PremiumButton("Delete", style=PremiumButton.Style.GHOST_DANGER, icon_name="delete")
                delete_btn.setFixedSize(88, 34)
                delete_btn.setToolTip("Delete integration")
                delete_btn.clicked.connect(lambda checked, iid=integration.id: self.delete_integration(iid))
                self.table.setCellWidget(row, 5, _btn_cell(delete_btn))
            
        finally:
            session.close()
    
    @pyqtSlot()
    def add_integration(self):
        """Show add integration dialog"""
        dialog = IntegrationDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            integration_data = dialog.get_data()
            session = get_session()
            try:
                IntegrationManager.create_integration(session, **integration_data)
                self.refresh_integrations()
            finally:
                session.close()
    
    @pyqtSlot(int)
    def edit_integration(self, integration_id: int):
        """Edit existing integration"""
        session = get_session()
        try:
            integration = IntegrationManager.get_integration(session, integration_id)
            if integration:
                dialog = IntegrationDialog(integration)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    integration_data = dialog.get_data()
                    IntegrationManager.update_integration(session, integration_id, **integration_data)
                    self.refresh_integrations()
        finally:
            session.close()
    
    @pyqtSlot(int)
    def delete_integration(self, integration_id: int):
        """Delete integration"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this integration?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
                IntegrationManager.delete_integration(session, integration_id)
                self.refresh_integrations()
            finally:
                session.close()


class IntegrationDialog(QDialog):
    """Dialog for adding/editing integrations"""
    
    APP_TYPES = {
        "Email": "email",
        "Calendar": "calendar",
        "Payment": "payment",
        "Task Manager": "task",
        "Banking": "banking",
        "Custom": "custom"
    }
    
    def __init__(self, integration=None):
        super().__init__()
        self.integration = integration
        self.setWindowTitle("Integration Settings")
        self.setGeometry(200, 200, 400, 300)
        self._setup_ui()
        
        if integration:
            self._populate_fields(integration)
    
    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QFormLayout()
        layout.setSpacing(15)
        
        # Name
        self.name_input = QLineEdit()
        layout.addRow("Name (e.g., Gmail, Outlook):", self.name_input)
        
        # App type
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.APP_TYPES.keys())
        layout.addRow("Type:", self.type_combo)
        
        # Username
        self.username_input = QLineEdit()
        layout.addRow("Username/Email:", self.username_input)
        
        # API Key / Password
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("API Key/Password:", self.api_key_input)
        
        # Status
        from PyQt6.QtWidgets import QCheckBox as _QCheckBox
        self.active_check = _QCheckBox("Active")
        self.active_check.setChecked(True)
        layout.addRow("Status:", self.active_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = PremiumButton("Save", style=PremiumButton.Style.PRIMARY, icon_name="save")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        cancel_btn = PremiumButton("Cancel", style=PremiumButton.Style.FLAT, icon_name="close")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def _populate_fields(self, integration):
        """Populate form fields from integration"""
        self.name_input.setText(integration.name)
        
        # Find and set app type
        for display_name, app_type in self.APP_TYPES.items():
            if app_type == integration.app_type:
                self.type_combo.setCurrentText(display_name)
                break
        
        self.username_input.setText(integration.username or "")
        self.api_key_input.setText(integration.api_key or "")
        self.active_check.setChecked(integration.is_active)
    
    def get_data(self):
        """Get form data"""
        selected_type = self.APP_TYPES[self.type_combo.currentText()]
        
        return {
            "name": self.name_input.text(),
            "app_type": selected_type,
            "username": self.username_input.text(),
            "api_key": self.api_key_input.text(),
            "is_active": self.active_check.isChecked(),
        }
