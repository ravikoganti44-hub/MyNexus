"""
Net Worth — Advanced Wealth Dashboard
--------------------------------------
Features
  * 7 KPI stat-cards: Assets, Liabilities, Net Worth, MoM change, YoY change,
    Debt-to-Asset %, FIRE Progress
  * Allocation donut  (pure-Qt, no matplotlib)
  * Top-8 categories horizontal bar chart (pure-Qt)
  * Net-worth growth sparkline (pure-Qt polyline)
  * Itemised breakdown with percentage share bars
  * Insight chips: MoM/YoY change, best/worst month, FIRE ETA
  * Full snapshot history table with Edit / Delete
  * Snapshot dialog with category autocomplete + live net-worth preview
  * Goals tab: custom wealth target + projected ETA
  * FIRE calculator (25x rule)
"""
import json
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QDialog, QLineEdit, QDoubleSpinBox,
    QDateEdit, QMessageBox, QScrollArea, QHeaderView, QSizePolicy,
    QAbstractItemView, QCompleter, QProgressBar, QTabWidget, QGridLayout,
)
from PyQt6.QtCore import Qt, QDate, QRectF, QPointF
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QPainterPath,
    QLinearGradient, QPolygonF,
)

from src.database.config import get_session
from src.database.operations import NetWorthManager
from src.ui.components.premium_button import PremiumButton
from src.ui.components.stat_card import StatCard
from src.core.ai_engine import NexusAI
from src.ui.components.ai_insights_panel import AIInsightsPanel

# ---------------------------------------------------------------------------
# Category suggestions
# ---------------------------------------------------------------------------
ASSET_CATEGORIES = [
    "Checking Account", "Savings Account", "Emergency Fund",
    "Investments / Stocks", "Index Funds / ETFs",
    "Retirement 401k", "Roth IRA", "HSA",
    "Real Estate (Primary)", "Real Estate (Rental)",
    "Vehicle", "Cryptocurrency", "Bonds / Fixed Income",
    "Business Equity", "Precious Metals", "Cash on Hand",
    "Life Insurance (Cash Value)", "Other Assets",
]
LIABILITY_CATEGORIES = [
    "Primary Mortgage", "Rental Mortgage",
    "Home Equity Loan", "Car Loan", "Car Lease",
    "Student Loan (Federal)", "Student Loan (Private)",
    "Credit Card 1", "Credit Card 2", "Credit Card 3",
    "Personal Loan", "Medical Debt",
    "Business Loan", "Tax Liability", "Other Liabilities",
]

# Palette
_GREEN  = "#3fb950"
_RED    = "#f85149"
_BLUE   = "#58a6ff"
_YELLOW = "#e3b341"
_PURPLE = "#bc8cff"
_ORANGE = "#f0883e"
_BG     = "#0d1117"
_CARD   = "#161b22"
_BORDER = "#30363d"
_TEXT   = "#c9d1d9"
_MUTED  = "#8b949e"

CATEGORY_COLORS = [
    "#58a6ff", "#3fb950", "#f0883e", "#bc8cff",
    "#e3b341", "#39c5cf", "#ff7b72", "#d2a8ff",
    "#7ee787", "#ffa657",
]


# ===========================================================================
#  Mini Chart Widgets  (zero external dependencies)
# ===========================================================================

