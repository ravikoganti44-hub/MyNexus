"""
Budget Tracker widget — monthly budget limits, expense entries, category progress bars.
"""
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit,
    QDoubleSpinBox, QComboBox, QDateEdit, QMessageBox, QScrollArea,
    QProgressBar, QHeaderView, QSizePolicy,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

from src.database.config import get_session
from src.database.operations import BudgetManager
from src.ui.components.premium_button import PremiumButton
from src.ui.components.stat_card import StatCard
from src.ui.components.ai_insights_panel import AIInsightsPanel
from src.ui.styles.tokens import token, spacing
from src.core.ai_engine import NexusAI

BUDGET_CATEGORIES = [
    "Housing", "Food & Groceries", "Transportation", "Utilities",
    "Healthcare", "Entertainment", "Shopping", "Insurance",
    "Subscriptions", "Savings", "Investment", "Education",
    "Personal Care", "Dining Out", "Travel", "Other",
]


class BudgetTrackerWidget(QWidget):
    """Full-page Budget Tracker with category progress bars and expense table."""

    def __init__(self):
        super().__init__()
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        self._period_id: int | None = None
        self._setup_ui()
        self.refresh_data()

    # ── UI construction ────────────────────────────────────────────────────────

    def _setup_ui(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""QScrollArea {{ background-color: {token("color.bg.primary")}; border: none; }}""")

        content = QWidget()
        main = QVBoxLayout()
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(20)

        # ── Header ──────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        title = QLabel("Budget Tracker")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setObjectName("titleLabel")
        hdr.addWidget(title)
        hdr.addStretch()

        set_limits_btn = PremiumButton("Set Limits", style=PremiumButton.Style.SECONDARY,
                                       icon_name="edit")
        set_limits_btn.clicked.connect(self._show_set_limits_dialog)
        hdr.addWidget(set_limits_btn)

        copy_btn = PremiumButton("Copy Previous Month", style=PremiumButton.Style.FLAT,
                                 icon_name="copy")
        copy_btn.clicked.connect(self._copy_previous_month)
        hdr.addWidget(copy_btn)

        add_btn = PremiumButton("Add Expense", style=PremiumButton.Style.PRIMARY,
                                icon_name="add")
        add_btn.clicked.connect(self._show_add_expense_dialog)
        hdr.addWidget(add_btn)

        refresh_btn = PremiumButton("Refresh", style=PremiumButton.Style.FLAT,
                                    icon_name="refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        hdr.addWidget(refresh_btn)

        export_btn = PremiumButton("Export", style=PremiumButton.Style.FLAT,
                                   icon_name="download")
        export_btn.clicked.connect(self._export_budget)
        hdr.addWidget(export_btn)

        import_stmt_btn = PremiumButton("Import Statement", style=PremiumButton.Style.FLAT,
                                        icon_name="upload")
        import_stmt_btn.setToolTip("Import transactions from bank statement CSV")
        import_stmt_btn.clicked.connect(self._import_bank_statement)
        hdr.addWidget(import_stmt_btn)

        main.addLayout(hdr)

        # ── Month navigation ─────────────────────────────────────────────────
        nav = QHBoxLayout()
        nav.setSpacing(8)

        self.prev_btn = self._nav_arrow("◀")
        self.prev_btn.clicked.connect(self._prev_month)

        self.month_label = QLabel()
        self.month_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.month_label.setStyleSheet(f"color: {token('color.text.primary')};")
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_label.setMinimumWidth(160)

        self.next_btn = self._nav_arrow("▶")
        self.next_btn.clicked.connect(self._next_month)

        nav.addWidget(self.prev_btn)
        nav.addWidget(self.month_label)
        nav.addWidget(self.next_btn)
        nav.addStretch()
        main.addLayout(nav)

        # ── Stat cards ───────────────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        self.card_budget    = StatCard("Total Budget",  "$0",  "💰", "#3fb950")
        self.card_spent     = StatCard("Total Spent",   "$0",  "💳", "#f59e0b")
        self.card_income    = StatCard("Total Income",  "$0",  "📈", "#3fb950")
        self.card_remaining = StatCard("Remaining",     "$0",  "✅", "#58a6ff")
        for c in (self.card_budget, self.card_spent, self.card_income, self.card_remaining):
            cards_row.addWidget(c)
        main.addLayout(cards_row)

        # ── Category progress bars ────────────────────────────────────────────
        main.addWidget(self._section_sep())
        cat_title = QLabel("📊 Spending by Category")
        cat_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        cat_title.setStyleSheet("color: #58a6ff;")
        main.addWidget(cat_title)

        self.category_frame = QFrame()
        self.category_frame.setObjectName("card")
        self.category_layout = QVBoxLayout(self.category_frame)
        self.category_layout.setContentsMargins(16, 16, 16, 16)
        self.category_layout.setSpacing(12)
        main.addWidget(self.category_frame)

        # ── Expenses table ────────────────────────────────────────────────────
        main.addWidget(self._section_sep())
        exp_title = QLabel("📝 Expense Entries")
        exp_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        exp_title.setStyleSheet("color: #58a6ff;")
        main.addWidget(exp_title)

        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(6)
        self.expenses_table.setHorizontalHeaderLabels(
            ["Date", "Title", "Category", "Amount", "Notes", ""])
        self.expenses_table.setMinimumHeight(200)
        self.expenses_table.setAlternatingRowColors(True)
        self.expenses_table.verticalHeader().setVisible(False)
        self.expenses_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.expenses_table.setStyleSheet("""
            QTableWidget {
                background-color: #161b22; alternate-background-color: #21262d;
                gridline-color: #30363d; border: 1px solid #30363d; border-radius: 8px;
            }
            QTableWidget::item { padding: 8px; color: #c9d1d9; }
            QHeaderView::section {
                background: #1c2128; color: #8b949e; padding: 10px 8px;
                border: none; border-bottom: 2px solid #30363d;
                font-weight: 700; font-size: 11px; text-transform: uppercase;
            }
        """)
        h = self.expenses_table.horizontalHeader()
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.expenses_table.setColumnWidth(0, 100)
        self.expenses_table.setColumnWidth(2, 140)
        self.expenses_table.setColumnWidth(3, 90)
        self.expenses_table.setColumnWidth(5, 90)
        main.addWidget(self.expenses_table)

        # ── AI Budget Insights ────────────────────────────────────────────
        main.addWidget(self._section_sep())
        self.budget_ai_panel = AIInsightsPanel()
        main.addWidget(self.budget_ai_panel)

        main.addStretch()
        content.setLayout(main)
        scroll.setWidget(content)
        outer.addWidget(scroll)
        self.setLayout(outer)

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _nav_arrow(symbol: str) -> QPushButton:
        btn = QPushButton(symbol)
        btn.setFixedSize(36, 36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(88,166,255,0.08); color: #58a6ff;
                border: 1px solid rgba(88,166,255,0.2); border-radius: 8px; font-size: 14px;
            }
            QPushButton:hover { background: rgba(88,166,255,0.15); }
        """)
        return btn

    @staticmethod
    def _section_sep() -> QFrame:
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {token('color.border.default')};")
        return sep

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_data()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_data()

    # ── Data refresh ───────────────────────────────────────────────────────────

    def refresh_data(self):
        self.month_label.setText(
            datetime(self.current_year, self.current_month, 1).strftime("%B %Y"))

        session = get_session()
        try:
            period = BudgetManager.get_or_create_period(
                session, self.current_year, self.current_month)
            self._period_id = period.id
            limits   = {lim.category: lim.limit_amount
                        for lim in BudgetManager.get_limits(session, period.id)}
            spending = BudgetManager.get_spending_by_category(session, period.id)
            entries  = BudgetManager.get_entries(session, period.id)
        finally:
            session.close()

        self._refresh_stats(limits, spending)
        self._refresh_category_bars(limits, spending)
        self._refresh_expenses_table(entries)

        # ── AI insights for budget ────────────────────────────────────────
        session2 = get_session()
        try:
            budget_insights = NexusAI.analyse_budget(session2)
            self.budget_ai_panel.set_insights(budget_insights)
        except Exception:
            pass
        finally:
            session2.close()

    def _refresh_stats(self, limits: dict, spending: dict):
        total_budget = sum(limits.values())
        # Separate expenses (positive amounts) from income (negative amounts)
        total_expenses = sum(v for v in spending.values() if v > 0)
        total_income   = sum(abs(v) for v in spending.values() if v < 0)
        remaining      = total_budget - total_expenses + total_income

        self.card_budget.set_value(f"${total_budget:,.0f}")
        self.card_spent.set_value(f"${total_expenses:,.0f}")
        self.card_income.set_value(f"${total_income:,.0f}")
        self.card_remaining.set_value(f"${remaining:,.0f}")
        self.card_remaining.set_color("#f85149" if remaining < 0 else "#58a6ff")

    def _refresh_category_bars(self, limits: dict, spending: dict):
        self._clear_layout(self.category_layout)

        all_cats = sorted(set(list(limits.keys()) + list(spending.keys())))
        if not all_cats:
            msg = QLabel(
                "No budget categories set yet.  Click \"Set Limits\" to define your monthly budget.")
            msg.setStyleSheet("color: #4b5563; font-size: 13px;")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.category_layout.addWidget(msg)
            return

        for cat in all_cats:
            raw_amt = spending.get(cat, 0.0)
            limit = limits.get(cat, 0.0)
            is_income = raw_amt < 0
            display_amt = abs(raw_amt)

            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(12)

            cat_lbl = QLabel(cat)
            cat_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
            cat_lbl.setStyleSheet("color: #c9d1d9;")
            cat_lbl.setFixedWidth(160)
            row.addWidget(cat_lbl)

            bar = QProgressBar()
            bar.setMinimum(0)
            if is_income:
                bar.setMaximum(max(int(display_amt * 100), 100))
                bar.setValue(int(display_amt * 100))
                bar_color = "#3fb950"  # green for income
            else:
                bar.setMaximum(max(int(limit * 100), int(display_amt * 100) + 1, 100))
                bar.setValue(int(display_amt * 100))
                pct = (display_amt / limit * 100) if limit > 0 else 100.0
                bar_color = "#f85149" if pct >= 100 else ("#f59e0b" if pct >= 80 else "#3fb950")
            bar.setFixedHeight(16)
            bar.setTextVisible(False)
            bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            bar.setStyleSheet(f"""
                QProgressBar {{ background-color: #30363d; border-radius: 8px; border: none; }}
                QProgressBar::chunk {{ background-color: {bar_color}; border-radius: 8px; }}
            """)
            row.addWidget(bar, 1)

            if is_income:
                amounts = QLabel(f"+${display_amt:,.0f}")
            else:
                amounts = QLabel(f"${display_amt:,.0f} / ${limit:,.0f}")
            amounts.setFont(QFont("Segoe UI", 9))
            amounts.setStyleSheet(f"color: {bar_color}; min-width: 130px;")
            amounts.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(amounts)

            self.category_layout.addWidget(row_widget)

    def _refresh_expenses_table(self, entries):
        self.expenses_table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            self.expenses_table.setItem(
                row, 0, QTableWidgetItem(entry.entry_date.strftime("%Y-%m-%d")))
            self.expenses_table.setItem(row, 1, QTableWidgetItem(entry.title))
            self.expenses_table.setItem(row, 2, QTableWidgetItem(entry.category))

            if entry.amount < 0:
                amt_item = QTableWidgetItem(f"+${abs(entry.amount):,.2f}")
                amt_item.setForeground(QColor("#3fb950"))
            else:
                amt_item = QTableWidgetItem(f"${entry.amount:,.2f}")
                amt_item.setForeground(QColor("#f59e0b"))
            self.expenses_table.setItem(row, 3, amt_item)

            self.expenses_table.setItem(row, 4, QTableWidgetItem(entry.notes or ""))

            del_btn = PremiumButton("Delete", style=PremiumButton.Style.GHOST_DANGER,
                                    icon_name="delete")
            del_btn.setFixedHeight(30)
            del_btn.clicked.connect(lambda _checked, eid=entry.id: self._delete_entry(eid))
            cell = QWidget()
            cl = QHBoxLayout(cell)
            cl.setContentsMargins(4, 2, 4, 2)
            cl.addWidget(del_btn)
            self.expenses_table.setCellWidget(row, 5, cell)
            self.expenses_table.setRowHeight(row, 44)

    # ── Actions ────────────────────────────────────────────────────────────────

    def _delete_entry(self, entry_id: int):
        reply = QMessageBox.question(
            self, "Confirm Delete", "Delete this expense entry?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
                BudgetManager.delete_entry(session, entry_id)
            finally:
                session.close()
            self.refresh_data()

    def _copy_previous_month(self):
        """Copy budget limits from the previous month as a template."""
        prev_month = self.current_month - 1
        prev_year = self.current_year
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1

        session = get_session()
        try:
            prev_period = BudgetManager.get_or_create_period(session, prev_year, prev_month)
            prev_limits = BudgetManager.get_limits(session, prev_period.id)
            if not prev_limits:
                QMessageBox.information(
                    self, "No Data",
                    f"No budget limits found for {datetime(prev_year, prev_month, 1).strftime('%B %Y')}."
                )
                return

            reply = QMessageBox.question(
                self, "Copy Limits",
                f"Copy {len(prev_limits)} budget limits from "
                f"{datetime(prev_year, prev_month, 1).strftime('%B %Y')} "
                f"to {datetime(self.current_year, self.current_month, 1).strftime('%B %Y')}?\n\n"
                "Existing limits for this month will be overwritten.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            cur_period = BudgetManager.get_or_create_period(
                session, self.current_year, self.current_month)
            for lim in prev_limits:
                BudgetManager.set_limit(session, cur_period.id, lim.category, lim.limit_amount)
        finally:
            session.close()
        self.refresh_data()
        QMessageBox.information(self, "Copied", "Budget limits copied successfully.")

    def _export_budget(self):
        """Export current month budget data to JSON."""
        import json as _json
        from PyQt6.QtWidgets import QFileDialog
        month_name = datetime(self.current_year, self.current_month, 1).strftime("%B_%Y")
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Budget", f"budget_{month_name}.json", "JSON Files (*.json)"
        )
        if not path:
            return
        session = get_session()
        try:
            period = BudgetManager.get_or_create_period(session, self.current_year, self.current_month)
            limits = {lim.category: lim.limit_amount for lim in BudgetManager.get_limits(session, period.id)}
            entries = BudgetManager.get_entries(session, period.id)
            data = {
                "month": self.current_month,
                "year": self.current_year,
                "limits": limits,
                "entries": [
                    {"title": e.title, "amount": e.amount, "category": e.category,
                     "date": str(e.entry_date), "notes": e.notes}
                    for e in entries
                ],
            }
            with open(path, "w", encoding="utf-8") as f:
                _json.dump(data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Export", f"Budget exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
        finally:
            session.close()

    def _import_bank_statement(self):
        """Open bank statement CSV import dialog."""
        from src.ui.components.data_importers import BankStatementImportDialog
        dlg = BankStatementImportDialog(self, year=self.current_year, month=self.current_month)
        if dlg.exec():
            self.refresh_data()

    def _show_set_limits_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Monthly Budget Limits")
        dialog.setMinimumWidth(480)
        dialog.setStyleSheet(
            "QDialog { background-color: #161b22; }"
            "QLabel  { color: #c9d1d9; }"
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        month_name = datetime(self.current_year, self.current_month, 1).strftime("%B %Y")
        hdr = QLabel(f"Budget Limits for {month_name}")
        hdr.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        hdr.setStyleSheet("color: #58a6ff;")
        layout.addWidget(hdr)

        # Load existing limits
        session = get_session()
        try:
            period = BudgetManager.get_or_create_period(
                session, self.current_year, self.current_month)
            existing = {lim.category: lim.limit_amount
                        for lim in BudgetManager.get_limits(session, period.id)}
        finally:
            session.close()

        spin_map: dict[str, QDoubleSpinBox] = {}
        for cat in BUDGET_CATEGORIES:
            row = QHBoxLayout()
            lbl = QLabel(cat)
            lbl.setFixedWidth(180)
            lbl.setFont(QFont("Segoe UI", 10))
            spin = QDoubleSpinBox()
            spin.setPrefix("$")
            spin.setRange(0, 999_999)
            spin.setDecimals(0)
            spin.setValue(existing.get(cat, 0.0))
            spin.setStyleSheet(
                "QDoubleSpinBox { background: #21262d; color: #e6edf3; "
                "border: 1px solid #30363d; border-radius: 6px; padding: 4px 8px; }")
            spin.setMinimumWidth(130)
            spin_map[cat] = spin
            row.addWidget(lbl)
            row.addWidget(spin)
            layout.addLayout(row)

        btns = QHBoxLayout()
        save_btn   = PremiumButton("Save Limits", style=PremiumButton.Style.PRIMARY,   icon_name="save")
        cancel_btn = PremiumButton("Cancel",      style=PremiumButton.Style.FLAT,       icon_name="close")

        def _save():
            session2 = get_session()
            try:
                period2 = BudgetManager.get_or_create_period(
                    session2, self.current_year, self.current_month)
                for cat, spin in spin_map.items():
                    if spin.value() > 0:
                        BudgetManager.set_limit(session2, period2.id, cat, spin.value())
            finally:
                session2.close()
            dialog.accept()
            self.refresh_data()

        save_btn.clicked.connect(_save)
        cancel_btn.clicked.connect(dialog.reject)
        btns.addStretch()
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)
        dialog.setLayout(layout)
        dialog.exec()

    def _show_add_expense_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Expense")
        dialog.setMinimumWidth(420)
        dialog.setStyleSheet(
            "QDialog { background-color: #161b22; }"
            "QLabel  { color: #c9d1d9; }"
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        hdr = QLabel("New Expense Entry")
        hdr.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        hdr.setStyleSheet("color: #58a6ff;")
        layout.addWidget(hdr)

        form = QFormLayout()
        form.setSpacing(10)

        field_style = ("background: #21262d; color: #e6edf3; "
                       "border: 1px solid #30363d; border-radius: 6px; padding: 8px;")

        title_edit = QLineEdit()
        title_edit.setPlaceholderText("e.g. Grocery run, Rent payment  (🤖 AI auto-categorises)")
        title_edit.setStyleSheet(f"QLineEdit {{ {field_style} }}")

        amount_spin = QDoubleSpinBox()
        amount_spin.setPrefix("$")
        amount_spin.setRange(0.01, 999_999)
        amount_spin.setDecimals(2)
        amount_spin.setStyleSheet(
            f"QDoubleSpinBox {{ {field_style} }}")

        cat_combo = QComboBox()
        cat_combo.addItems(BUDGET_CATEGORIES)
        cat_combo.setStyleSheet(
            f"QComboBox {{ {field_style} }}")

        # AI auto-category suggestion
        ai_cat_hint = QLabel("")
        ai_cat_hint.setFont(QFont("Segoe UI", 8))
        ai_cat_hint.setStyleSheet("color: #a78bfa; padding: 0;")

        def _on_title_changed(text):
            if len(text) >= 3:
                suggested = NexusAI.suggest_category(text)
                if suggested != "Other":
                    ai_cat_hint.setText(f"🤖 Suggested: {suggested}")
                    idx = cat_combo.findText(suggested)
                    if idx >= 0:
                        cat_combo.setCurrentIndex(idx)
                else:
                    ai_cat_hint.setText("")
            else:
                ai_cat_hint.setText("")

        title_edit.textChanged.connect(_on_title_changed)

        date_edit = QDateEdit(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        date_edit.setStyleSheet(f"QDateEdit {{ {field_style} }}")

        notes_edit = QLineEdit()
        notes_edit.setPlaceholderText("Optional notes")
        notes_edit.setStyleSheet(f"QLineEdit {{ {field_style} }}")

        form.addRow("Title *:", title_edit)
        form.addRow("", ai_cat_hint)
        form.addRow("Amount *:", amount_spin)
        form.addRow("Category *:", cat_combo)
        form.addRow("Date:", date_edit)
        form.addRow("Notes:", notes_edit)
        layout.addLayout(form)

        btns = QHBoxLayout()
        save_btn   = PremiumButton("Add Expense", style=PremiumButton.Style.PRIMARY,  icon_name="add")
        cancel_btn = PremiumButton("Cancel",       style=PremiumButton.Style.FLAT,     icon_name="close")

        def _save():
            if not title_edit.text().strip():
                QMessageBox.warning(dialog, "Required Field", "Please enter an expense title.")
                return
            if amount_spin.value() <= 0:
                QMessageBox.warning(dialog, "Invalid Amount", "Amount must be greater than zero.")
                return
            d = date_edit.date()
            entry_date = datetime(d.year(), d.month(), d.day())
            session = get_session()
            try:
                BudgetManager.add_entry(
                    session, self._period_id or 0,
                    title=title_edit.text().strip(),
                    amount=amount_spin.value(),
                    category=cat_combo.currentText(),
                    entry_date=entry_date,
                    notes=notes_edit.text().strip() or None,
                )
            finally:
                session.close()
            dialog.accept()
            self.refresh_data()

        save_btn.clicked.connect(_save)
        cancel_btn.clicked.connect(dialog.reject)
        btns.addStretch()
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)
        dialog.setLayout(layout)
        dialog.exec()
