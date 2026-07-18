"""
Document Vault Component
Provides document storage, organization, and preview functionality
"""
import os
import json
import shutil
import functools
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QFrame, QComboBox, QLineEdit, QHeaderView,
    QMessageBox, QDialog, QFormLayout, QSpinBox, QTextEdit, QCheckBox,
    QSplitter, QListWidget, QListWidgetItem, QAbstractItemView, QScrollArea,
    QGridLayout, QTabWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QDateTime, QTimer
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap

from src.ui.styles.icon_manager import IconManager
from src.database.config import get_session
from src.database.operations import DocumentManager
from src.database.models import Document, DocumentCategory, DocumentType
from src.core.ai_engine import NexusAI
from src.ui.components.ai_insights_panel import AIInsightsPanel


class DocumentVaultWidget(QWidget):
    """Main Document Vault widget"""
    
    MAX_FILE_SIZE_MB = 50  # Maximum file size in megabytes
    
    def __init__(self):
        super().__init__()
        self.documents_dir = Path("data/documents")
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.current_category = None
        self.current_sub_category = None
        self.setAcceptDrops(True)
        self._setup_ui()
        self._load_documents()
    
    def _setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("📁 Document Vault")
        header_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_label.setObjectName("pageTitle")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Action buttons
        upload_btn = QPushButton("  ⬆  Upload Document")
        upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_btn.clicked.connect(self._on_upload_document)
        upload_btn.setObjectName("primaryButton")
        upload_btn.setFixedHeight(36)
        upload_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        upload_btn.setMinimumWidth(148)
        header_layout.addWidget(upload_btn)

        scan_folder_btn = QPushButton("  📂  Scan Folder")
        scan_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        scan_folder_btn.clicked.connect(self._scan_folder_import)
        scan_folder_btn.setObjectName("secondaryButton")
        scan_folder_btn.setFixedHeight(36)
        scan_folder_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        scan_folder_btn.setMinimumWidth(140)
        scan_folder_btn.setToolTip("Scan a folder and bulk-import documents with auto-categorization")
        header_layout.addWidget(scan_folder_btn)
        
        main_layout.addLayout(header_layout)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("separator")
        main_layout.addWidget(sep)
        
        # Tab widget for different views
        tab_widget = QTabWidget()
        tab_widget.setObjectName("tabWidget")
        
        # Tab 1: Browse Documents
        browse_widget = self._create_browse_tab()
        tab_widget.addTab(browse_widget, "Browse Documents")
        
        # Tab 2: My Favorites
        favorites_widget = self._create_favorites_tab()
        tab_widget.addTab(favorites_widget, "Favorites")
        
        # Tab 3: Statistics
        stats_widget = self._create_stats_tab()
        tab_widget.addTab(stats_widget, "Statistics")
        tab_widget.currentChanged.connect(lambda _: self._schedule_layout_refresh())
        
        main_layout.addWidget(tab_widget)
        self.tab_widget = tab_widget
    
    def _create_browse_tab(self) -> QWidget:
        """Create browse documents tab"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Left sidebar - Categories
        left_frame = QFrame()
        left_frame.setObjectName("categoryFrame")
        left_layout = QVBoxLayout(left_frame)
        
        category_label = QLabel("Categories")
        category_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        left_layout.addWidget(category_label)
        
        # Category list
        self.category_list = QListWidget()
        self.category_list.setObjectName("categoryList")
        self.category_list.itemClicked.connect(self._on_category_selected)
        left_layout.addWidget(self.category_list)
        
        # Populate categories
        categories = [
            ("📄 All Documents", None),
            ("🛂 Passports", DocumentCategory.PASSPORT),
            ("📊 Tax Documents", DocumentCategory.TAX_DOCUMENTS),
            ("🏠 Property Documents", DocumentCategory.PROPERTY_DOCUMENTS),
            ("🎓 Certificates", DocumentCategory.CERTIFICATES),
            ("✈️ Immigration", DocumentCategory.IMMIGRATION_DOCUMENTS),
            ("⚕️ Medical Records", DocumentCategory.MEDICAL_RECORDS),
            ("🛡️ Insurance", DocumentCategory.INSURANCE_DOCUMENTS),
            ("💰 Financial", DocumentCategory.FINANCIAL_DOCUMENTS),
            ("⚖️ Legal Documents", DocumentCategory.LEGAL_DOCUMENTS),
            ("📎 Other", DocumentCategory.OTHER),
        ]
        
        for label, category in categories:
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, category)
            self.category_list.addItem(item)
        
        # Select first item
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)
        
        left_frame.setMinimumWidth(176)
        left_frame.setMaximumWidth(188)
        layout.addWidget(left_frame)
        
        # Right side - Documents list and controls
        right_layout = QVBoxLayout()
        
        # Search and filter
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search documents...")
        self.search_field.setMinimumWidth(220)
        self.search_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.search_field.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_field)
        
        self.show_archived_check = QCheckBox("Archived")
        self.show_archived_check.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.show_archived_check.stateChanged.connect(self._on_show_archived_changed)
        search_layout.addWidget(self.show_archived_check, 0, Qt.AlignmentFlag.AlignRight)
        
        right_layout.addLayout(search_layout)
        
        # Documents table
        self.documents_table = QTableWidget()
        self.documents_table.setColumnCount(5)
        self.documents_table.setHorizontalHeaderLabels([
            "Document Name", "Category", "Type · Date", "Reference", "Actions"
        ])
        self.documents_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.documents_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.documents_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.documents_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.documents_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.documents_table.verticalHeader().setDefaultSectionSize(44)
        self.documents_table.verticalHeader().setVisible(False)
        self.documents_table.horizontalHeader().setMinimumSectionSize(52)
        self.documents_table.setShowGrid(False)
        self.documents_table.setAlternatingRowColors(True)
        self.documents_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.documents_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.documents_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.documents_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.documents_table.setObjectName("documentsTable")
        self.documents_table.setStyleSheet("""
            QTableWidget::item { padding: 4px 2px; }
        """)
        right_layout.addWidget(self.documents_table)
        self._update_documents_table_widths()
        
        layout.addLayout(right_layout, 2)
        
        return widget
    
    def _create_favorites_tab(self) -> QWidget:
        """Create favorites tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Favorite Documents")
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(label)
        
        self.favorites_table = QTableWidget()
        self.favorites_table.setColumnCount(4)
        self.favorites_table.setHorizontalHeaderLabels([
            "Document Name", "Category", "Date", "Actions"
        ])
        self.favorites_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.favorites_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.favorites_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.favorites_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.favorites_table.verticalHeader().setDefaultSectionSize(44)
        self.favorites_table.verticalHeader().setVisible(False)
        self.favorites_table.setShowGrid(False)
        self.favorites_table.setAlternatingRowColors(True)
        self.favorites_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.favorites_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.favorites_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.favorites_table.setStyleSheet("""
            QTableWidget::item { padding: 4px 2px; }
        """)
        layout.addWidget(self.favorites_table)
        self._update_favorites_table_widths()
        
        return widget
    
    def _create_stats_tab(self) -> QWidget:
        """Create statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Stats grid
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_layout = QGridLayout(stats_frame)
        
        # Total documents
        total_label = QLabel("Total Documents")
        self.total_docs_value = QLabel("0")
        self.total_docs_value.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        stat_box = QVBoxLayout()
        stat_box.addWidget(total_label)
        stat_box.addWidget(self.total_docs_value)
        stats_layout.addLayout(stat_box, 0, 0)
        
        # Expiring soon
        expiring_label = QLabel("Expiring Soon")
        self.expiring_docs_value = QLabel("0")
        self.expiring_docs_value.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.expiring_docs_value.setStyleSheet(f"color: {token('color.semantic.warning')};")
        stat_box = QVBoxLayout()
        stat_box.addWidget(expiring_label)
        stat_box.addWidget(self.expiring_docs_value)
        stats_layout.addLayout(stat_box, 0, 1)
        
        # Expired
        expired_label = QLabel("Expired")
        self.expired_docs_value = QLabel("0")
        self.expired_docs_value.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.expired_docs_value.setStyleSheet(f"color: {token('color.semantic.error')};")
        stat_box = QVBoxLayout()
        stat_box.addWidget(expired_label)
        stat_box.addWidget(self.expired_docs_value)
        stats_layout.addLayout(stat_box, 0, 2)
        
        layout.addWidget(stats_frame)
        
        # Expiring documents list
        expiring_label = QLabel("Documents Expiring Soon")
        expiring_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(expiring_label)
        
        self.expiring_list = QTableWidget()
        self.expiring_list.setColumnCount(4)
        self.expiring_list.setHorizontalHeaderLabels([
            "Document", "Category", "Expiry Date", "Days Left"
        ])
        self.expiring_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.expiring_list)

        # ── AI Document Insights ──────────────────────────────────────────
        sep_ai = QFrame()
        sep_ai.setFixedHeight(1)
        sep_ai.setStyleSheet(f"background-color: {token('color.border.default')};")
        layout.addWidget(sep_ai)
        self.doc_ai_panel = AIInsightsPanel()
        layout.addWidget(self.doc_ai_panel)
        
        return widget
    
    def _load_documents(self):
        """Load documents from database"""
        try:
            session = get_session()
            docs = DocumentManager.get_all_documents(session)
            self._display_documents(docs)
            self._load_favorites()
            self._load_statistics()
            self._schedule_layout_refresh()
        except Exception as e:
            print(f"Error loading documents: {e}")

    # ── Drag-and-drop support ──────────────────────────────────────────
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle files dropped onto the document vault."""
        if not event.mimeData().hasUrls():
            return
        files = [u.toLocalFile() for u in event.mimeData().urls() if u.toLocalFile()]
        for file_path in files:
            self._import_dropped_file(file_path)
        event.acceptProposedAction()

    def _import_dropped_file(self, file_path: str):
        """Import a single dropped file with size validation."""
        from pathlib import Path as _P
        p = _P(file_path)
        if not p.is_file():
            return
        size_mb = p.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            QMessageBox.warning(
                self, "File Too Large",
                f"{p.name} is {size_mb:.1f} MB.\nMaximum allowed size is {self.MAX_FILE_SIZE_MB} MB."
            )
            return
        # Trigger the upload dialog pre-filled with this file
        self._on_upload_document(prefill_path=str(p))

    def _schedule_layout_refresh(self):
        """Refresh layout after Qt finishes applying pending geometry updates."""
        QTimer.singleShot(0, self.refresh_layout)

    def refresh_layout(self):
        """Public layout refresh for stacked-page activation and resize handling."""
        self._update_documents_table_widths()
        self._update_favorites_table_widths()
        self.documents_table.horizontalScrollBar().setValue(0)
        self.favorites_table.horizontalScrollBar().setValue(0)

    def _update_documents_table_widths(self):
        """Keep the documents table readable across window sizes."""
        viewport_width = max(0, self.documents_table.viewport().width())
        if viewport_width <= 0:
            viewport_width = max(0, self.documents_table.width() - 2)
        if viewport_width <= 0:
            return

        action_width = 200
        remaining = viewport_width - action_width
        # Distribute remaining space: Name 34%, Category 22%, Type 24%, Reference 20%
        category_width = max(110, int(remaining * 0.22))
        type_width = max(120, int(remaining * 0.24))
        reference_width = max(94, int(remaining * 0.20))
        name_width = max(160, remaining - category_width - type_width - reference_width)

        self.documents_table.setColumnWidth(0, name_width)
        self.documents_table.setColumnWidth(1, category_width)
        self.documents_table.setColumnWidth(2, type_width)
        self.documents_table.setColumnWidth(3, reference_width)
        self.documents_table.setColumnWidth(4, action_width)

    def _update_favorites_table_widths(self):
        """Keep the favorites table readable across window sizes."""
        viewport_width = max(0, self.favorites_table.viewport().width())
        if viewport_width <= 0:
            viewport_width = max(0, self.favorites_table.width() - 2)
        if viewport_width <= 0:
            return

        action_width = 200
        remaining = viewport_width - action_width
        # Distribute remaining space proportionally: Name 45%, Category 28%, Date 27%
        category_width = max(110, int(remaining * 0.28))
        date_width = max(108, int(remaining * 0.27))
        name_width = max(180, remaining - category_width - date_width)

        self.favorites_table.setColumnWidth(0, name_width)
        self.favorites_table.setColumnWidth(1, category_width)
        self.favorites_table.setColumnWidth(2, date_width)
        self.favorites_table.setColumnWidth(3, action_width)
    
    def _make_action_widget(self, doc_id: int, is_favorite: bool) -> QWidget:
        """Create styled action buttons container for a document row"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # Preview button — blue accent
        preview_btn = QPushButton("View")
        preview_btn.setFixedSize(52, 26)
        preview_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        preview_btn.setToolTip("Open document in viewer")
        preview_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(56, 139, 253, 0.15);
                color: #6ab0ff;
                border: 1px solid rgba(56, 139, 253, 0.45);
                border-radius: 5px;
                padding: 0 4px;
            }
            QPushButton:hover {
                background-color: rgba(56, 139, 253, 0.30);
                color: #aad4ff;
                border: 1px solid rgba(56, 139, 253, 0.75);
            }
            QPushButton:pressed { background-color: rgba(56, 139, 253, 0.45); }
        """)
        preview_btn.clicked.connect(functools.partial(self._preview_document, doc_id))
        layout.addWidget(preview_btn)

        # Info button — teal accent
        details_btn = QPushButton("Info")
        details_btn.setFixedSize(44, 26)
        details_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        details_btn.setToolTip("View document details")
        details_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        details_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(45, 194, 168, 0.12);
                color: #4dd9bb;
                border: 1px solid rgba(45, 194, 168, 0.40);
                border-radius: 5px;
                padding: 0 4px;
            }
            QPushButton:hover {
                background-color: rgba(45, 194, 168, 0.25);
                color: #88ebd6;
                border: 1px solid rgba(45, 194, 168, 0.70);
            }
            QPushButton:pressed { background-color: rgba(45, 194, 168, 0.40); }
        """)
        details_btn.clicked.connect(functools.partial(self._view_document_details, doc_id))
        layout.addWidget(details_btn)

        # Favorite button — gold, changes state
        fav_text = "★" if is_favorite else "☆"
        fav_color = "#f5c518" if is_favorite else "#888ea8"
        fav_bg = "rgba(245,197,24,0.15)" if is_favorite else "rgba(136,142,168,0.08)"
        fav_border = "rgba(245,197,24,0.50)" if is_favorite else "rgba(136,142,168,0.30)"
        fav_btn = QPushButton(fav_text)
        fav_btn.setFixedSize(30, 26)
        fav_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fav_btn.setToolTip("Remove from favorites" if is_favorite else "Add to favorites")
        fav_btn.setFont(QFont("Segoe UI", 9))
        fav_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {fav_bg};
                color: {fav_color};
                border: 1px solid {fav_border};
                border-radius: 5px;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: rgba(245,197,24,0.25);
                color: #f5c518;
                border: 1px solid rgba(245,197,24,0.65);
            }}
            QPushButton:pressed {{ background-color: rgba(245,197,24,0.40); }}
        """)
        fav_btn.clicked.connect(functools.partial(self._toggle_favorite, doc_id))
        layout.addWidget(fav_btn)

        # Delete button — red accent
        delete_btn = QPushButton("Del")
        delete_btn.setFixedSize(40, 26)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setToolTip("Delete document")
        delete_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 59, 48, 0.10);
                color: #ff6b6b;
                border: 1px solid rgba(255, 59, 48, 0.40);
                border-radius: 5px;
                padding: 0 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 59, 48, 0.25);
                color: #ff9999;
                border: 1px solid rgba(255, 59, 48, 0.70);
            }
            QPushButton:pressed { background-color: rgba(255, 59, 48, 0.45); }
        """)
        delete_btn.clicked.connect(functools.partial(self._delete_document, doc_id))
        layout.addWidget(delete_btn)

        return container

    def _display_documents(self, documents: List[Document]):
        """Display documents in table"""
        self.documents_table.setRowCount(0)
        
        for doc in documents:
            row = self.documents_table.rowCount()
            self.documents_table.insertRow(row)
            self.documents_table.setRowHeight(row, 44)
            
            # Name
            name_item = QTableWidgetItem(doc.title)
            name_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
            self.documents_table.setItem(row, 0, name_item)
            
            # Category
            category_item = QTableWidgetItem(doc.category.value.replace('_', ' ').title())
            category_item.setForeground(QColor("#8aaefc"))
            self.documents_table.setItem(row, 1, category_item)
            
            # Type + Date
            date_str = doc.created_at.strftime("%Y-%m-%d") if doc.created_at else ""
            type_str = doc.file_type.value.upper() if doc.file_type else "Unknown"
            type_item = QTableWidgetItem(f"{type_str} · {date_str}")
            type_item.setForeground(QColor("#aeb9ca"))
            self.documents_table.setItem(row, 2, type_item)
            
            # Reference / Sub-category
            ref = doc.reference_number or doc.sub_category or ""
            ref_item = QTableWidgetItem(ref)
            ref_item.setForeground(QColor("#aeb9ca"))
            self.documents_table.setItem(row, 3, ref_item)
            
            # Actions column
            action_widget = self._make_action_widget(doc.id, doc.is_favorite)
            self.documents_table.setCellWidget(row, 4, action_widget)
        
        # Always show Document Name column (column 0) — reset horizontal scroll
        self.refresh_layout()
    
    def _load_favorites(self):
        """Load favorite documents"""
        try:
            session = get_session()
            favorites = DocumentManager.get_favorite_documents(session)
            
            self.favorites_table.setRowCount(0)
            for doc in favorites:
                row = self.favorites_table.rowCount()
                self.favorites_table.insertRow(row)
                self.favorites_table.setRowHeight(row, 44)
                
                name_item = QTableWidgetItem(doc.title)
                name_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
                self.favorites_table.setItem(row, 0, name_item)
                
                category_item = QTableWidgetItem(doc.category.value.replace('_', ' ').title())
                category_item.setForeground(QColor("#8aaefc"))
                self.favorites_table.setItem(row, 1, category_item)
                
                date_str = doc.created_at.strftime("%Y-%m-%d") if doc.created_at else ""
                date_item = QTableWidgetItem(date_str)
                date_item.setForeground(QColor("#aeb9ca"))
                self.favorites_table.setItem(row, 2, date_item)
                
                action_widget = self._make_action_widget(doc.id, doc.is_favorite)
                self.favorites_table.setCellWidget(row, 3, action_widget)
            self.refresh_layout()
        except Exception as e:
            print(f"Error loading favorites: {e}")
    
    def _load_statistics(self):
        """Load and display statistics"""
        try:
            session = get_session()
            
            # Total documents
            all_docs = DocumentManager.get_all_documents(session)
            self.total_docs_value.setText(str(len(all_docs)))
            
            # Expiring documents
            expiring = DocumentManager.get_expiring_documents(session, days_ahead=30)
            self.expiring_docs_value.setText(str(len(expiring)))
            
            # Expired documents
            expired = DocumentManager.get_expired_documents(session)
            self.expired_docs_value.setText(str(len(expired)))
            
            # Display expiring documents list
            self.expiring_list.setRowCount(0)
            for doc in expiring:
                row = self.expiring_list.rowCount()
                self.expiring_list.insertRow(row)
                
                name_item = QTableWidgetItem(doc.title)
                self.expiring_list.setItem(row, 0, name_item)
                
                category_item = QTableWidgetItem(doc.category.value.replace('_', ' ').title())
                self.expiring_list.setItem(row, 1, category_item)
                
                expiry_str = doc.expiry_date.strftime("%Y-%m-%d") if doc.expiry_date else "N/A"
                expiry_item = QTableWidgetItem(expiry_str)
                self.expiring_list.setItem(row, 2, expiry_item)
                
                if doc.expiry_date:
                    days_left = (doc.expiry_date - datetime.now()).days
                    days_item = QTableWidgetItem(str(max(0, days_left)))
                    self.expiring_list.setItem(row, 3, days_item)

            # ── AI document insights ──────────────────────────────────
            try:
                doc_insights = NexusAI.analyse_documents(session)
                self.doc_ai_panel.set_insights(doc_insights)
            except Exception:
                pass

        except Exception as e:
            print(f"Error loading statistics: {e}")
    
    def _on_category_selected(self):
        """Handle category selection"""
        item = self.category_list.currentItem()
        if item:
            category = item.data(Qt.ItemDataRole.UserRole)
            self.current_category = category
            self._filter_documents()
    
    def _filter_documents(self):
        """Filter documents by category"""
        try:
            session = get_session()
            if self.current_category is None:
                docs = DocumentManager.get_all_documents(session)
            else:
                docs = DocumentManager.get_documents_by_category(session, self.current_category)
            
            self._display_documents(docs)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to filter documents: {e}")
    
    def _on_search(self):
        """Handle search"""
        search_term = self.search_field.text()
        if not search_term:
            self._filter_documents()
            return
        
        try:
            session = get_session()
            docs = DocumentManager.search_documents(session, search_term)
            self._display_documents(docs)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Search failed: {e}")
    
    def _on_show_archived_changed(self, state):
        """Handle show archived checkbox"""
        # Placeholder for archive functionality
        self._filter_documents()
    
    def _on_upload_document(self, prefill_path: str | None = None):
        """Handle document upload"""
        dialog = DocumentUploadDialog(self, prefill_path=prefill_path)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_documents()

    def _scan_folder_import(self):
        """Open bulk folder scan/import dialog."""
        from src.ui.components.data_importers import BulkDocumentImportDialog
        dlg = BulkDocumentImportDialog(self)
        if dlg.exec():
            self._load_documents()

    def _preview_document(self, doc_id: int):
        """Preview a document"""
        try:
            session = get_session()
            doc = DocumentManager.get_document(session, doc_id)
            if not doc:
                QMessageBox.warning(self, "Error", "Document not found")
                return
            
            # Update last accessed
            DocumentManager.update_last_accessed(session, doc_id)
            
            # Open file with default application
            file_path = Path(doc.file_path)
            if not file_path.exists():
                QMessageBox.critical(self, "Error", f"Document file not found at:\n{file_path}")
                return
            
            # Try to open the file with platform-appropriate method
            try:
                import sys, subprocess
                if sys.platform == "win32":
                    os.startfile(str(file_path))
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", str(file_path)])
                else:
                    subprocess.Popen(["xdg-open", str(file_path)])
                QMessageBox.information(self, "Success", f"Opening: {doc.title}")
            except Exception as open_error:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(open_error)}\n\nFile path: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to preview document:\n{str(e)}")
    
    def _view_document_details(self, doc_id: int):
        """View document details in a dialog"""
        try:
            session = get_session()
            doc = DocumentManager.get_document(session, doc_id)
            if not doc:
                QMessageBox.warning(self, "Error", "Document not found")
                return
            
            # Create details dialog
            details_text = f"""
