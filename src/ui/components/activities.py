"""
Activities management widget with advanced features
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QDialog, QLineEdit, QTextEdit, QComboBox, QDateTimeEdit,
    QSpinBox, QCheckBox, QFormLayout, QMessageBox, QHeaderView, QFileDialog,
    QProgressDialog, QTabWidget, QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot, QDateTime, QTimer
from PyQt6.QtGui import QFont, QColor, QIcon


def _btn_cell(btn):
    """Wrap a button in a centered container widget for clean table cell sizing."""
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(4, 2, 4, 2)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(btn)
    return container
import csv
import json
from datetime import datetime

from src.database.config import get_session
from src.database.operations import ActivityManager
from src.database.models import RecurrenceType, CategoryType, Activity
from src.ui.components.premium_button import PremiumButton
from src.ui.styles.icon_manager import IconManager
from src.core.ai_engine import NexusAI
from src.ui.components.ai_insights_panel import AIInsightsPanel


class ActivitiesWidget(QWidget):
    """Activities management widget with advanced features"""
    
    def __init__(self):
        super().__init__()
        self.all_activities = []
        self.filtered_activities = []
        self._setup_ui()
        self.refresh_activities()
    
    def _setup_ui(self):
        """Setup activities UI"""
        main_layout = QVBoxLayout()
        # standardized content gutter
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("My Activities")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Action buttons
        add_btn = PremiumButton("Add Activity", style=PremiumButton.Style.PRIMARY, icon_name="add")
        add_btn.setToolTip("Add a new activity")
        add_btn.clicked.connect(self.add_activity)
        header_layout.addWidget(add_btn)

        templates_btn = PremiumButton("Templates", style=PremiumButton.Style.SECONDARY, icon_name="copy")
        templates_btn.setToolTip("Quick-add from common activity templates")
        templates_btn.clicked.connect(self._show_templates)
        header_layout.addWidget(templates_btn)

        import_cal_btn = PremiumButton("Import Calendar", style=PremiumButton.Style.FLAT, icon_name="upload")
        import_cal_btn.setToolTip("Import events from .ics calendar file")
        import_cal_btn.clicked.connect(self._import_calendar)
        header_layout.addWidget(import_cal_btn)

        refresh_btn = PremiumButton("Refresh", style=PremiumButton.Style.SECONDARY, icon_name="refresh")
        refresh_btn.setToolTip("Refresh activity list")
        refresh_btn.clicked.connect(self.refresh_activities)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Search and Filter bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        # Search box
        search_label = QLabel("🔍 Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search activities by title or description...")
        self.search_input.textChanged.connect(self.apply_filters)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        # Category filter
        category_label = QLabel("Category:")
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", None)
        for cat in CategoryType:
            self.category_filter.addItem(cat.value.title(), cat)
        self.category_filter.currentIndexChanged.connect(self.apply_filters)
        search_layout.addWidget(category_label)
        search_layout.addWidget(self.category_filter)
        
        # Status filter
        status_label = QLabel("Status:")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Pending", "Completed", "Overdue"])
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        search_layout.addWidget(status_label)
        search_layout.addWidget(self.status_filter)
        
        # Sort option
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Due Date (Soon)", "Due Date (Later)", "Created (New)", "Created (Old)", "Title (A-Z)", "Title (Z-A)"])
        self.sort_combo.currentIndexChanged.connect(self.apply_filters)
        search_layout.addWidget(sort_label)
        search_layout.addWidget(self.sort_combo)
        
        # Clear filters
        clear_btn = PremiumButton("Clear Filters", style=PremiumButton.Style.FLAT, icon_name="close")
        clear_btn.clicked.connect(self.clear_filters)
        search_layout.addWidget(clear_btn)
        
        main_layout.addLayout(search_layout)
        
        # Bulk operations bar
        bulk_layout = QHBoxLayout()
        bulk_layout.setSpacing(10)
        
        bulk_label = QLabel("Bulk Actions:")
        self.select_all_cb = QCheckBox("Select All")
        self.select_all_cb.stateChanged.connect(self.toggle_select_all)
        
        mark_complete_btn = PremiumButton("Mark Complete", style=PremiumButton.Style.SUCCESS, icon_name="check")
        mark_complete_btn.clicked.connect(self.mark_selected_complete)

        delete_sel_btn = PremiumButton("Delete Selected", style=PremiumButton.Style.DANGER, icon_name="delete")
        delete_sel_btn.clicked.connect(self.delete_selected)

        export_btn = PremiumButton("Export", style=PremiumButton.Style.FLAT, icon_name="download")
        export_btn.setToolTip("Export to CSV or JSON")
        export_btn.clicked.connect(self.show_export_menu)

        import_btn = PremiumButton("Import", style=PremiumButton.Style.FLAT, icon_name="upload")
        import_btn.setToolTip("Import from CSV or JSON")
        import_btn.clicked.connect(self.import_activities)
        
        bulk_layout.addWidget(bulk_label)
        bulk_layout.addWidget(self.select_all_cb)
        bulk_layout.addSpacing(20)
        bulk_layout.addWidget(mark_complete_btn)
        bulk_layout.addWidget(delete_sel_btn)
        bulk_layout.addSpacing(20)
        bulk_layout.addWidget(export_btn)
        bulk_layout.addWidget(import_btn)
        bulk_layout.addStretch()
        
        main_layout.addLayout(bulk_layout)
        
        # Info bar showing count
        self.info_label = QLabel("Showing 0 activities")
        self.info_label.setFont(QFont("Segoe UI", 9))
        self.info_label.setStyleSheet("color: #9aa4b2;")
        main_layout.addWidget(self.info_label)
        
        # Activities table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "✓", "Title", "Category", "Recurrence", "Next Due", "Days Left", "Status", "Edit", "Delete"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #161b22;
                alternate-background-color: #1c2128;
                gridline-color: #30363d;
                border: 1px solid #30363d;
                border-radius: 8px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px 8px;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: rgba(88, 166, 255, 0.06);
            }
            QTableWidget::item:selected {
                background-color: rgba(88, 166, 255, 0.15);
                color: #e6edf3;
            }
            QHeaderView::section {
                background-color: #1c2128;
                color: #c9d1d9;
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid #30363d;
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            }
        """)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        # Column widths
        self.table.setColumnWidth(0, 38)   # checkbox
        self.table.setColumnWidth(2, 110)  # category
        self.table.setColumnWidth(3, 100)  # recurrence
        self.table.setColumnWidth(4, 110)  # next due
        self.table.setColumnWidth(5, 80)   # days left
        self.table.setColumnWidth(6, 120)  # status
        self.table.setColumnWidth(7, 100)  # edit
        self.table.setColumnWidth(8, 100)  # delete
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Title stretches
        # Improve row height for readability
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.verticalHeader().setVisible(False)
        # double click for detail
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
        main_layout.addWidget(self.table)

        # ── AI Activity Insights ──────────────────────────────────────────
        sep_ai = QFrame()
        sep_ai.setFixedHeight(1)
        sep_ai.setStyleSheet("background-color: #30363d;")
        main_layout.addWidget(sep_ai)
        self.activity_ai_panel = AIInsightsPanel()
        main_layout.addWidget(self.activity_ai_panel)
        
        self.setLayout(main_layout)
    
    def apply_filters(self):
        """Apply search and filter criteria"""
        search_text = self.search_input.text().lower()
        category_filter = self.category_filter.currentData()
        status_filter = self.status_filter.currentText()
        
        self.filtered_activities = []
        
        for activity in self.all_activities:
            # Search filter
            if search_text and search_text not in activity.title.lower() and search_text not in (activity.description or "").lower():
                continue
            
            # Category filter
            if category_filter is not None and activity.category != category_filter:
                continue
            
            # Status filter
            if status_filter == "Pending" and activity.is_completed:
                continue
            elif status_filter == "Completed" and not activity.is_completed:
                continue
            elif status_filter == "Overdue":
                if activity.next_due_date and activity.next_due_date > datetime.now():
                    continue
                if activity.is_completed:
                    continue
            
            self.filtered_activities.append(activity)
        
        # Apply sorting
        sort_option = self.sort_combo.currentText()
        if "Due Date (Soon)" in sort_option:
            self.filtered_activities.sort(key=lambda x: x.next_due_date or datetime.max)
        elif "Due Date (Later)" in sort_option:
            self.filtered_activities.sort(key=lambda x: x.next_due_date or datetime.max, reverse=True)
        elif "Created (New)" in sort_option:
            self.filtered_activities.sort(key=lambda x: x.start_date or datetime.min, reverse=True)
        elif "Created (Old)" in sort_option:
            self.filtered_activities.sort(key=lambda x: x.start_date or datetime.min)
        elif "Title (A-Z)" in sort_option:
            self.filtered_activities.sort(key=lambda x: x.title)
        elif "Title (Z-A)" in sort_option:
            self.filtered_activities.sort(key=lambda x: x.title, reverse=True)
        
        self.populate_table()
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.category_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.sort_combo.setCurrentIndex(0)
    
    @pyqtSlot()
    def refresh_activities(self):
        """Refresh activities table"""
        session = get_session()
        try:
            self.all_activities = ActivityManager.get_all_activities(session)
            self.apply_filters()
            # ── AI insights ───────────────────────────────────────────
            try:
                insights = NexusAI.analyse_activities(session)
                self.activity_ai_panel.set_insights(insights)
            except Exception:
                pass
        finally:
            session.close()
    
    def populate_table(self):
        """Populate table with filtered activities"""
        self.table.setRowCount(len(self.filtered_activities))
        
        for row, activity in enumerate(self.filtered_activities):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setProperty("activity_id", activity.id)
            self.table.setCellWidget(row, 0, checkbox)
            
            # Title - clickable for quick preview
            title_item = QTableWidgetItem(activity.title)
            title_item.setToolTip(activity.description or "No description")
            self.table.setItem(row, 1, title_item)
            
            # Category
            self.table.setItem(row, 2, QTableWidgetItem(activity.category.value.title()))
            
            # Recurrence
            self.table.setItem(row, 3, QTableWidgetItem(activity.recurrence_type.value.title()))
            
            # Next due date
            due_date = activity.next_due_date.strftime("%Y-%m-%d %H:%M") if activity.next_due_date else "N/A"
            due_item = QTableWidgetItem(due_date)
            self.table.setItem(row, 4, due_item)
            
            # Days left — AI-powered smart prediction text
            if activity.next_due_date:
                prediction = NexusAI.predict_next_due(activity)
                days_left = (activity.next_due_date - datetime.now()).days
                days_item = QTableWidgetItem(prediction or str(max(0, days_left)))
                
                # Color code by urgency
                if days_left < 0:
                    days_item.setBackground(QColor("#ef4444"))
                    days_item.setForeground(QColor("#fff"))
                elif days_left == 0:
                    days_item.setBackground(QColor("#f59e0b"))
                    days_item.setForeground(QColor("#fff"))
                elif days_left <= 3:
                    days_item.setBackground(QColor("#fbbf24"))
                    days_item.setForeground(QColor("#1a1a1a"))
                
                self.table.setItem(row, 5, days_item)
            else:
                self.table.setItem(row, 5, QTableWidgetItem("N/A"))
            
            # Status with color
            status = "✓ Completed" if activity.is_completed else "⏳ Pending"
            status_item = QTableWidgetItem(status)
            if activity.is_completed:
                status_item.setForeground(QColor("#10d981"))
            else:
                status_item.setForeground(QColor("#94a3b8"))
            self.table.setItem(row, 6, status_item)
            
            # Edit button — labeled, blue ghost style
            edit_btn = PremiumButton("Edit", style=PremiumButton.Style.EDIT, icon_name="edit")
            edit_btn.setFixedSize(88, 34)
            edit_btn.setToolTip("Edit this activity")
            edit_btn.clicked.connect(lambda checked, aid=activity.id: self.edit_activity(aid))
            self.table.setCellWidget(row, 7, _btn_cell(edit_btn))

            # Delete button — labeled, red ghost style
            delete_btn = PremiumButton("Delete", style=PremiumButton.Style.GHOST_DANGER, icon_name="delete")
            delete_btn.setFixedSize(88, 34)
            delete_btn.setToolTip("Delete this activity")
            delete_btn.clicked.connect(lambda checked, aid=activity.id: self.delete_activity(aid))
            self.table.setCellWidget(row, 8, _btn_cell(delete_btn))
        
        # Update info label
        total_text = f"Showing {len(self.filtered_activities)} of {len(self.all_activities)} activities"
        self.info_label.setText(total_text)
    
    def toggle_select_all(self):
        """Toggle select all checkboxes"""
        is_checked = self.select_all_cb.isChecked()
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(is_checked)
    
    def get_selected_activities(self):
        """Get list of selected activity IDs"""
        selected = []
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                activity_id = checkbox.property("activity_id")
                selected.append(activity_id)
        return selected
    
    def mark_selected_complete(self):
        """Mark selected activities as complete"""
        selected = self.get_selected_activities()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select activities to mark as complete.")
            return
        
        session = get_session()
        try:
            for activity_id in selected:
                ActivityManager.update_activity(session, activity_id, is_completed=True)
            QMessageBox.information(self, "Success", f"Marked {len(selected)} activities as complete.")
            self.refresh_activities()
            # Celebration check
            try:
                from src.ui.components.celebrations import maybe_celebrate
                all_activities = ActivityManager.get_all_activities(session, active_only=False)
                total_completed = sum(1 for a in all_activities if a.is_completed)
                maybe_celebrate(self.window(), total_completed)
            except Exception:
                pass
        finally:
            session.close()
    
    def delete_selected(self):
        """Delete selected activities"""
        selected = self.get_selected_activities()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select activities to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {len(selected)} activities? This cannot be undone."
        )
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
                for activity_id in selected:
                    ActivityManager.delete_activity(session, activity_id)
                QMessageBox.information(self, "Success", f"Deleted {len(selected)} activities.")
                self.refresh_activities()
            finally:
                session.close()
    
    def show_export_menu(self):
        """Show export menu"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Activities")
        dialog.setMinimumWidth(320)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        filtered_count = len(self.filtered_activities)
        all_count      = len(self.all_activities)

        scope_lbl = QLabel(
            f"Current view: {filtered_count} activit{'y' if filtered_count == 1 else 'ies'} "
            f"(of {all_count} total)")
        scope_lbl.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(scope_lbl)

        csv_filtered_btn = PremiumButton(
            f"Export current view as CSV ({filtered_count})",
            style=PremiumButton.Style.FLAT, icon_name="download")
        csv_filtered_btn.clicked.connect(
            lambda: self.export_activities("csv", dialog, all_activities=False))
        layout.addWidget(csv_filtered_btn)

        csv_all_btn = PremiumButton(
            f"Export ALL activities as CSV ({all_count})",
            style=PremiumButton.Style.SECONDARY, icon_name="download")
        csv_all_btn.clicked.connect(
            lambda: self.export_activities("csv", dialog, all_activities=True))
        layout.addWidget(csv_all_btn)

        json_filtered_btn = PremiumButton(
            f"Export current view as JSON ({filtered_count})",
            style=PremiumButton.Style.FLAT, icon_name="download")
        json_filtered_btn.clicked.connect(
            lambda: self.export_activities("json", dialog, all_activities=False))
        layout.addWidget(json_filtered_btn)

        json_all_btn = PremiumButton(
            f"Export ALL activities as JSON ({all_count})",
            style=PremiumButton.Style.FLAT, icon_name="download")
        json_all_btn.clicked.connect(
            lambda: self.export_activities("json", dialog, all_activities=True))
        layout.addWidget(json_all_btn)

        dialog.setLayout(layout)
        dialog.exec()
    
    def export_activities(self, format_type, dialog, all_activities: bool = False):
        """Export activities to file"""
        source = self.all_activities if all_activities else self.filtered_activities
        file_filter = "CSV files (*.csv)" if format_type == "csv" else "JSON files (*.json)"
        filename, _ = QFileDialog.getSaveFileName(self, "Export Activities", "", file_filter)
        
        if not filename:
            return
        
        try:
            if format_type == "csv":
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Title', 'Description', 'Category', 'Recurrence', 'Next Due', 'Status', 'Created'])
                    for activity in source:
                        writer.writerow([
                            activity.title,
                            activity.description or '',
                            activity.category.value.title(),
                            activity.recurrence_type.value.title(),
                            activity.next_due_date.strftime("%Y-%m-%d %H:%M") if activity.next_due_date else '',
                            "Completed" if activity.is_completed else "Pending",
                            activity.start_date.strftime("%Y-%m-%d %H:%M") if activity.start_date else ''
                        ])
            else:  # JSON
                data = []
                for activity in source:
                    data.append({
                        'title': activity.title,
                        'description': activity.description,
                        'category': activity.category.value,
                        'recurrence': activity.recurrence_type.value,
                        'next_due_date': activity.next_due_date.isoformat() if activity.next_due_date else None,
                        'status': 'completed' if activity.is_completed else 'pending',
                        'created': activity.start_date.isoformat() if activity.start_date else None
                    })
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
            
            QMessageBox.information(self, "Export Successful", f"Activities exported to {filename}")
            dialog.close()
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
    
    def import_activities(self):
        """Import activities from file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Activities", "", "CSV files (*.csv);;JSON files (*.json)"
        )
        
        if not filename:
            return
        
        try:
            activities_to_add = []
            
            if filename.endswith('.csv'):
                with open(filename, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        activities_to_add.append({
                            'title': row['Title'],
                            'description': row['Description'],
                            'category': CategoryType[row['Category'].upper().replace(' ', '_')],
                            'recurrence_type': RecurrenceType[row['Recurrence'].upper().replace(' ', '_')],
                            'next_due_date': datetime.fromisoformat(row['Next Due']) if row['Next Due'] else datetime.now(),
                        })
            else:  # JSON
                with open(filename, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        activities_to_add.append({
                            'title': item['title'],
                            'description': item['description'],
                            'category': CategoryType[item['category'].upper()],
                            'recurrence_type': RecurrenceType[item['recurrence'].upper()],
                            'next_due_date': datetime.fromisoformat(item['next_due_date']) if item['next_due_date'] else datetime.now(),
                        })
            
            if activities_to_add:
                session = get_session()
                try:
                    for activity_data in activities_to_add:
                        ActivityManager.create_activity(session, **activity_data)
                    QMessageBox.information(self, "Import Successful", f"Imported {len(activities_to_add)} activities.")
                    self.refresh_activities()
                finally:
                    session.close()
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import: {str(e)}")

    def _show_templates(self):
        """Open the quick activity templates dialog."""
        from src.ui.components.data_importers import QuickTemplatesDialog
        dlg = QuickTemplatesDialog(self)
        if dlg.exec():
            self.refresh_activities()

    def _import_calendar(self):
        """Open the ICS calendar import dialog."""
        from src.ui.components.data_importers import CalendarImportDialog
        dlg = CalendarImportDialog(self)
        if dlg.exec():
            self.refresh_activities()

    @pyqtSlot()
    def add_activity(self):
        """Show add activity dialog"""
        dialog = ActivityDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            activity_data = dialog.get_data()
            session = get_session()
            try:
                ActivityManager.create_activity(session, **activity_data)
                self.refresh_activities()
                QMessageBox.information(self, "Success", "Activity created successfully!")
            finally:
                session.close()
    
    @pyqtSlot(int)
    def edit_activity(self, activity_id: int):
        """Edit existing activity"""
        session = get_session()
        try:
            activity = ActivityManager.get_activity(session, activity_id)
            if activity:
                dialog = ActivityDialog(activity)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    activity_data = dialog.get_data()
                    ActivityManager.update_activity(session, activity_id, **activity_data)
                    self.refresh_activities()
                    QMessageBox.information(self, "Success", "Activity updated successfully!")
        finally:
            session.close()
    
    @pyqtSlot(int)
    def delete_activity(self, activity_id: int):
        """Delete activity"""
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this activity?")
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
                ActivityManager.delete_activity(session, activity_id)
                self.refresh_activities()
                QMessageBox.information(self, "Success", "Activity deleted successfully!")
            finally:
                session.close()

    def _on_row_double_clicked(self, row: int, column: int):
        """Handle double-click on a table row to show activity details"""
        try:
            item = self.table.item(row, 1)
            if item:
                # Title cell contains tooltip with description; find activity id via checkbox widget
                checkbox = self.table.cellWidget(row, 0)
                activity_id = checkbox.property('activity_id') if checkbox else None
                if activity_id:
                    self.show_activity_detail(activity_id)
        except Exception:
            pass

    def show_activity_detail(self, activity_id: int):
        """Open a read-only dialog showing activity details"""
        session = get_session()
        try:
            activity = ActivityManager.get_activity(session, activity_id)
            if not activity:
                return
            dlg = QDialog(self)
            dlg.setWindowTitle("Activity Details")
            dlg.setGeometry(300, 300, 480, 380)
            layout = QVBoxLayout()
            title = QLabel(activity.title)
            title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            layout.addWidget(title)

            desc = QLabel(activity.description or "No description")
            desc.setWordWrap(True)
            layout.addWidget(desc)

            meta = QLabel(f"Category: {activity.category.value.title()}  •  Recurrence: {activity.recurrence_type.value.title()}")
            layout.addWidget(meta)

            due = QLabel(f"Next due: {activity.next_due_date.strftime('%Y-%m-%d %H:%M') if activity.next_due_date else 'N/A'}")
            layout.addWidget(due)

            btn = PremiumButton("Close", style=PremiumButton.Style.FLAT, icon_name="close")
            btn.clicked.connect(dlg.accept)
            layout.addWidget(btn)

            dlg.setLayout(layout)
            dlg.exec()
        finally:
            session.close()


class ActivityDialog(QDialog):
    """Dialog for adding/editing activities"""
    
    def __init__(self, activity=None):
        super().__init__()
        self.activity = activity
        self.setWindowTitle("Activity Details")
        self.setGeometry(200, 200, 500, 600)
        self._setup_ui()
        
        if activity:
            self._populate_fields(activity)
    
    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QFormLayout()
        layout.setSpacing(15)
        
        # Title
        self.title_input = QLineEdit()
        layout.addRow("Title:", self.title_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        layout.addRow("Description:", self.description_input)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems([c.value.title() for c in CategoryType])
        layout.addRow("Category:", self.category_combo)
        
        # Recurrence type
        self.recurrence_combo = QComboBox()
        self.recurrence_combo.addItems([r.value.title() for r in RecurrenceType])
        layout.addRow("Recurrence:", self.recurrence_combo)
        
        # Recurrence interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(365)
        layout.addRow("Interval (days):", self.interval_spin)
        
        # Start date
        self.start_date = QDateTimeEdit()
        self.start_date.setDateTime(QDateTime.currentDateTime())
        layout.addRow("Start Date:", self.start_date)
        
        # Due date
        self.next_due_date = QDateTimeEdit()
        self.next_due_date.setDateTime(QDateTime.currentDateTime())
        layout.addRow("Next Due Date:", self.next_due_date)
        
        # Reminder days before
        self.reminder_days = QSpinBox()
        self.reminder_days.setMinimum(0)
        self.reminder_days.setMaximum(365)
        self.reminder_days.setValue(1)
        layout.addRow("Remind (days before):", self.reminder_days)
        
        # Reminder hours before
        self.reminder_hours = QSpinBox()
        self.reminder_hours.setMinimum(0)
        self.reminder_hours.setMaximum(24)
        layout.addRow("Remind (hours before):", self.reminder_hours)

        # Tags / labels
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("e.g. urgent, finance, personal (comma-separated)")
        layout.addRow("Tags:", self.tags_input)
        
        # Send notification
        self.notification_check = QCheckBox("Send notifications")
        self.notification_check.setChecked(True)
        layout.addRow("", self.notification_check)
        
        # Active
        self.active_check = QCheckBox("Active")
        self.active_check.setChecked(True)
        layout.addRow("", self.active_check)
        
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
    
    def _populate_fields(self, activity):
        """Populate form fields from activity"""
        self.title_input.setText(activity.title)
        self.description_input.setText(activity.description or "")
        self.category_combo.setCurrentText(activity.category.value.title())
        self.recurrence_combo.setCurrentText(activity.recurrence_type.value.title())
        self.interval_spin.setValue(activity.recurrence_interval)
        self.start_date.setDateTime(activity.start_date)
        self.next_due_date.setDateTime(activity.next_due_date)
        self.reminder_days.setValue(activity.reminder_days_before)
        self.reminder_hours.setValue(activity.reminder_hours_before)
        self.tags_input.setText(activity.tags or "")
        self.notification_check.setChecked(activity.send_notification)
        self.active_check.setChecked(activity.is_active)
    
    def get_data(self):
        """Get form data"""
        return {
            "title": self.title_input.text(),
            "description": self.description_input.toPlainText(),
            "category": CategoryType[self.category_combo.currentText().upper()],
            "recurrence_type": RecurrenceType[self.recurrence_combo.currentText().upper()],
            "recurrence_interval": self.interval_spin.value(),
            "start_date": self.start_date.dateTime().toPyDateTime(),
            "next_due_date": self.next_due_date.dateTime().toPyDateTime(),
            "reminder_days_before": self.reminder_days.value(),
            "reminder_hours_before": self.reminder_hours.value(),
            "tags": self.tags_input.text().strip(),
            "send_notification": self.notification_check.isChecked(),
            "is_active": self.active_check.isChecked(),
        }