class _Sparkline(QWidget):
    """Polyline net-worth trend chart."""

    def __init__(self, values=None):
        super().__init__()
        self._values = values or []
        self.setMinimumHeight(60)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_values(self, values):
        self._values = values
        self.update()

    def paintEvent(self, _event):
        if len(self._values) < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        pad  = 6
        mn, mx = min(self._values), max(self._values)
        rng = mx - mn if mx != mn else 1.0

        def pt(i, v):
            x = pad + (i / (len(self._values) - 1)) * (w - 2 * pad)
            y = h - pad - ((v - mn) / rng) * (h - 2 * pad)
            return QPointF(x, y)

        points = [pt(i, v) for i, v in enumerate(self._values)]

        # Gradient fill
        path = QPainterPath()
        path.moveTo(QPointF(points[0].x(), h))
        for p in points:
            path.lineTo(p)
        path.lineTo(QPointF(points[-1].x(), h))
        path.closeSubpath()
        positive = self._values[-1] >= 0
        base = QColor(_GREEN if positive else _RED)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(base.red(), base.green(), base.blue(), 80))
        grad.setColorAt(1, QColor(base.red(), base.green(), base.blue(), 0))
        painter.fillPath(path, QBrush(grad))

        # Line
        pen = QPen(QColor(_GREEN if positive else _RED), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPolyline(QPolygonF(points))

        # Endpoint dot
        painter.setBrush(QBrush(QColor(_GREEN if positive else _RED)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(points[-1], 4, 4)
        painter.end()


class _DonutChart(QWidget):
    """Asset-class allocation donut (no legend built-in)."""

    def __init__(self):
        super().__init__()
        self._slices = []
        self.setFixedSize(160, 160)

    def set_slices(self, slices):
        self._slices = slices
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h  = self.width(), self.height()
        pad   = 12
        rect  = QRectF(pad, pad, w - 2 * pad, h - 2 * pad)
        total = sum(v for _, v, _ in self._slices) or 1
        angle = 90 * 16
        for _, value, color in self._slices:
            span = int(value / total * 360 * 16)
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPie(rect, angle, span)
            angle -= span
        inner = (w - 2 * pad) * 0.35
        painter.setBrush(QBrush(QColor(_CARD)))
        painter.drawEllipse(QPointF(w / 2, h / 2), inner, inner)
        painter.end()


class _BarChart(QWidget):
    """Horizontal bar chart for top categories."""

    def __init__(self):
        super().__init__()
        self._bars = []
        self.setMinimumHeight(20)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def set_bars(self, bars):
        self._bars = bars
        bar_h = 26
        self.setFixedHeight(max(60, len(bars) * (bar_h + 6)))
        self.update()

    def paintEvent(self, _event):
        if not self._bars:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w       = self.width()
        bar_h   = 26
        gap     = 6
        label_w = 160
        max_v   = max(v for _, v, _ in self._bars) or 1

        for i, (label, value, color) in enumerate(self._bars):
            y = i * (bar_h + gap)
            painter.setPen(QPen(QColor(_TEXT)))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(0, y, label_w - 8, bar_h,
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                             label[:22])
            bx   = label_w
            bw   = w - label_w - 70
            track = QRectF(bx, y + 6, bw, bar_h - 12)
            painter.setBrush(QBrush(QColor(_BORDER)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(track, 4, 4)
            fill_w = bw * (value / max_v)
            if fill_w > 0:
                fill = QRectF(bx, y + 6, fill_w, bar_h - 12)
                col  = QColor(color)
                col.setAlpha(200)
                painter.setBrush(QBrush(col))
                painter.drawRoundedRect(fill, 4, 4)
            painter.setPen(QPen(QColor(_MUTED)))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.drawText(bx + bw + 4, y, 64, bar_h,
                             Qt.AlignmentFlag.AlignVCenter, f"${value:,.0f}")
        painter.end()


# ===========================================================================
#  Insight Chip
# ===========================================================================

class _InsightChip(QFrame):
    def __init__(self, label, value, color=_BLUE):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{ background: rgba(88,166,255,0.08);
                      border: 1px solid {color}55; border-radius: 20px; }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(6)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color:{_MUTED}; font-size:10px; background:transparent; border:none;")
        val = QLabel(value)
        val.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        val.setStyleSheet(f"color:{color}; background:transparent; border:none;")
        layout.addWidget(lbl)
        layout.addWidget(val)


# ===========================================================================
#  Category Row (used inside snapshot dialog)
# ===========================================================================

class _CategoryRow(QWidget):

    def __init__(self, name="", amount=0.0, suggestions=None):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        fs = ("background:#21262d; color:#e6edf3; "
              "border:1px solid #30363d; border-radius:6px; padding:6px 8px;")

        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("Category name")
        self.name_edit.setStyleSheet(f"QLineEdit{{{fs}}}")
        if suggestions:
            comp = QCompleter(suggestions, self.name_edit)
            comp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            comp.setFilterMode(Qt.MatchFlag.MatchContains)
            self.name_edit.setCompleter(comp)

        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setPrefix("$")
        self.amount_spin.setRange(0, 99_999_999)
        self.amount_spin.setDecimals(0)
        self.amount_spin.setValue(amount)
        self.amount_spin.setFixedWidth(150)
        self.amount_spin.setStyleSheet(f"QDoubleSpinBox{{{fs}}}")

        remove_btn = QPushButton("x")
        remove_btn.setFixedSize(28, 28)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setStyleSheet(
            "QPushButton{background:transparent;color:#f85149;border:none;"
            "font-size:12px;border-radius:4px;}"
            "QPushButton:hover{background:rgba(248,81,73,0.15);}")
        remove_btn.clicked.connect(self._remove_self)

        layout.addWidget(self.name_edit, 1)
        layout.addWidget(self.amount_spin)
        layout.addWidget(remove_btn)

    def _remove_self(self):
        if self.parent() and self.parent().layout():
            self.parent().layout().removeWidget(self)
        self.setParent(None)
        self.deleteLater()

    def get_data(self):
        return self.name_edit.text().strip(), self.amount_spin.value()


# ===========================================================================
#  Snapshot Dialog  (with live preview)
# ===========================================================================

class _SnapshotDialog(QDialog):

    def __init__(self, parent, existing_snapshot=None, existing_data=None,
                 prefill_data=None):
        super().__init__(parent)
        # Accept either ORM object (legacy) or plain dict
        if existing_data is None and existing_snapshot is not None:
            existing_data = {
                "id":          existing_snapshot.id,
                "date":        existing_snapshot.snapshot_date,
                "assets":      json.loads(existing_snapshot.assets_json or "{}"),
                "liabilities": json.loads(existing_snapshot.liabilities_json or "{}"),
                "notes":       existing_snapshot.notes or "",
            }
        self.existing  = existing_data
        # prefill_data: pre-populate values from a previous snapshot but keep
        # the dialog in "New" mode (today's date, no id, title = New Snapshot)
        self._prefill  = prefill_data
        self.setWindowTitle("Edit Snapshot" if existing_data else "New Net Worth Snapshot")
        self.setMinimumWidth(580)
        self.setMinimumHeight(560)
        self.setStyleSheet(
            "QDialog{background-color:#161b22;}"
            "QLabel{color:#c9d1d9;}")
        self._build()
        if existing_data:
            self._load(existing_data)
        elif prefill_data:
            self._load_prefill(prefill_data)
        self._update_preview()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 16)
        root.setSpacing(12)

        hdr = QLabel("Edit Snapshot" if self.existing else "New Net Worth Snapshot")
        hdr.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        hdr.setStyleSheet("color:#58a6ff;")
        root.addWidget(hdr)

        # Date row
        date_row = QHBoxLayout()
        date_lbl = QLabel("Snapshot Date:")
        date_lbl.setFixedWidth(120)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet(
            "QDateEdit{background:#21262d;color:#e6edf3;"
            "border:1px solid #30363d;border-radius:6px;padding:6px;}")
        date_row.addWidget(date_lbl)
        date_row.addWidget(self.date_edit)
        date_row.addStretch()
        root.addLayout(date_row)

        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        scroll.setMinimumHeight(300)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(10)

        # Assets
        inner_layout.addWidget(self._sep())
        ah = QHBoxLayout()
        at = QLabel("  Assets")
        at.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        at.setStyleSheet(f"color:{_GREEN};")
        ah.addWidget(at)
        ah.addStretch()
        add_a = QPushButton("+ Add Row")
        add_a.setStyleSheet(
            f"QPushButton{{background:transparent;color:{_GREEN};border:none;"
            "font-size:11px;font-weight:600;}}"
            f"QPushButton:hover{{color:#56d364;}}")
        add_a.setCursor(Qt.CursorShape.PointingHandCursor)
        add_a.clicked.connect(
            lambda: self._add_row(self.assets_layout, suggestions=ASSET_CATEGORIES))
        ah.addWidget(add_a)
        inner_layout.addLayout(ah)
        self.assets_layout = QVBoxLayout()
        self.assets_layout.setSpacing(6)
        inner_layout.addLayout(self.assets_layout)

        # Liabilities
        inner_layout.addWidget(self._sep())
        lh = QHBoxLayout()
        lt = QLabel("  Liabilities")
        lt.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lt.setStyleSheet(f"color:{_RED};")
        lh.addWidget(lt)
        lh.addStretch()
        add_l = QPushButton("+ Add Row")
        add_l.setStyleSheet(
            f"QPushButton{{background:transparent;color:{_RED};border:none;"
            "font-size:11px;font-weight:600;}}"
            f"QPushButton:hover{{color:#ff7b72;}}")
        add_l.setCursor(Qt.CursorShape.PointingHandCursor)
        add_l.clicked.connect(
            lambda: self._add_row(self.liab_layout, suggestions=LIABILITY_CATEGORIES))
        lh.addWidget(add_l)
        inner_layout.addLayout(lh)
        self.liab_layout = QVBoxLayout()
        self.liab_layout.setSpacing(6)
        inner_layout.addLayout(self.liab_layout)

        inner_layout.addStretch()
        scroll.setWidget(inner)
        root.addWidget(scroll)

        # Live preview
        root.addWidget(self._sep())
        prev_row = QHBoxLayout()
        prev_row.setSpacing(16)
        self._prev_assets_lbl = QLabel("Assets  $0")
        self._prev_assets_lbl.setStyleSheet(
            f"color:{_GREEN};font-size:11px;font-weight:600;")
        self._prev_liab_lbl = QLabel("Liabilities  $0")
        self._prev_liab_lbl.setStyleSheet(
            f"color:{_RED};font-size:11px;font-weight:600;")
        self._prev_nw_lbl = QLabel("Net Worth  $0")
        self._prev_nw_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._prev_nw_lbl.setStyleSheet(f"color:{_BLUE};")
        sep_lbl1 = QLabel("-")
        sep_lbl1.setStyleSheet(f"color:{_MUTED};")
        sep_lbl2 = QLabel("=")
        sep_lbl2.setStyleSheet(f"color:{_MUTED};")
        prev_row.addWidget(self._prev_assets_lbl)
        prev_row.addWidget(sep_lbl1)
        prev_row.addWidget(self._prev_liab_lbl)
        prev_row.addWidget(sep_lbl2)
        prev_row.addWidget(self._prev_nw_lbl)
        prev_row.addStretch()
        root.addLayout(prev_row)

        # Notes
        notes_row = QHBoxLayout()
        notes_lbl = QLabel("Notes:")
        notes_lbl.setFixedWidth(60)
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional context for this snapshot...")
        self.notes_edit.setStyleSheet(
            "QLineEdit{background:#21262d;color:#e6edf3;"
            "border:1px solid #30363d;border-radius:6px;padding:8px;}")
        notes_row.addWidget(notes_lbl)
        notes_row.addWidget(self.notes_edit, 1)
        root.addLayout(notes_row)

        # Buttons
        btns = QHBoxLayout()
        save_btn   = PremiumButton("Save Snapshot", style=PremiumButton.Style.PRIMARY, icon_name="save")
        cancel_btn = PremiumButton("Cancel",         style=PremiumButton.Style.FLAT,   icon_name="close")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        root.addLayout(btns)

        # Default rows for new snapshot (only when no prefill / existing data)
        if not self.existing and not self._prefill:
            for cat in ASSET_CATEGORIES[:4]:
                self._add_row(self.assets_layout, cat, suggestions=ASSET_CATEGORIES)
            for cat in LIABILITY_CATEGORIES[:3]:
                self._add_row(self.liab_layout, cat, suggestions=LIABILITY_CATEGORIES)

    @staticmethod
    def _sep():
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{_BORDER};")
        return sep

    def _add_row(self, layout, name="", amount=0.0, suggestions=None):
        row = _CategoryRow(name, amount, suggestions)
        row.amount_spin.valueChanged.connect(self._update_preview)
        layout.addWidget(row)
        self._update_preview()

    def _load(self, data):
        d = data["date"]
        self.date_edit.setDate(QDate(d.year, d.month, d.day))
        for name, amt in data["assets"].items():
            self._add_row(self.assets_layout, name, amt, ASSET_CATEGORIES)
        for name, amt in data["liabilities"].items():
            self._add_row(self.liab_layout, name, amt, LIABILITY_CATEGORIES)
        if data.get("notes"):
            self.notes_edit.setText(data["notes"])

    def _load_prefill(self, data):
        """Pre-populate from a previous snapshot but keep date as today."""
        for name, amt in data["assets"].items():
            self._add_row(self.assets_layout, name, amt, ASSET_CATEGORIES)
        for name, amt in data["liabilities"].items():
            self._add_row(self.liab_layout, name, amt, LIABILITY_CATEGORIES)
        # Leave notes blank — it's a new snapshot entry

    def _update_preview(self):
        a = sum(v for _, v in self._collect_rows(self.assets_layout).items())
        l = sum(v for _, v in self._collect_rows(self.liab_layout).items())
        nw = a - l
        self._prev_assets_lbl.setText(f"Assets  ${a:,.0f}")
        self._prev_liab_lbl.setText(f"Liabilities  ${l:,.0f}")
        color = _GREEN if nw >= 0 else _RED
        self._prev_nw_lbl.setText(f"Net Worth  ${nw:,.0f}")
        self._prev_nw_lbl.setStyleSheet(
            f"color:{color};font-size:12px;font-weight:700;")

    # Public API
    def get_assets(self):
        return self._collect_rows(self.assets_layout)

    def get_liabilities(self):
        return self._collect_rows(self.liab_layout)

    def get_snapshot_date(self):
        d = self.date_edit.date()
        return datetime(d.year(), d.month(), d.day())

    def get_notes(self):
        return self.notes_edit.text().strip() or None

    @staticmethod
    def _collect_rows(layout):
        result = {}
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and isinstance(item.widget(), _CategoryRow):
                name, amount = item.widget().get_data()
                if name and amount > 0:
                    result[name] = amount
        return result


# ===========================================================================
#  Main Widget
# ===========================================================================

class NetWorthWidget(QWidget):

    def __init__(self):
        super().__init__()
        self._insights = {}
        self._setup_ui()
        self.refresh_data()

    # -----------------------------------------------------------------------
    # UI construction
    # -----------------------------------------------------------------------

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea{{background:{_BG};border:none;}}")

        content = QWidget()
        main = QVBoxLayout(content)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Net Worth")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setObjectName("titleLabel")
        subtitle = QLabel("Wealth snapshot & financial analytics")
        subtitle.setStyleSheet(f"color:{_MUTED};font-size:12px;")
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        hdr.addLayout(title_col)
        hdr.addStretch()
        new_btn = PremiumButton("New Snapshot", style=PremiumButton.Style.PRIMARY, icon_name="add")
        new_btn.clicked.connect(self._show_new_dialog)
        refresh_btn = PremiumButton("Refresh", style=PremiumButton.Style.FLAT, icon_name="refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        hdr.addWidget(new_btn)
        hdr.addWidget(refresh_btn)
        main.addLayout(hdr)

        # KPI row 1
        row1 = QHBoxLayout()
        row1.setSpacing(12)
        self.card_assets = StatCard("Total Assets",      "$0", "🏦", _GREEN)
        self.card_liab   = StatCard("Total Liabilities", "$0", "💳", _RED)
        self.card_nw     = StatCard("Net Worth",          "$0", "📈", _BLUE)
        for c in (self.card_assets, self.card_liab, self.card_nw):
            row1.addWidget(c)
        main.addLayout(row1)

        # KPI row 2
        row2 = QHBoxLayout()
        row2.setSpacing(12)
        self.card_mom  = StatCard("MoM Change",    "$0", "📅", _YELLOW)
        self.card_yoy  = StatCard("YoY Change",    "$0", "📆", _PURPLE)
        self.card_d2a  = StatCard("Debt-to-Asset", "0%", "⚖️",  _ORANGE)
        self.card_fire = StatCard("FIRE Progress", "0%", "🔥", _GREEN)
        for c in (self.card_mom, self.card_yoy, self.card_d2a, self.card_fire):
            row2.addWidget(c)
        main.addLayout(row2)

        # Insight chips
        self._chips_container = QWidget()
        self._chips_row = QHBoxLayout(self._chips_container)
        self._chips_row.setSpacing(8)
        main.addWidget(self._chips_container)

        # Sparkline
        spark_row = QHBoxLayout()
        spark_title = QLabel("Net Worth Trend")
        spark_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        spark_title.setStyleSheet(f"color:{_BLUE};")
        spark_line = QFrame()
        spark_line.setFrameShape(QFrame.Shape.HLine)
        spark_line.setStyleSheet(f"color:{_BORDER};")
        spark_row.addWidget(spark_title)
        spark_row.addWidget(spark_line, 1)
        main.addLayout(spark_row)

        spark_card = QFrame()
        spark_card.setObjectName("card")
        spark_layout = QVBoxLayout(spark_card)
        spark_layout.setContentsMargins(16, 12, 16, 12)
        self.sparkline = _Sparkline()
        spark_layout.addWidget(self.sparkline)
        main.addWidget(spark_card)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background:{_CARD}; border:1px solid {_BORDER};
                border-radius:8px; margin-top:-1px;
            }}
            QTabBar::tab {{
                background:transparent; color:{_MUTED};
                padding:8px 18px; border:none;
                font-size:12px; font-weight:600;
            }}
            QTabBar::tab:selected {{color:{_BLUE};border-bottom:2px solid {_BLUE};}}
            QTabBar::tab:hover {{color:{_TEXT};}}
        """)

        # -- Tab 1: Breakdown --
        tab_breakdown = QWidget()
        bd_layout = QHBoxLayout(tab_breakdown)
        bd_layout.setContentsMargins(16, 16, 16, 16)
        bd_layout.setSpacing(16)

        self.assets_frame = QFrame()
        self.assets_frame.setObjectName("card")
        self.assets_v = QVBoxLayout(self.assets_frame)
        self.assets_v.setContentsMargins(16, 16, 16, 16)
        self.assets_v.setSpacing(6)
        ah_lbl = QLabel("  Assets")
        ah_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        ah_lbl.setStyleSheet(f"color:{_GREEN};")
        self.assets_v.addWidget(ah_lbl)
        bd_layout.addWidget(self.assets_frame, 1)

        self.liab_frame = QFrame()
        self.liab_frame.setObjectName("card")
        self.liab_v = QVBoxLayout(self.liab_frame)
        self.liab_v.setContentsMargins(16, 16, 16, 16)
        self.liab_v.setSpacing(6)
        lh_lbl = QLabel("  Liabilities")
        lh_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lh_lbl.setStyleSheet(f"color:{_RED};")
        self.liab_v.addWidget(lh_lbl)
        bd_layout.addWidget(self.liab_frame, 1)
        self.tabs.addTab(tab_breakdown, "Breakdown")

        # -- Tab 2: Analytics --
        tab_analytics = QWidget()
        an_layout = QHBoxLayout(tab_analytics)
        an_layout.setContentsMargins(16, 16, 16, 16)
        an_layout.setSpacing(24)

        donut_col = QVBoxLayout()
        donut_title = QLabel("Asset Allocation")
        donut_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        donut_title.setStyleSheet(f"color:{_TEXT};")
        donut_col.addWidget(donut_title)
        self.donut = _DonutChart()
        donut_col.addWidget(self.donut, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._donut_legend = QVBoxLayout()
        self._donut_legend.setSpacing(4)
        donut_col.addLayout(self._donut_legend)
        donut_col.addStretch()
        an_layout.addLayout(donut_col)

        bar_col = QVBoxLayout()
        bar_title = QLabel("Top Categories by Value")
        bar_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        bar_title.setStyleSheet(f"color:{_TEXT};")
        bar_col.addWidget(bar_title)
        self.bar_chart = _BarChart()
        bar_col.addWidget(self.bar_chart)
        bar_col.addStretch()
        an_layout.addLayout(bar_col, 1)
        self.tabs.addTab(tab_analytics, "Analytics")

        # -- Tab 3: History --
        tab_history = QWidget()
        hist_layout = QVBoxLayout(tab_history)
        hist_layout.setContentsMargins(0, 0, 0, 0)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(
            ["Date", "Assets", "Liabilities", "Net Worth", "Notes", "Actions"])
        self.history_table.setAlternatingRowColors(True)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setMinimumHeight(240)
        self.history_table.setStyleSheet(f"""
            QTableWidget {{
                background-color:{_CARD}; alternate-background-color:#21262d;
                gridline-color:{_BORDER}; border:none; border-radius:8px;
            }}
            QTableWidget::item {{ padding:8px; color:{_TEXT}; }}
            QHeaderView::section {{
                background:#1c2128; color:{_MUTED}; padding:10px 8px;
                border:none; border-bottom:2px solid {_BORDER};
                font-weight:700; font-size:11px;
            }}
        """)
        hh = self.history_table.horizontalHeader()
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        for col, cw in enumerate([120, 120, 120, 130, 0, 140]):
            if cw:
                self.history_table.setColumnWidth(col, cw)
        hist_layout.addWidget(self.history_table)
        self.tabs.addTab(tab_history, "History")

        # -- Tab 4: FIRE & Goals --
        tab_goals = QWidget()
        goals_layout = QVBoxLayout(tab_goals)
        goals_layout.setContentsMargins(20, 20, 20, 20)
        goals_layout.setSpacing(14)

        fire_title = QLabel("  FIRE Calculator")
        fire_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        fire_title.setStyleSheet(f"color:{_YELLOW};")
        goals_layout.addWidget(fire_title)

        fire_desc = QLabel(
            "FIRE = Financial Independence, Retire Early. "
            "Rule: you need 25x your annual expenses invested.\n"
            "Annual expense proxy: current total liabilities.")
        fire_desc.setWordWrap(True)
        fire_desc.setStyleSheet(f"color:{_MUTED};font-size:11px;")
        goals_layout.addWidget(fire_desc)

        self._fire_progress_bar = QProgressBar()
        self._fire_progress_bar.setRange(0, 100)
        self._fire_progress_bar.setValue(0)
        self._fire_progress_bar.setTextVisible(True)
        self._fire_progress_bar.setFixedHeight(24)
        self._fire_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background:{_BORDER}; border-radius:10px;
                color:white; font-weight:700; font-size:11px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {_YELLOW}, stop:1 {_GREEN});
                border-radius:10px;
            }}
        """)
        goals_layout.addWidget(self._fire_progress_bar)

        self._fire_stats_grid = QGridLayout()
        self._fire_stats_grid.setSpacing(12)
        goals_layout.addLayout(self._fire_stats_grid)

        sep_line = QFrame()
        sep_line.setFixedHeight(1)
        sep_line.setStyleSheet(f"background:{_BORDER};")
        goals_layout.addWidget(sep_line)

        goal_title = QLabel("  Custom Wealth Goal")
        goal_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        goal_title.setStyleSheet(f"color:{_BLUE};")
        goals_layout.addWidget(goal_title)

        tgt_row = QHBoxLayout()
        tgt_lbl = QLabel("Target Net Worth:")
        tgt_lbl.setFixedWidth(160)
        fs = ("background:#21262d;color:#e6edf3;"
              "border:1px solid #30363d;border-radius:6px;padding:6px 8px;")
        self._goal_spin = QDoubleSpinBox()
        self._goal_spin.setPrefix("$")
        self._goal_spin.setRange(0, 99_999_999)
        self._goal_spin.setDecimals(0)
        self._goal_spin.setValue(1_000_000)
        self._goal_spin.setFixedWidth(160)
        self._goal_spin.setStyleSheet(f"QDoubleSpinBox{{{fs}}}")
        calc_btn = PremiumButton("Calculate", style=PremiumButton.Style.FLAT, icon_name="refresh")
        calc_btn.clicked.connect(self._update_goal_display)
        tgt_row.addWidget(tgt_lbl)
        tgt_row.addWidget(self._goal_spin)
        tgt_row.addWidget(calc_btn)
        tgt_row.addStretch()
        goals_layout.addLayout(tgt_row)

        self._goal_result_lbl = QLabel("")
        self._goal_result_lbl.setWordWrap(True)
        self._goal_result_lbl.setStyleSheet(f"color:{_TEXT};font-size:12px;")
        goals_layout.addWidget(self._goal_result_lbl)
        goals_layout.addStretch()

        self.tabs.addTab(tab_goals, "FIRE & Goals")
        main.addWidget(self.tabs)

        # ── AI Net Worth Insights ─────────────────────────────────────────
        main.addWidget(self._sep())
        self.nw_ai_panel = AIInsightsPanel()
        main.addWidget(self.nw_ai_panel)

        main.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _sep():
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{_BORDER};")
        return sep

    @staticmethod
    def _clear_layout_children(layout, keep_first=0):
        while layout.count() > keep_first:
            item = layout.takeAt(keep_first)
            if item.widget():
                item.widget().deleteLater()

    # -----------------------------------------------------------------------
    # Data refresh
    # -----------------------------------------------------------------------

    def refresh_data(self):
        session = get_session()
        try:
            snapshots = NetWorthManager.get_snapshots_serialized(session)
            # ── AI insights ───────────────────────────────────────────
            try:
                nw_insights = NexusAI.analyse_net_worth(session)
                self.nw_ai_panel.set_insights(nw_insights)
            except Exception:
                pass
        finally:
            session.close()

        self._insights = NetWorthManager.compute_insights(snapshots)
        ins = self._insights
        latest = ins.get("latest")
        snaps_newest_first = list(reversed(snapshots))

        self._refresh_kpi_cards(ins)
        self._refresh_insight_chips(ins)
        self._refresh_sparkline(snapshots)
        self._refresh_breakdown(latest)
        self._refresh_analytics(latest)
        self._refresh_history_table(snaps_newest_first)
        self._refresh_fire_tab(ins)

    def _refresh_kpi_cards(self, ins):
        latest = ins.get("latest")
        if not latest:
            for c in (self.card_assets, self.card_liab, self.card_nw,
                      self.card_mom, self.card_yoy, self.card_d2a, self.card_fire):
                c.set_value("—")
            return

        a  = latest["total_assets"]
        l  = latest["total_liab"]
        nw = latest["net_worth"]
        self.card_assets.set_value(f"${a:,.0f}")
        self.card_liab.set_value(f"${l:,.0f}")
        self.card_nw.set_value(f"${nw:,.0f}")
        self.card_nw.set_color(_GREEN if nw >= 0 else _RED)

        mom = ins.get("mom_change", 0)
        sign = "+" if mom >= 0 else ""
        self.card_mom.set_value(f"{sign}${abs(mom):,.0f}")
        self.card_mom.set_color(_GREEN if mom >= 0 else _RED)

        yoy = ins.get("yoy_change", 0)
        self.card_yoy.set_value(f"{'+'if yoy>=0 else ''}${abs(yoy):,.0f}")
        self.card_yoy.set_color(_GREEN if yoy >= 0 else _RED)

        d2a = ins.get("d2a_ratio", 0)
        self.card_d2a.set_value(f"{d2a:.1f}%")
        self.card_d2a.set_color(
            _GREEN if d2a < 40 else (_YELLOW if d2a < 70 else _RED))

        fire_no  = ins.get("fire_number", 0)
        fire_pct = min((nw / fire_no * 100) if fire_no > 0 else 0, 100)
        self.card_fire.set_value(f"{max(fire_pct,0):.1f}%")
        self.card_fire.set_color(
            _GREEN if fire_pct >= 100 else (_YELLOW if fire_pct >= 50 else _BLUE))

    def _refresh_insight_chips(self, ins):
        self._clear_layout_children(self._chips_row)
        if not ins:
            return

        mom_pct  = ins.get("mom_pct", 0)
        yoy_pct  = ins.get("yoy_pct", 0)
        best     = ins.get("best_gain", 0)
        worst    = ins.get("worst_loss", 0)
        count    = ins.get("snapshot_count", 0)
        mtf      = ins.get("months_to_fire")

        chips = [
            ("MoM",          f"{'+'if mom_pct>=0 else ''}{mom_pct:.1f}%",
             _GREEN if mom_pct >= 0 else _RED),
            ("YoY",          f"{'+'if yoy_pct>=0 else ''}{yoy_pct:.1f}%",
             _GREEN if yoy_pct >= 0 else _RED),
            ("Best month",   f"+${best:,.0f}", _GREEN),
            ("Worst month",  f"${worst:,.0f}", _RED),
            ("Snapshots",    str(count),       _BLUE),
        ]
        if mtf is not None and mtf > 0:
            chips.append(("FIRE ETA", f"{mtf/12:.1f} yrs", _YELLOW))
        elif mtf is not None and mtf <= 0:
            chips.append(("FIRE ETA", "Achieved!", _GREEN))

        for label, value, color in chips:
            self._chips_row.addWidget(_InsightChip(label, value, color))
        self._chips_row.addStretch()

    def _refresh_sparkline(self, snapshots):
        self.sparkline.set_values([s["net_worth"] for s in snapshots])

    def _refresh_breakdown(self, latest):
        def clear_rows(layout):
            while layout.count() > 1:
                item = layout.takeAt(1)
                if item.widget():
                    item.widget().deleteLater()

        clear_rows(self.assets_v)
        clear_rows(self.liab_v)

        if not latest:
            for layout in (self.assets_v, self.liab_v):
                empty = QLabel("No data yet.")
                empty.setStyleSheet(f"color:#4b5563;font-size:12px;")
                layout.addWidget(empty)
            return

        def add_rows(layout, data, color):
            total = sum(data.values()) or 1
            for name, amount in sorted(data.items(), key=lambda x: -x[1]):
                row_w = QWidget()
                row_l = QVBoxLayout(row_w)
                row_l.setContentsMargins(0, 2, 0, 2)
                row_l.setSpacing(3)
                top = QHBoxLayout()
                n = QLabel(name)
                n.setFont(QFont("Segoe UI", 10))
                n.setStyleSheet(f"color:{_TEXT};")
                pct_lbl = QLabel(f"{amount/total*100:.1f}%")
                pct_lbl.setStyleSheet(f"color:{_MUTED};font-size:9px;")
                a = QLabel(f"${amount:,.0f}")
                a.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                a.setStyleSheet(f"color:{color};")
                a.setAlignment(Qt.AlignmentFlag.AlignRight)
                top.addWidget(n, 1)
                top.addWidget(pct_lbl)
                top.addSpacing(8)
                top.addWidget(a)
                row_l.addLayout(top)
                pbar = QProgressBar()
                pbar.setRange(0, 1000)
                pbar.setValue(int(amount / total * 1000))
                pbar.setTextVisible(False)
                pbar.setFixedHeight(3)
                pbar.setStyleSheet(f"""
                    QProgressBar{{background:{_BORDER};border-radius:1px;border:none;}}
                    QProgressBar::chunk{{background:{color};border-radius:1px;}}
                """)
                row_l.addWidget(pbar)
                layout.addWidget(row_w)
            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background:{_BORDER};")
            layout.addWidget(sep)
            total_row = QHBoxLayout()
            tl = QLabel("Total")
            tl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            tl.setStyleSheet(f"color:{_TEXT};")
            tv = QLabel(f"${sum(data.values()):,.0f}")
            tv.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            tv.setStyleSheet(f"color:{color};")
            tv.setAlignment(Qt.AlignmentFlag.AlignRight)
            total_row.addWidget(tl, 1)
            total_row.addWidget(tv)
            tw = QWidget()
            tw.setLayout(total_row)
            layout.addWidget(tw)

        add_rows(self.assets_v, latest["assets"],      _GREEN)
        add_rows(self.liab_v,   latest["liabilities"], _RED)

    def _refresh_analytics(self, latest):
        self._clear_layout_children(self._donut_legend)

        if not latest or not latest["assets"]:
            self.donut.set_slices([])
            self.bar_chart.set_bars([])
            return

        slices = [
            (name, val, CATEGORY_COLORS[i % len(CATEGORY_COLORS)])
            for i, (name, val) in enumerate(
                sorted(latest["assets"].items(), key=lambda x: -x[1])[:8])
        ]
        self.donut.set_slices(slices)

        for name, val, color in slices:
            row = QHBoxLayout()
            dot = QLabel("*")
            dot.setStyleSheet(f"color:{color};font-size:10px;")
            dot.setFixedWidth(14)
            lbl = QLabel(name[:20])
            lbl.setStyleSheet(f"color:{_TEXT};font-size:10px;")
            row.addWidget(dot)
            row.addWidget(lbl, 1)
            lw = QWidget()
            lw.setLayout(row)
            self._donut_legend.addWidget(lw)

        all_items = (
            list(latest["assets"].items()) +
            [(f"[L] {k}", v) for k, v in latest["liabilities"].items()]
        )
        all_items.sort(key=lambda x: -x[1])
        bars = [
            (name, val,
             _RED if name.startswith("[L]") else CATEGORY_COLORS[i % len(CATEGORY_COLORS)])
            for i, (name, val) in enumerate(all_items[:8])
        ]
        self.bar_chart.set_bars(bars)

    def _refresh_history_table(self, snapshots):
        self.history_table.setRowCount(len(snapshots))
        for row, snap in enumerate(snapshots):
            nw = snap["net_worth"]
            self.history_table.setItem(
                row, 0, QTableWidgetItem(snap["date"].strftime("%Y-%m-%d")))
            ai = QTableWidgetItem(f"${snap['total_assets']:,.0f}")
            ai.setForeground(QColor(_GREEN))
            self.history_table.setItem(row, 1, ai)
            li = QTableWidgetItem(f"${snap['total_liab']:,.0f}")
            li.setForeground(QColor(_RED))
            self.history_table.setItem(row, 2, li)
            ni = QTableWidgetItem(f"${nw:,.0f}")
            ni.setForeground(QColor(_GREEN if nw >= 0 else _RED))
            self.history_table.setItem(row, 3, ni)
            self.history_table.setItem(row, 4, QTableWidgetItem(snap["notes"]))
            aw = QWidget()
            al = QHBoxLayout(aw)
            al.setContentsMargins(4, 2, 4, 2)
            al.setSpacing(4)
            eb = PremiumButton("Edit",   style=PremiumButton.Style.EDIT,         icon_name="edit")
            db = PremiumButton("Delete", style=PremiumButton.Style.GHOST_DANGER, icon_name="delete")
            eb.setFixedHeight(30)
            db.setFixedHeight(30)
            eb.clicked.connect(
                lambda _c, sid=snap["id"]: self._show_edit_dialog_by_id(sid))
            db.clicked.connect(
                lambda _c, sid=snap["id"]: self._delete_snapshot(sid))
            al.addWidget(eb)
            al.addWidget(db)
            self.history_table.setCellWidget(row, 5, aw)
            self.history_table.setRowHeight(row, 44)

    def _refresh_fire_tab(self, ins):
        while self._fire_stats_grid.count():
            item = self._fire_stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not ins:
            return

        latest   = ins.get("latest") or {}
        fire_no  = ins.get("fire_number", 0)
        nw       = latest.get("net_worth", 0)
        fire_pct = min(max((nw / fire_no * 100) if fire_no > 0 else 0, 0), 100)
        self._fire_progress_bar.setValue(int(fire_pct))
        self._fire_progress_bar.setFormat(f"{fire_pct:.1f}% toward FIRE")

        mtf = ins.get("months_to_fire")
        avg = ins.get("avg_monthly_growth", 0)

        stats = [
            ("FIRE Number (25x expenses)", f"${fire_no:,.0f}"),
            ("Current Net Worth",          f"${nw:,.0f}"),
            ("Remaining to FIRE",          f"${max(fire_no - nw, 0):,.0f}"),
            ("Avg Monthly Growth",
             f"${avg:,.0f}" if avg else "Insufficient data"),
        ]
        if mtf is not None and mtf > 0:
            stats.append(("FIRE ETA",
                           f"{mtf/12:.1f} years ({int(mtf)} months)"))
        elif mtf is not None and mtf <= 0:
            stats.append(("FIRE Status", "Achieved!"))
        else:
            stats.append(("FIRE ETA", "Add more snapshots to project"))

        for i, (label, value) in enumerate(stats):
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color:{_MUTED};font-size:11px;")
            val = QLabel(value)
            val.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            val.setStyleSheet(f"color:{_TEXT};")
            self._fire_stats_grid.addWidget(lbl, i, 0)
            self._fire_stats_grid.addWidget(val, i, 1)

        self._update_goal_display()

    def _update_goal_display(self):
        ins = self._insights
        if not ins:
            self._goal_result_lbl.setText("Add snapshots to use this calculator.")
            return
        target    = self._goal_spin.value()
        nw        = (ins.get("latest") or {}).get("net_worth", 0)
        avg       = ins.get("avg_monthly_growth", 0)
        remaining = target - nw
        if remaining <= 0:
            self._goal_result_lbl.setText(
                f"You have already reached your goal of ${target:,.0f}!")
            return
        if avg > 0:
            months = remaining / avg
            self._goal_result_lbl.setText(
                f"At your average monthly growth of ${avg:,.0f},\n"
                f"you will reach ${target:,.0f} in approximately "
                f"{months/12:.1f} years ({int(months)} months).\n"
                f"Still needed: ${remaining:,.0f}")
        else:
            self._goal_result_lbl.setText(
                f"Still needed: ${remaining:,.0f} — "
                "add more snapshots to generate a projection.")

    # -----------------------------------------------------------------------
    # Actions
    # -----------------------------------------------------------------------

    def _show_new_dialog(self):
        # Pre-fill with latest snapshot values so the user only needs to
        # update changed figures instead of re-entering everything.
        prefill = None
        if self._insights and self._insights.get("latest"):
            prefill = self._insights["latest"]
        dialog = _SnapshotDialog(self, prefill_data=prefill)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            assets = dialog.get_assets()
            liab   = dialog.get_liabilities()
            if not assets and not liab:
                QMessageBox.warning(self, "Empty Snapshot",
                    "Please add at least one asset or liability row.")
                return
            session = get_session()
            try:
                NetWorthManager.create_snapshot(
                    session, assets, liab,
                    notes=dialog.get_notes(),
                    snapshot_date=dialog.get_snapshot_date())
            finally:
                session.close()
            self.refresh_data()

    def _show_edit_dialog_by_id(self, snapshot_id):
        session = get_session()
        try:
            from src.database.models import NetWorthSnapshot as NWS
            snap = session.query(NWS).filter_by(id=snapshot_id).first()
            if not snap:
                return
            existing = {
                "id":          snap.id,
                "date":        snap.snapshot_date,
                "assets":      json.loads(snap.assets_json or "{}"),
                "liabilities": json.loads(snap.liabilities_json or "{}"),
                "notes":       snap.notes or "",
            }
        finally:
            session.close()

        dialog = _SnapshotDialog(self, existing_data=existing)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            session2 = get_session()
            try:
                NetWorthManager.update_snapshot(
                    session2, snapshot_id,
                    assets=dialog.get_assets(),
                    liabilities=dialog.get_liabilities(),
                    notes=dialog.get_notes(),
                    snapshot_date=dialog.get_snapshot_date())
            finally:
                session2.close()
            self.refresh_data()

    def _delete_snapshot(self, snapshot_id):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Delete this net worth snapshot permanently?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
                NetWorthManager.delete_snapshot(session, snapshot_id)
            finally:
                session.close()
            self.refresh_data()