📄 Document Details
{'='*50}

Title: {doc.title}
Category: {doc.category.value.replace('_', ' ').title()}
Sub-Category: {doc.sub_category or 'N/A'}

File Information:
  Original Name: {doc.original_filename}
  File Type: {doc.file_type.value.upper() if doc.file_type else 'Unknown'}
  File Size: {doc.file_size or 'Unknown'} bytes
  Stored Location: {doc.file_path}

Document Details:
  Reference Number: {doc.reference_number or 'N/A'}
  Issue Date: {doc.issue_date.strftime('%Y-%m-%d') if doc.issue_date else 'N/A'}
  Expiry Date: {doc.expiry_date.strftime('%Y-%m-%d') if doc.expiry_date else 'N/A'}
  
Status:
  Favorite: {'Yes ★' if doc.is_favorite else 'No ☆'}
  Archived: {'Yes' if doc.is_archived else 'No'}
  Encrypted: {'Yes' if doc.is_encrypted else 'No'}

Timestamps:
  Created: {doc.created_at.strftime('%Y-%m-%d %H:%M:%S') if doc.created_at else 'N/A'}
  Last Updated: {doc.updated_at.strftime('%Y-%m-%d %H:%M:%S') if doc.updated_at else 'N/A'}
  Last Accessed: {doc.last_accessed.strftime('%Y-%m-%d %H:%M:%S') if doc.last_accessed else 'Never'}

Description/Notes:
{doc.description or 'No notes'}
            """
            
            QMessageBox.information(self, "Document Details", details_text)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load document details:\n{str(e)}")
    
    def _delete_document(self, doc_id: int):
        """Delete a document with confirmation"""
        try:
            session = get_session()
            doc = DocumentManager.get_document(session, doc_id)
            if not doc:
                QMessageBox.warning(self, "Error", "Document not found")
                return
            
            # Confirm deletion
            reply = QMessageBox.question(
                self,
                "Delete Document?",
                f"Are you sure you want to delete:\n\n{doc.title}\n\nThis action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Delete file from storage
            file_path = Path(doc.file_path)
            if file_path.exists():
                try:
                    file_path.unlink()  # Delete the file
                except Exception as file_error:
                    QMessageBox.warning(self, "Warning", f"File could not be deleted:\n{str(file_error)}\n\nDocument record will still be deleted from database.")
            
            # Delete from database
            DocumentManager.delete_document(session, doc_id)
            
            QMessageBox.information(self, "Success", f"Document '{doc.title}' has been deleted.")
            self._load_documents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete document:\n{str(e)}")
    
    def _toggle_favorite(self, doc_id: int):
        """Toggle document favorite status"""
        try:
            session = get_session()
            DocumentManager.toggle_favorite(session, doc_id)
            self._load_documents()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to toggle favorite: {e}")

    def resizeEvent(self, event):
        """Keep document tables responsive when the page resizes."""
        super().resizeEvent(event)
        self._schedule_layout_refresh()

    def showEvent(self, event):
        """Refresh layout when the page becomes visible in the stacked widget."""
        super().showEvent(event)
        self._schedule_layout_refresh()


class DocumentUploadDialog(QDialog):
    """Dialog for uploading documents"""
    
    def __init__(self, parent=None, prefill_path: str | None = None):
        super().__init__(parent)
        self.selected_file = None
        self.setWindowTitle("Upload Document")
        self.setGeometry(100, 100, 500, 450)
        self._setup_ui()
        if prefill_path:
            self.selected_file = prefill_path
            self.file_label.setText(Path(prefill_path).name)
            if not self.title_input.text():
                self.title_input.setText(Path(prefill_path).stem.replace("_", " ").title())
    
    def _setup_ui(self):
        """Setup upload dialog UI"""
        layout = QFormLayout(self)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        file_btn = QPushButton("Browse...")
        file_btn.clicked.connect(self._select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(file_btn)
        layout.addRow("File:", file_layout)
        
        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., My Passport")
        layout.addRow("Title:", self.title_input)
        
        # Category
        self.category_combo = QComboBox()
        for category in DocumentCategory:
            self.category_combo.addItem(category.value.replace('_', ' ').title(), category)
        layout.addRow("Category:", self.category_combo)
        
        # Sub-category for Tax Documents
        self.subcategory_input = QLineEdit()
        self.subcategory_input.setPlaceholderText("e.g., 2024 (for tax docs)")
        layout.addRow("Sub-Category:", self.subcategory_input)
        
        # Reference number
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("e.g., Passport number")
        layout.addRow("Reference Number:", self.reference_input)
        
        # Issue date
        from PyQt6.QtWidgets import QDateEdit
        self.issue_date = QDateEdit()
        self.issue_date.setDate(QDateTime.currentDateTime().date())
        layout.addRow("Issue Date:", self.issue_date)
        
        # Expiry date
        self.expiry_date = QDateEdit()
        self.expiry_date.setDate(QDateTime.currentDateTime().date())
        layout.addRow("Expiry Date:", self.expiry_date)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional notes about the document")
        self.description_input.setMaximumHeight(80)
        layout.addRow("Description:", self.description_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        upload_btn = QPushButton("Upload")
        cancel_btn = QPushButton("Cancel")
        upload_btn.clicked.connect(self._on_upload)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(upload_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
    
    def _select_file(self):
        """Select file to upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Document",
            "", "All Files (*);;PDF Files (*.pdf);;Images (*.jpg *.jpeg *.png);;Documents (*.doc *.docx *.xlsx)"
        )
        if file_path:
            # File size validation
            max_mb = DocumentVaultWidget.MAX_FILE_SIZE_MB
            size_mb = Path(file_path).stat().st_size / (1024 * 1024)
            if size_mb > max_mb:
                QMessageBox.warning(
                    self, "File Too Large",
                    f"Selected file is {size_mb:.1f} MB.\nMaximum allowed size is {max_mb} MB."
                )
                return
            self.selected_file = file_path
            self.file_label.setText(Path(file_path).name)
    
    def _on_upload(self):
        """Handle upload button click"""
        if not self.selected_file:
            QMessageBox.warning(self, "Error", "Please select a file")
            return
        
        if not self.title_input.text():
            QMessageBox.warning(self, "Error", "Please enter a title")
            return
        
        try:
            # Copy file to documents directory
            documents_dir = Path("data/documents")
            documents_dir.mkdir(parents=True, exist_ok=True)
            
            source = Path(self.selected_file)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_filename = f"{timestamp}_{source.name}"
            dest_path = documents_dir / dest_filename
            
            shutil.copy2(source, dest_path)
            
            # Determine file type
            suffix = source.suffix.lower()
            if suffix == '.pdf':
                file_type = DocumentType.PDF
            elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                file_type = DocumentType.IMAGE
            elif suffix in ['.doc', '.docx']:
                file_type = DocumentType.WORD
            elif suffix in ['.xls', '.xlsx']:
                file_type = DocumentType.EXCEL
            elif suffix == '.txt':
                file_type = DocumentType.TEXT
            else:
                file_type = DocumentType.OTHER
            
            # Save to database
            session = get_session()
            DocumentManager.create_document(
                session=session,
                original_filename=source.name,
                stored_filename=dest_filename,
                file_path=str(dest_path),
                file_size=source.stat().st_size,
                file_type=file_type,
                mime_type=source.suffix,
                title=self.title_input.text(),
                description=self.description_input.toPlainText(),
                category=self.category_combo.currentData(),
                sub_category=self.subcategory_input.text() or None,
                reference_number=self.reference_input.text() or None,
                issue_date=self.issue_date.dateTime().toPyDateTime(),
                expiry_date=self.expiry_date.dateTime().toPyDateTime(),
            )
            
            QMessageBox.information(self, "Success", "Document uploaded successfully")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload document: {e}")
