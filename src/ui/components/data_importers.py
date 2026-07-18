"""
Smart data importers — auto-collect information from external sources.

Supported:
  - Browser password CSV (Chrome, Firefox, Bitwarden, LastPass, 1Password) → Connected Apps
  - ICS / iCal calendar files → Activities
  - Bank statement CSV (auto-column detection) → Budget entries
  - Bulk folder scan → Document Vault (auto-categorize by filename/extension)
  - Activity quick-templates (pre-built common recurring tasks)
"""
import csv
import io
import json
import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QMessageBox, QComboBox, QTableWidget, QTableWidgetItem, QCheckBox,
    QHeaderView, QFrame, QProgressBar, QScrollArea, QWidget, QGridLayout,
    QLineEdit, QTextEdit,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QCursor, QColor

from src.ui.components.premium_button import PremiumButton


# ═══════════════════════════════════════════════════════════════════════════════
#  1.  BROWSER PASSWORD IMPORT  →  Connected Apps
# ═══════════════════════════════════════════════════════════════════════════════

# Column mapping for common password manager CSV exports
_BROWSER_PROFILES = {
    "Chrome / Edge": {
        "name": ["name"], "url": ["url"], "username": ["username"], "password": ["password"],
    },
    "Firefox": {
        "name": ["url", "hostname"], "url": ["url", "hostname"], "username": ["username"],
        "password": ["password"],
    },
    "Bitwarden": {
        "name": ["name"], "url": ["login_uri", "uri"], "username": ["login_username", "username"],
        "password": ["login_password", "password"], "notes": ["notes"],
    },
    "LastPass": {
        "name": ["name"], "url": ["url"], "username": ["username"],
        "password": ["password"], "notes": ["extra", "notes"],
    },
    "1Password": {
        "name": ["title"], "url": ["url", "urls"], "username": ["username"],
        "password": ["password"], "notes": ["notes", "notesplain"],
    },
    "Auto-detect": {},  # will try to guess
}

_CATEGORY_KEYWORDS = {
    "banking": ["bank", "chase", "wells fargo", "citi", "boa", "capital one", "hsbc", "barclays"],
    "credit_card": ["credit", "visa", "mastercard", "amex", "discover"],
    "mortgage": ["mortgage", "home loan", "loan", "housing"],
    "investment": ["invest", "fidelity", "vanguard", "schwab", "robinhood", "etrade", "trading"],
    "insurance": ["insurance", "geico", "allstate", "progressive", "state farm"],
    "medical": ["medical", "health", "doctor", "hospital", "pharmacy", "cvs", "walgreens"],
    "utilities": ["electric", "gas", "water", "power", "utility", "comcast", "spectrum", "att", "verizon", "t-mobile"],
    "subscription": ["netflix", "spotify", "hulu", "disney", "amazon", "apple", "google", "youtube", "hbo",
                      "adobe", "microsoft", "dropbox", "slack", "zoom", "github"],
}


def _guess_category(name: str, url: str) -> str:
    """Guess connected app category from name / URL."""
    combined = f"{name} {url}".lower()
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return cat
    return "other"


def _guess_emoji(category: str) -> str:
    return {
        "banking": "🏦", "credit_card": "💳", "mortgage": "🏠",
        "investment": "📈", "insurance": "🛡️", "medical": "🏥",
        "utilities": "⚡", "subscription": "📱", "other": "📋",
    }.get(category, "📋")


def _auto_detect_columns(headers: list[str]) -> dict:
    """Try to map CSV headers to our fields automatically."""
    mapping = {}
    lower_headers = {h.lower().strip(): h for h in headers}
    # name
    for candidate in ["name", "title", "hostname", "site"]:
        if candidate in lower_headers:
            mapping["name"] = lower_headers[candidate]
            break
    # url
    for candidate in ["url", "login_uri", "website", "hostname", "uri"]:
        if candidate in lower_headers:
            mapping["url"] = lower_headers[candidate]
            break
    # username
    for candidate in ["username", "login_username", "user", "email", "login"]:
        if candidate in lower_headers:
            mapping["username"] = lower_headers[candidate]
            break
    # password
    for candidate in ["password", "login_password", "pass"]:
        if candidate in lower_headers:
            mapping["password"] = lower_headers[candidate]
            break
    # notes
    for candidate in ["notes", "extra", "note", "comment", "notesplain"]:
        if candidate in lower_headers:
            mapping["notes"] = lower_headers[candidate]
            break
    return mapping


def _match_profile_columns(profile: dict, lower_to_actual: dict) -> dict:
    """Case-insensitive column matching for a browser profile.

    Each profile value is a list of candidate column names. We iterate
    through candidates for each field and pick the first one that exists
    (case-insensitively) in the CSV headers.
    """
    col_map = {}
    for our_field, candidates in profile.items():
        for candidate in candidates:
            actual = lower_to_actual.get(candidate.lower().strip())
            if actual:
                col_map[our_field] = actual
                break
    return col_map


class BrowserPasswordImportDialog(QDialog):
    """Import passwords from browser/manager CSV export."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Passwords from Browser / Manager")
        self.setMinimumSize(700, 520)
        self.setModal(True)
        self._rows = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setStyleSheet("""
            QDialog { background-color: #0d1117; color: #e6eef8; }
            QLabel { color: #c7d2e0; }
            QTableWidget { background-color: #161b22; color: #e6eef8; border: 1px solid #30363d; border-radius: 6px; }
            QHeaderView::section { background: #1c2128; color: #8b949e; padding: 6px; border: none;
                                   border-bottom: 1px solid #30363d; font-weight: bold; }
        """)

        info = QLabel(
            "Export your passwords as CSV from Chrome (chrome://settings/passwords → Export),\n"
            "Firefox, Bitwarden, LastPass, or 1Password. Then select the file below."
        )
        info.setWordWrap(True)
        info.setFont(QFont("Segoe UI", 10))
        layout.addWidget(info)

        # Source selector + file picker
        row = QHBoxLayout()
        row.addWidget(QLabel("Source:"))
        self.source_combo = QComboBox()
        self.source_combo.addItems(list(_BROWSER_PROFILES.keys()))
        self.source_combo.setFixedWidth(180)
        row.addWidget(self.source_combo)

        browse_btn = PremiumButton("Browse CSV…", style=PremiumButton.Style.PRIMARY, icon_name="upload")
        browse_btn.clicked.connect(self._browse_csv)
        row.addWidget(browse_btn)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #8b949e;")
        row.addWidget(self.file_label, 1)
        layout.addLayout(row)

        # Preview table
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(5)
        self.preview_table.setHorizontalHeaderLabels(["Import", "Name / Site", "URL", "Username", "Category (auto)"])
        self.preview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setAlternatingRowColors(True)
        layout.addWidget(self.preview_table, 1)

        self.count_label = QLabel("0 entries found")
        self.count_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        layout.addWidget(self.count_label)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = PremiumButton("Cancel", style=PremiumButton.Style.FLAT)
        cancel_btn.clicked.connect(self.reject)
        import_btn = PremiumButton("Import Selected", style=PremiumButton.Style.SUCCESS, icon_name="download")
        import_btn.clicked.connect(self._do_import)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(import_btn)
        layout.addLayout(btn_row)

    def _browse_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if not path:
            return
        self.file_label.setText(Path(path).name)
        self._parse_csv(path)

    def _parse_csv(self, path: str):
        try:
            # Try to detect encoding
            raw_bytes = open(path, "rb").read(4096)
            enc = "utf-8-sig"
            if b"\xff\xfe" in raw_bytes[:4] or b"\x00" in raw_bytes[:100]:
                enc = "utf-16"

            with open(path, "r", encoding=enc, errors="replace") as f:
                content = f.read()

            # Handle potential delimiter issues
            sniffer_sample = content[:2048]
            try:
                dialect = csv.Sniffer().sniff(sniffer_sample, delimiters=",;\t|")
            except csv.Error:
                dialect = None

            reader = csv.DictReader(io.StringIO(content), dialect=dialect) if dialect else csv.DictReader(io.StringIO(content))
            headers = reader.fieldnames or []
            # Build case-insensitive header lookup: lowercase → actual header
            lower_to_actual = {h.lower().strip(): h for h in headers}

            source = self.source_combo.currentText()
            if source == "Auto-detect":
                col_map = _auto_detect_columns(headers)
            else:
                profile = _BROWSER_PROFILES[source]
                col_map = _match_profile_columns(profile, lower_to_actual)

            self._rows = []
            for raw in reader:
                name = raw.get(col_map.get("name", ""), "") or ""
                url = raw.get(col_map.get("url", ""), "") or ""
                username = raw.get(col_map.get("username", ""), "") or ""
                password = raw.get(col_map.get("password", ""), "") or ""
                notes = raw.get(col_map.get("notes", ""), "") or ""
                name, url, username, password, notes = (
                    name.strip(), url.strip(), username.strip(),
                    password.strip(), notes.strip(),
                )
                if not name and url:
                    # Extract domain as name
                    name = re.sub(r"https?://(?:www\.)?", "", url).split("/")[0]
                if not username and not url:
                    continue
                category = _guess_category(name, url)
                self._rows.append({
                    "name": name, "url": url, "username": username,
                    "password": password, "notes": notes, "category": category,
                })

            self._populate_preview()
            if not self._rows and headers:
                QMessageBox.warning(
                    self, "No Data Found",
                    f"CSV was read but no entries matched.\n"
                    f"Headers found: {', '.join(headers)}\n\n"
                    f"Try selecting a different Source or use Auto-detect."
                )
        except Exception as e:
            QMessageBox.critical(self, "Parse Error", f"Failed to read CSV:\n{e}")

    def _populate_preview(self):
        self.preview_table.setRowCount(len(self._rows))
        for i, r in enumerate(self._rows):
            cb = QCheckBox()
            cb.setChecked(True)
            self.preview_table.setCellWidget(i, 0, cb)
            self.preview_table.setItem(i, 1, QTableWidgetItem(r["name"]))
            self.preview_table.setItem(i, 2, QTableWidgetItem(r["url"]))
            self.preview_table.setItem(i, 3, QTableWidgetItem(r["username"]))
            self.preview_table.setItem(i, 4, QTableWidgetItem(r["category"].replace("_", " ").title()))
        self.count_label.setText(f"{len(self._rows)} entries found")

    def _do_import(self):
        from src.database.config import get_session
        from src.database.operations import ConnectedApplicationManager
        session = get_session()
        imported = 0
        try:
            for i, r in enumerate(self._rows):
                cb = self.preview_table.cellWidget(i, 0)
                if not cb or not cb.isChecked():
                    continue
                # Encrypt password if possible
                encrypted_pwd = None
                if r["password"]:
                    try:
                        from src.core.encryption import get_encryption_manager
                        em = get_encryption_manager()
                        encrypted_pwd = em.encrypt(r["password"]) if em else r["password"]
                    except Exception:
                        encrypted_pwd = r["password"]

                ConnectedApplicationManager.create_connected_app(
                    session,
                    name=r["name"] or r["url"],
                    app_name=r["name"],
                    app_type=r["category"],
                    category=r["category"],
                    website_url=r["url"] or None,
                    login_url=r["url"] or None,
                    username=r["username"],
                    password_encrypted=encrypted_pwd,
                    icon_emoji=_guess_emoji(r["category"]),
                    notes=r["notes"] or None,
                )
                imported += 1
        finally:
            session.close()

        QMessageBox.information(self, "Import Complete", f"Successfully imported {imported} connected apps.")
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
#  2.  ICS / iCAL IMPORT  →  Activities
# ═══════════════════════════════════════════════════════════════════════════════

def _parse_ics_events(path: str) -> list[dict]:
    """Minimal VEVENT parser — no external dependency required."""
    events = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    blocks = re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", text, re.DOTALL)
    for block in blocks:
        ev: dict = {}
        for line in block.strip().splitlines():
            line = line.strip()
            if line.startswith("SUMMARY"):
                ev["title"] = line.split(":", 1)[-1].strip()
            elif line.startswith("DESCRIPTION"):
                ev["description"] = line.split(":", 1)[-1].strip().replace("\\n", "\n")
            elif line.startswith("DTSTART"):
                ev["start"] = _parse_ics_dt(line.split(":", 1)[-1].strip())
            elif line.startswith("DTEND"):
                ev["end"] = _parse_ics_dt(line.split(":", 1)[-1].strip())
            elif line.startswith("RRULE"):
                ev["rrule"] = line.split(":", 1)[-1].strip()
        if "title" in ev and "start" in ev:
            events.append(ev)
    return events


def _parse_ics_dt(val: str) -> datetime:
    """Parse ICS date / datetime string."""
    val = val.replace("Z", "")
    for fmt in ("%Y%m%dT%H%M%S", "%Y%m%d"):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return datetime.now()


def _rrule_to_recurrence(rrule: str):
    """Map RRULE FREQ to our RecurrenceType."""
    from src.database.models import RecurrenceType
    freq_map = {
        "DAILY": RecurrenceType.DAILY,
        "WEEKLY": RecurrenceType.WEEKLY,
        "MONTHLY": RecurrenceType.MONTHLY,
        "YEARLY": RecurrenceType.YEARLY,
    }
    for key, val in freq_map.items():
        if key in rrule.upper():
            return val
    return RecurrenceType.ONCE


class CalendarImportDialog(QDialog):
    """Import events from .ics / .ical files → Activities."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Calendar Events (.ics)")
        self.setMinimumSize(660, 460)
        self.setModal(True)
        self._events = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setStyleSheet("""
            QDialog { background-color: #0d1117; color: #e6eef8; }
            QLabel { color: #c7d2e0; }
            QTableWidget { background-color: #161b22; color: #e6eef8; border: 1px solid #30363d; border-radius: 6px; }
            QHeaderView::section { background: #1c2128; color: #8b949e; padding: 6px; border: none;
                                   border-bottom: 1px solid #30363d; font-weight: bold; }
        """)

        info = QLabel(
            "Import events from Google Calendar, Outlook, or Apple Calendar.\n"
            "Export your calendar as .ics file first, then select it here."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        browse_btn = PremiumButton("Browse .ics File…", style=PremiumButton.Style.PRIMARY, icon_name="upload")
        browse_btn.clicked.connect(self._browse)
        layout.addWidget(browse_btn)

        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(5)
        self.preview_table.setHorizontalHeaderLabels(["Import", "Event Title", "Start Date", "Recurrence", "Description"])
        self.preview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setAlternatingRowColors(True)
        layout.addWidget(self.preview_table, 1)

        self.count_label = QLabel("0 events found")
        self.count_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        layout.addWidget(self.count_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = PremiumButton("Cancel", style=PremiumButton.Style.FLAT)
        cancel_btn.clicked.connect(self.reject)
        import_btn = PremiumButton("Import Selected", style=PremiumButton.Style.SUCCESS, icon_name="download")
        import_btn.clicked.connect(self._do_import)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(import_btn)
        layout.addLayout(btn_row)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select ICS File", "", "Calendar Files (*.ics *.ical)")
        if not path:
            return
        self._events = _parse_ics_events(path)
        self._populate()

    def _populate(self):
        self.preview_table.setRowCount(len(self._events))
        for i, ev in enumerate(self._events):
            cb = QCheckBox()
            cb.setChecked(True)
            self.preview_table.setCellWidget(i, 0, cb)
            self.preview_table.setItem(i, 1, QTableWidgetItem(ev.get("title", "")))
            self.preview_table.setItem(i, 2, QTableWidgetItem(
                ev["start"].strftime("%Y-%m-%d %H:%M") if "start" in ev else ""))
            rrule = ev.get("rrule", "")
            recurrence = _rrule_to_recurrence(rrule).value if rrule else "once"
            self.preview_table.setItem(i, 3, QTableWidgetItem(recurrence.title()))
            self.preview_table.setItem(i, 4, QTableWidgetItem(ev.get("description", "")[:80]))
        self.count_label.setText(f"{len(self._events)} events found")

    def _do_import(self):
        from src.database.config import get_session
        from src.database.operations import ActivityManager
        from src.database.models import RecurrenceType, CategoryType
        session = get_session()
        imported = 0
        try:
            for i, ev in enumerate(self._events):
                cb = self.preview_table.cellWidget(i, 0)
                if not cb or not cb.isChecked():
                    continue
                rrule = ev.get("rrule", "")
                rec_type = _rrule_to_recurrence(rrule) if rrule else RecurrenceType.ONCE
                start = ev.get("start", datetime.now())
                ActivityManager.create_activity(
                    session,
                    title=ev.get("title", "Imported Event"),
                    description=ev.get("description", ""),
                    category=CategoryType.TASK,
                    recurrence_type=rec_type,
                    start_date=start,
                    next_due_date=start,
                    reminder_days_before=1,
                )
                imported += 1
        finally:
            session.close()
        QMessageBox.information(self, "Import Complete", f"Imported {imported} activities from calendar.")
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
#  3.  BANK STATEMENT CSV IMPORT  →  Budget  (AI-powered column detection)
# ═══════════════════════════════════════════════════════════════════════════════

# ── Amount parser ───────────────────────────────────────────────────────────

def _parse_amount(raw: str) -> Optional[float]:
    """Parse a monetary string into a float, handling many world formats.

    Handles: $1,234.56  (1234.56)  -1234.56  1.234,56  Rs.1,234  ₹1234  CR/DR suffix
    Returns None if unparseable.
    """
    if not raw or not raw.strip():
        return None
    s = raw.strip()
    # Detect if parentheses indicate negative  e.g. (1234.56)
    negative = "(" in s and ")" in s
    # Check for DR suffix (negative) or CR suffix (positive)
    s_upper = s.upper()
    if s_upper.endswith("DR") or s_upper.endswith("DR."):
        negative = True
        s = re.sub(r'\s*DR\.?\s*$', '', s, flags=re.IGNORECASE)
    elif s_upper.endswith("CR") or s_upper.endswith("CR."):
        s = re.sub(r'\s*CR\.?\s*$', '', s, flags=re.IGNORECASE)
    # Strip currency prefix (Rs., USD, $, ₹, £, €, INR, Kr., etc.) and suffix
    s = re.sub(r'^[A-Za-z₹$€£¥₩]{1,5}\.?\s*', '', s)
    s = re.sub(r'\s*[A-Za-z₹$€£¥₩]{1,5}\.?\s*$', '', s)
    # Strip remaining non-numeric (keep digits, dots, commas, minus)
    s = re.sub(r"[^\d.,-]", "", s.replace("(", "").replace(")", ""))
    if not s:
        return None
    # European format: 1.234,56  →  1234.56
    if re.match(r"^\d{1,3}(\.\d{3})+(,\d{1,2})?$", s):
        s = s.replace(".", "").replace(",", ".")
    # European format without thousands separator: 1234,56
    elif re.match(r"^\d+(,\d{1,2})$", s):
        s = s.replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        val = float(s)
    except ValueError:
        return None
    return -val if negative else val


# ── Column Data Profiler (AI-like heuristic analysis) ───────────────────────

class _ColumnProfile:
    """Statistical profile of a single CSV column's values."""
    DATE = "date"
    MONEY = "money"
    TEXT = "text"
    TYPE_INDICATOR = "type_indicator"  # DR/CR, Debit/Credit
    NUMERIC = "numeric"
    EMPTY = "empty"
    MIXED = "mixed"

    _DATE_PATTERNS = [
        re.compile(r'^\d{1,4}[/\-.\s]\d{1,2}[/\-.\s]\d{1,4}$'),
        re.compile(r'^\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}$'),
        re.compile(r'^[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{2,4}$'),
        re.compile(r'^\d{4}\d{2}\d{2}$'),  # 20240115
        re.compile(r'^\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\s+\d{1,2}:\d{2}'),  # with time
    ]

    _TYPE_WORDS = {"dr", "cr", "dr.", "cr.", "debit", "credit", "d", "c",
                   "dr/cr", "cr/dr", "db", "debit/credit", "credit/debit"}

    def __init__(self, header: str, values: list[str]):
        self.header = header
        self.values = values
        self.n_total = len(values)
        self.n_non_empty = sum(1 for v in values if v.strip())
        self.n_date = 0
        self.n_money = 0
        self.n_text = 0
        self.n_type = 0
        self.n_numeric = 0
        self.money_has_negatives = False
        self.money_values: list[float] = []
        self._analyze()

    def _analyze(self):
        for raw in self.values:
            v = raw.strip()
            if not v:
                continue
            # Date check
            if any(p.match(v) for p in self._DATE_PATTERNS):
                self.n_date += 1
                continue
            # Type indicator check (short strings like DR, CR, Debit, etc.)
            if v.lower().rstrip(".") in self._TYPE_WORDS or len(v) <= 2 and v.upper() in ("D", "C", "DR", "CR"):
                self.n_type += 1
                continue
            # Money check
            amt = _parse_amount(v)
            if amt is not None:
                self.n_money += 1
                self.money_values.append(amt)
                if amt < 0:
                    self.money_has_negatives = True
                continue
            # Text (contains letters)
            if re.search(r'[a-zA-Z]{2,}', v):
                self.n_text += 1
                continue
            # Pure numeric
            try:
                float(v.replace(",", ""))
                self.n_numeric += 1
            except ValueError:
                self.n_text += 1  # fallback to text

    @property
    def inferred_type(self) -> str:
        if self.n_non_empty == 0:
            return self.EMPTY
        n = self.n_non_empty
        if self.n_date / n >= 0.5:
            return self.DATE
        if self.n_type / n >= 0.5:
            return self.TYPE_INDICATOR
        if (self.n_money + self.n_numeric) / n >= 0.5:
            return self.MONEY
        if self.n_text / n >= 0.4:
            return self.TEXT
        return self.MIXED

    @property
    def money_score(self) -> float:
        if self.n_non_empty == 0:
            return 0.0
        return (self.n_money + self.n_numeric) / self.n_non_empty

    @property
    def date_score(self) -> float:
        if self.n_non_empty == 0:
            return 0.0
        return self.n_date / self.n_non_empty

    @property
    def text_score(self) -> float:
        if self.n_non_empty == 0:
            return 0.0
        return self.n_text / self.n_non_empty

    @property
    def type_score(self) -> float:
        if self.n_non_empty == 0:
            return 0.0
        return self.n_type / self.n_non_empty


# ── Name-hint scoring (secondary signal on top of data profiling) ───────────

_NAME_HINTS = {
    "date":        ["date", "dt", "posted", "trans date", "txn date", "value date",
                    "posting", "effective", "book", "settlement", "transaction date"],
    "description": ["description", "desc", "memo", "detail", "details", "narrative",
                    "payee", "name", "merchant", "particulars", "reference",
                    "remark", "remarks", "narration", "transaction description"],
    "amount":      ["amount", "amt", "value", "sum", "total", "net", "gross",
                    "transaction amount", "summary amt", "txn amt", "trans amt"],
    "debit":       ["debit", "dr", "withdrawal", "money out", "outflow", "spent",
                    "expense", "debit amount", "debit amt", "withdrawal amt"],
    "credit":      ["credit", "cr", "deposit", "money in", "inflow", "income",
                    "received", "credit amount", "credit amt", "deposit amt"],
    "type":        ["type", "txn type", "trans type", "dr/cr", "dr cr",
                    "transaction type"],
    "balance":     ["balance", "bal", "running balance", "closing balance",
                    "available balance", "ledger balance"],
    "category":    ["category", "tag", "label", "group"],
}


def _name_hint_score(header: str, role: str) -> float:
    """Return 0-1 score for how well a header name matches a role."""
    h = re.sub(r'[.\s_/\-()]+', ' ', header.lower()).strip()
    if not h:
        return 0.0
    candidates = _NAME_HINTS.get(role, [])
    for c in candidates:
        cn = re.sub(r'[.\s_/\-()]+', ' ', c.lower()).strip()
        if cn == h:
            return 1.0
        # Candidate phrase found inside header (e.g. candidate "trans date" in header "transaction date")
        if cn in h:
            return 0.7
        # Header found in candidate — only if header covers most of candidate
        if h in cn and len(h) >= len(cn) * 0.6:
            return 0.5
        # Check if individual words overlap
        c_words = set(cn.split())
        h_words = set(h.split())
        overlap = c_words & h_words
        if overlap and len(overlap) / max(len(c_words), 1) >= 0.5:
            return 0.4
    return 0.0


# ── Smart CSV Layout Detector ───────────────────────────────────────────────

class _CSVLayout:
    """AI-powered layout detector: profiles every column's data + header hints."""

    SINGLE_AMOUNT = "single_amount"
    SINGLE_AMOUNT_WITH_TYPE = "amount+type"
    SPLIT_DEBIT_CREDIT = "split"

    def __init__(self, headers: list[str], all_rows: list[dict]):
        self.headers = [h for h in headers if h and h.strip()]
        self.col: dict[str, Optional[str]] = {
            "date": None, "description": None, "amount": None,
            "debit": None, "credit": None, "type": None,
            "balance": None, "category": None,
        }
        self.layout_type: Optional[str] = None
        self.profiles: dict[str, _ColumnProfile] = {}
        self.detection_method = "unknown"

        # Build profiles from up to 50 sample rows
        sample = all_rows[:50]
        for h in self.headers:
            vals = [(row.get(h, "") or "") for row in sample]
            self.profiles[h] = _ColumnProfile(h, vals)

        self._detect()

    def _detect(self):
        """Two-pass detection: header hints first, then data profiling."""
        assigned: set[str] = set()   # headers already assigned

        # ── Pass 1: strong header matches ──
        # Process type BEFORE debit/credit so DR/CR columns aren't misidentified
        for role in ("date", "description", "amount", "type", "debit", "credit",
                     "balance", "category"):
            best_h, best_score = None, 0.3  # min threshold
            for h in self.headers:
                if h in assigned:
                    continue
                score = _name_hint_score(h, role)
                # Boost if data type agrees
                prof = self.profiles[h]
                if role == "date" and prof.inferred_type == _ColumnProfile.DATE:
                    score += 0.3
                elif role in ("amount", "debit", "credit", "balance") and prof.inferred_type == _ColumnProfile.MONEY:
                    score += 0.3
                elif role == "description" and prof.inferred_type == _ColumnProfile.TEXT:
                    score += 0.3
                elif role == "type" and prof.inferred_type == _ColumnProfile.TYPE_INDICATOR:
                    score += 0.3
                # Penalize: type-indicator data shouldn't become an amount role
                if role in ("amount", "debit", "credit", "balance") and prof.inferred_type == _ColumnProfile.TYPE_INDICATOR:
                    score -= 0.4
                if score > best_score:
                    best_score = score
                    best_h = h
            if best_h:
                self.col[role] = best_h
                assigned.add(best_h)

        # ── Pass 2: data-driven assignment for missing roles ──
        # Date
        if not self.col["date"]:
            best = self._best_unassigned(assigned, "date_score", 0.4)
            if best:
                self.col["date"] = best
                assigned.add(best)

        # Description (prefer longest text column)
        if not self.col["description"]:
            text_cols = [(h, p) for h, p in self.profiles.items()
                         if h not in assigned and p.text_score >= 0.3]
            if text_cols:
                # Pick column with highest average text length
                best_h = max(text_cols, key=lambda x: x[1].text_score)[0]
                self.col["description"] = best_h
                assigned.add(best_h)

        # Money columns
        money_cols = [(h, p) for h, p in self.profiles.items()
                      if h not in assigned and p.money_score >= 0.4]
        money_cols.sort(key=lambda x: -x[1].money_score)

        # Type indicator
        if not self.col["type"]:
            type_cols = [(h, p) for h, p in self.profiles.items()
                         if h not in assigned and p.type_score >= 0.4]
            if type_cols:
                best_t = max(type_cols, key=lambda x: x[1].type_score)[0]
                self.col["type"] = best_t
                assigned.add(best_t)
                # Remove from money list
                money_cols = [(h, p) for h, p in money_cols if h != best_t]

        # Assign money columns
        if not self.col["amount"] and not self.col["debit"] and not self.col["credit"]:
            if len(money_cols) >= 2:
                # Two money columns: could be debit+credit OR amount+balance
                # Heuristic: if one has name hint for balance, treat as amount+balance
                c1, c2 = money_cols[0], money_cols[1]
                if _name_hint_score(c1[0], "balance") > 0.3 or _name_hint_score(c2[0], "balance") > 0.3:
                    # One is balance
                    if _name_hint_score(c2[0], "balance") > _name_hint_score(c1[0], "balance"):
                        self.col["amount"] = c1[0]
                        self.col["balance"] = c2[0]
                        assigned.update([c1[0], c2[0]])
                    else:
                        self.col["amount"] = c2[0]
                        self.col["balance"] = c1[0]
                        assigned.update([c1[0], c2[0]])
                else:
                    # Check if they look like separate debit/credit
                    # (typically one has values where the other is empty)
                    vals1 = [v for v in c1[1].money_values if abs(v) > 0.001]
                    vals2 = [v for v in c2[1].money_values if abs(v) > 0.001]
                    both_partial = (c1[1].n_non_empty < c1[1].n_total * 0.8 and
                                    c2[1].n_non_empty < c2[1].n_total * 0.8)
                    if both_partial:
                        # Split debit/credit pattern (each has gaps)
                        self.col["debit"] = c1[0]
                        self.col["credit"] = c2[0]
                        assigned.update([c1[0], c2[0]])
                    else:
                        # Treat higher-scoring as amount, second as balance
                        self.col["amount"] = c1[0]
                        if len(money_cols) > 1:
                            self.col["balance"] = c2[0]
                        assigned.update([c1[0], c2[0]])
            elif len(money_cols) == 1:
                self.col["amount"] = money_cols[0][0]
                assigned.add(money_cols[0][0])

        # ── If *still* no amount/debit → brute force: pick ANY column with numbers ──
        if not self.col["amount"] and not self.col["debit"]:
            for h in self.headers:
                if h in assigned:
                    continue
                p = self.profiles[h]
                if p.n_money >= 1 or p.n_numeric >= 1:
                    self.col["amount"] = h
                    assigned.add(h)
                    break

        # Balance (if not assigned yet)
        if not self.col["balance"]:
            remaining_money = [(h, p) for h, p in self.profiles.items()
                               if h not in assigned and p.money_score >= 0.3]
            if remaining_money:
                self.col["balance"] = remaining_money[0][0]
                assigned.add(remaining_money[0][0])

        # Description fallback: longest unassigned text-ish column
        if not self.col["description"]:
            for h in self.headers:
                if h in assigned:
                    continue
                p = self.profiles[h]
                if p.n_text >= 1 or p.inferred_type == _ColumnProfile.MIXED:
                    self.col["description"] = h
                    assigned.add(h)
                    break

        # ── Determine layout type ──
        if self.col["debit"] and self.col["credit"]:
            self.layout_type = self.SPLIT_DEBIT_CREDIT
        elif self.col["amount"] and self.col["type"]:
            self.layout_type = self.SINGLE_AMOUNT_WITH_TYPE
        elif self.col["amount"]:
            self.layout_type = self.SINGLE_AMOUNT
        elif self.col["debit"]:
            self.col["amount"] = self.col["debit"]
            self.layout_type = self.SINGLE_AMOUNT
        elif self.col["credit"]:
            self.col["amount"] = self.col["credit"]
            self.layout_type = self.SINGLE_AMOUNT

        # Set detection method
        self.detection_method = "AI data profiling" if self.layout_type else "failed"

    def _best_unassigned(self, assigned: set, score_attr: str, threshold: float) -> Optional[str]:
        best_h, best_s = None, threshold
        for h, p in self.profiles.items():
            if h in assigned:
                continue
            s = getattr(p, score_attr, 0.0)
            if s > best_s:
                best_s = s
                best_h = h
        return best_h

    @property
    def detected(self) -> bool:
        return self.layout_type is not None

    def describe(self) -> str:
        lines = [f"Layout: {self.layout_type or 'unknown'} ({self.detection_method})"]
        for role, hdr in self.col.items():
            if hdr:
                p = self.profiles.get(hdr)
                dtype = p.inferred_type if p else "?"
                lines.append(f"  {role:>12s} → {hdr}  (detected as: {dtype})")
        return "\n".join(lines)


# ── Transaction classification helpers ──────────────────────────────────────

_DEBIT_KEYWORDS = {"debit", "dr", "dr.", "withdrawal", "purchase", "payment",
                   "pos", "atm", "transfer out", "bill pay", "d"}
_CREDIT_KEYWORDS = {"credit", "cr", "cr.", "deposit", "refund", "transfer in",
                    "interest", "cashback", "reversal", "salary", "income", "c"}


def _classify_type(type_str: str) -> str:
    t = type_str.lower().strip().rstrip(".")
    if t in _DEBIT_KEYWORDS or any(k in t for k in _DEBIT_KEYWORDS):
        return "debit"
    if t in _CREDIT_KEYWORDS or any(k in t for k in _CREDIT_KEYWORDS):
        return "credit"
    return "unknown"


_INCOME_CATEGORY_KEYWORDS = {
    "Salary": ["salary", "payroll", "wages", "direct dep", "employer", "paycheck"],
    "Freelance / Business": ["freelance", "invoice", "consulting", "contract"],
    "Transfer In": ["transfer in", "xfer in", "zelle", "wire in", "ach credit",
                    "venmo", "cashapp"],
    "Refund": ["refund", "return", "reversal", "rebate", "cashback"],
    "Interest / Dividends": ["interest", "dividend", "apy", "yield", "capital gain"],
    "Government": ["irs", "tax refund", "social security", "stimulus", "government"],
}

_EXPENSE_CATEGORY_KEYWORDS = {
    "Food & Groceries": ["grocery", "supermarket", "walmart", "costco", "trader joe", "whole foods",
                          "kroger", "safeway", "aldi", "publix", "target"],
    "Dining Out": ["restaurant", "mcdonald", "starbucks", "chipotle", "dunkin", "subway",
                   "pizza", "burger", "cafe", "coffee", "doordash", "uber eats", "grubhub"],
    "Transportation": ["gas", "fuel", "shell", "chevron", "bp", "uber", "lyft", "parking",
                        "toll", "transit", "metro", "amtrak"],
    "Utilities": ["electric", "water", "gas bill", "internet", "comcast", "spectrum",
                  "at&t", "verizon", "t-mobile", "phone"],
    "Shopping": ["amazon", "ebay", "etsy", "best buy", "apple store", "home depot", "ikea"],
    "Entertainment": ["netflix", "spotify", "hulu", "disney", "hbo", "movie", "theater",
                       "gaming", "steam", "playstation", "xbox"],
    "Healthcare": ["pharmacy", "cvs", "walgreens", "doctor", "hospital", "medical", "dental",
                   "vision", "optometrist"],
    "Insurance": ["insurance", "geico", "allstate", "progressive", "state farm"],
    "Subscriptions": ["subscription", "membership", "monthly", "annual"],
    "Housing": ["rent", "mortgage", "hoa"],
}


def _guess_expense_category(description: str) -> str:
    desc_lower = description.lower()
    for category, keywords in _EXPENSE_CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return "Other"


def _guess_income_category(description: str) -> str:
    desc_lower = description.lower()
    for category, keywords in _INCOME_CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return "Income"


# ── Bank Statement Import Dialog ────────────────────────────────────────────

class BankStatementImportDialog(QDialog):
    """AI-powered bank statement importer.

    1. Reads any CSV / text file
    2. Profiles every column's data to determine type (date / money / text / type-indicator)
    3. Auto-assigns columns with header-name hints + data analysis
    4. Lets user override column assignments via dropdowns
    5. Color-coded debit/credit preview with filtering
    """

    _ROLES = ["(skip)", "date", "description", "amount", "debit", "credit",
              "type", "balance", "category"]

    def __init__(self, parent=None, year=None, month=None):
        super().__init__(parent)
        self.setWindowTitle("🤖 AI Bank Statement Importer")
        self.setMinimumSize(900, 650)
        self.setModal(True)
        self._year = year or datetime.now().year
        self._month = month or datetime.now().month
        self._rows: list[dict] = []
        self._all_raw_rows: list[dict] = []
        self._layout: Optional[_CSVLayout] = None
        self._mapping_combos: list[QComboBox] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        self.setStyleSheet("""
            QDialog { background-color: #0d1117; color: #e6eef8; }
            QLabel { color: #c7d2e0; }
            QTableWidget { background-color: #161b22; color: #e6eef8;
                           border: 1px solid #30363d; border-radius: 6px; }
            QHeaderView::section { background: #1c2128; color: #8b949e; padding: 6px;
                                   border: none; border-bottom: 1px solid #30363d;
                                   font-weight: bold; }
            QComboBox { background-color: #161b22; color: #e6eef8;
                        border: 1px solid #30363d; border-radius: 6px; padding: 4px; }
            QFrame#mappingFrame { background-color: #161b22; border: 1px solid #30363d;
                                  border-radius: 8px; padding: 8px; }
        """)

        # Title
        title = QLabel("🤖 Smart Bank Statement Importer")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #58a6ff;")
        layout.addWidget(title)

        info = QLabel(
            "Load any CSV — the AI engine profiles every column's data to auto-detect\n"
            "dates, amounts, descriptions, and debit/credit. Override below if needed."
        )
        info.setWordWrap(True)
        info.setFont(QFont("Segoe UI", 9))
        info.setStyleSheet("color: #8b949e;")
        layout.addWidget(info)

        # Browse row
        top = QHBoxLayout()
        browse_btn = PremiumButton("Browse CSV…", style=PremiumButton.Style.PRIMARY, icon_name="upload")
        browse_btn.clicked.connect(self._browse)
        top.addWidget(browse_btn)
        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("color: #8b949e; font-size: 11px; padding-left: 8px;")
        top.addWidget(self.file_label, 1)
        layout.addLayout(top)

        # Column mapping area (populated after file load)
        self.mapping_frame = QFrame()
        self.mapping_frame.setObjectName("mappingFrame")
        self.mapping_frame.setVisible(False)
        self.mapping_layout = QGridLayout(self.mapping_frame)
        self.mapping_layout.setSpacing(6)
        layout.addWidget(self.mapping_frame)

        # Re-analyze button
        reanalyze_row = QHBoxLayout()
        self.reanalyze_btn = PremiumButton("🔄 Re-analyze with overrides",
                                           style=PremiumButton.Style.FLAT)
        self.reanalyze_btn.clicked.connect(self._reanalyze)
        self.reanalyze_btn.setVisible(False)
        reanalyze_row.addWidget(self.reanalyze_btn)
        reanalyze_row.addStretch()
        self.layout_label = QLabel("")
        self.layout_label.setStyleSheet("color: #3fb950; font-size: 11px;")
        self.layout_label.setWordWrap(True)
        reanalyze_row.addWidget(self.layout_label, 1)
        layout.addLayout(reanalyze_row)

        # Filter row
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Show:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Transactions", "Debits (Expenses) Only",
                                    "Credits (Income) Only"])
        self.filter_combo.setFixedWidth(220)
        self.filter_combo.currentIndexChanged.connect(self._apply_filter)
        filter_row.addWidget(self.filter_combo)
        filter_row.addStretch()
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        filter_row.addWidget(self.summary_label)
        layout.addLayout(filter_row)

        # Preview table
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(7)
        self.preview_table.setHorizontalHeaderLabels(
            ["Import", "Date", "Description", "Type", "Amount", "Category (auto)", "Balance"])
        h = self.preview_table.horizontalHeader()
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setAlternatingRowColors(True)
        layout.addWidget(self.preview_table, 1)

        self.count_label = QLabel("0 transactions found")
        self.count_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        layout.addWidget(self.count_label)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = PremiumButton("Cancel", style=PremiumButton.Style.FLAT)
        cancel_btn.clicked.connect(self.reject)
        import_btn = PremiumButton("Import Selected", style=PremiumButton.Style.SUCCESS, icon_name="download")
        import_btn.clicked.connect(self._do_import)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(import_btn)
        layout.addLayout(btn_row)

    # ── File loading ────────────────────────────────────────────────────────

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Bank CSV", "",
            "CSV / Text Files (*.csv *.txt *.tsv);;All Files (*.*)")
        if not path:
            return
        self._parse(path)

    @staticmethod
    def _read_file_content(path: str) -> str:
        raw = open(path, "rb").read(8192)
        if raw[:2] in (b"\xff\xfe", b"\xfe\xff") or b"\x00" in raw[:200]:
            enc = "utf-16"
        else:
            enc = "utf-8-sig"
        with open(path, "r", encoding=enc, errors="replace") as f:
            return f.read()

    @staticmethod
    def _skip_preamble(content: str) -> str:
        """Find the real data section in bank CSVs that have summary preambles.

        Many banks (e.g. Bank of America) export CSVs with a summary block
        at the top (fewer columns), a blank line, then the real transactions
        with more columns.  Strategy:
          1. Split on blank lines into sections
          2. For each section, find the first line with ≥2 delimiters (candidate header)
          3. Pick the section whose candidate header has the MOST columns
        Falls back to the first line with ≥2 delimiters if no blank-line sections.
        """
        lines = content.splitlines()

        # Split into sections separated by blank lines
        sections: list[list[str]] = []
        current: list[str] = []
        for line in lines:
            if not line.strip():
                if current:
                    sections.append(current)
                    current = []
            else:
                current.append(line)
        if current:
            sections.append(current)

        if len(sections) >= 2:
            # Multiple sections — pick the one whose first line has the most delimiters
            best_section = None
            best_cols = 0
            for sec in sections:
                first = sec[0]
                n_cols = first.count(",") + first.count(";") + first.count("\t") + 1
                # Prefer sections with more data rows (not just 1-2 summary lines)
                row_bonus = min(len(sec) - 1, 5)  # up to 5 bonus points for data rows
                score = n_cols * 10 + row_bonus
                if score > best_cols:
                    best_cols = score
                    best_section = sec
            if best_section:
                return "\n".join(best_section)

        # Fallback: find first line with ≥2 delimiters
        for i, line in enumerate(lines):
            seps = line.count(",") + line.count(";") + line.count("\t")
            if seps >= 2:
                return "\n".join(lines[i:])
        return content

    def _parse(self, path: str):
        try:
            content = self._read_file_content(path)
            content = self._skip_preamble(content)

            try:
                dialect = csv.Sniffer().sniff(content[:4096], delimiters=",;\t|")
            except csv.Error:
                dialect = None

            reader = csv.DictReader(io.StringIO(content), dialect=dialect) if dialect else csv.DictReader(io.StringIO(content))
            headers = reader.fieldnames or []
            if not headers:
                QMessageBox.warning(self, "Empty File", "No headers found in CSV.")
                return

            self._all_raw_rows = list(reader)
            if not self._all_raw_rows:
                QMessageBox.warning(self, "Empty File", "CSV has headers but no data rows.")
                return

            self.file_label.setText(f"📄 {Path(path).name}  ({len(self._all_raw_rows)} rows, {len(headers)} columns)")

            # Run AI detection
            self._layout = _CSVLayout(headers, self._all_raw_rows)
            self._show_mapping()
            self._process_rows()

        except Exception as e:
            QMessageBox.critical(self, "Parse Error", f"Failed to read file:\n{e}")

    def _show_mapping(self):
        """Build the column-mapping dropdowns from detected layout."""
        # Clear old mapping widgets
        while self.mapping_layout.count():
            item = self.mapping_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._mapping_combos.clear()

        L = self._layout
        # Header row
        hdr_lbl = QLabel("Column Mapping (auto-detected — override if needed):")
        hdr_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        hdr_lbl.setStyleSheet("color: #58a6ff;")
        self.mapping_layout.addWidget(hdr_lbl, 0, 0, 1, 4)

        # Reverse map: header → assigned role
        h_to_role = {}
        for role, h in L.col.items():
            if h:
                h_to_role[h] = role

        row = 1
        col = 0
        for h in L.headers:
            prof = L.profiles.get(h)
            dtype = prof.inferred_type if prof else "?"
            label_text = f"{h}  [{dtype}]"
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #c7d2e0; font-size: 10px;")
            lbl.setFixedWidth(180)

            combo = QComboBox()
            combo.addItems(self._ROLES)
            combo.setFixedWidth(120)
            # Set current role
            assigned_role = h_to_role.get(h, "(skip)")
            idx = self._ROLES.index(assigned_role) if assigned_role in self._ROLES else 0
            combo.setCurrentIndex(idx)
            combo.setProperty("header", h)

            self.mapping_layout.addWidget(lbl, row, col * 2)
            self.mapping_layout.addWidget(combo, row, col * 2 + 1)
            self._mapping_combos.append(combo)

            col += 1
            if col >= 2:  # 2 columns of mappings per row
                col = 0
                row += 1

        self.mapping_frame.setVisible(True)
        self.reanalyze_btn.setVisible(True)

    def _reanalyze(self):
        """Re-process rows using user-overridden column mappings."""
        if not self._layout:
            return
        # Read combos into layout.col
        for role in self._layout.col:
            self._layout.col[role] = None
        for combo in self._mapping_combos:
            h = combo.property("header")
            role = combo.currentText()
            if role != "(skip)":
                self._layout.col[role] = h

        # Re-determine layout type
        L = self._layout
        if L.col.get("debit") and L.col.get("credit"):
            L.layout_type = _CSVLayout.SPLIT_DEBIT_CREDIT
        elif L.col.get("amount") and L.col.get("type"):
            L.layout_type = _CSVLayout.SINGLE_AMOUNT_WITH_TYPE
        elif L.col.get("amount"):
            L.layout_type = _CSVLayout.SINGLE_AMOUNT
        else:
            QMessageBox.warning(self, "No Amount Column",
                                "Please assign at least one column as 'amount', 'debit', or 'credit'.")
            return

        L.detection_method = "manual override"
        self._process_rows()

    def _process_rows(self):
        """Extract transactions from raw rows using current layout."""
        L = self._layout
        if not L or not L.detected:
            self.layout_label.setText("❌ Could not detect layout — please assign columns manually above.")
            self._rows = []
            self._populate([])
            return

        self.layout_label.setText(
            f"✅ {L.layout_type} ({L.detection_method})  •  "
            + "  •  ".join(f"{r}={h}" for r, h in L.col.items() if h)
        )

        self._rows = []
        for raw_row in self._all_raw_rows:
            txn = self._extract_transaction(raw_row)
            if txn:
                self._rows.append(txn)

        self._update_summary()
        self._apply_filter()

        if not self._rows:
            self.count_label.setText(
                f"⚠️ 0 transactions extracted from {len(self._all_raw_rows)} rows — "
                f"try reassigning columns above")

    def _extract_transaction(self, raw: dict) -> Optional[dict]:
        L = self._layout
        if not L:
            return None

        # Description
        desc = (raw.get(L.col.get("description") or "", "") or "").strip()
        if not desc:
            desc = " | ".join(
                v.strip() for k, v in raw.items()
                if v and v.strip() and _parse_amount(v.strip()) is None
                and not re.match(r'^\d{1,4}[/\-.\s]\d{1,2}[/\-.\s]\d{1,4}$', v.strip())
            )[:200] or "Transaction"

        # Date
        date_str = (raw.get(L.col.get("date") or "", "") or "").strip()
        dt = self._parse_date(date_str)

        # Amount & direction
        txn_type = "debit"
        amount = 0.0

        if L.layout_type == _CSVLayout.SPLIT_DEBIT_CREDIT:
            debit_val = _parse_amount(raw.get(L.col.get("debit") or "", ""))
            credit_val = _parse_amount(raw.get(L.col.get("credit") or "", ""))
            if debit_val and abs(debit_val) > 0.001:
                amount = abs(debit_val)
                txn_type = "debit"
            elif credit_val and abs(credit_val) > 0.001:
                amount = abs(credit_val)
                txn_type = "credit"
            else:
                return None

        elif L.layout_type == _CSVLayout.SINGLE_AMOUNT_WITH_TYPE:
            val = _parse_amount(raw.get(L.col.get("amount") or "", ""))
            if val is None or abs(val) < 0.001:
                return None
            amount = abs(val)
            type_str = raw.get(L.col.get("type") or "", "") or ""
            classified = _classify_type(type_str)
            if classified == "credit":
                txn_type = "credit"
            elif classified == "debit":
                txn_type = "debit"
            else:
                txn_type = "credit" if val > 0 else "debit"

        elif L.layout_type == _CSVLayout.SINGLE_AMOUNT:
            val = _parse_amount(raw.get(L.col.get("amount") or "", ""))
            if val is None or abs(val) < 0.001:
                return None
            amount = abs(val)
            txn_type = "credit" if val > 0 else "debit"

        else:
            return None

        # Balance
        balance = _parse_amount(raw.get(L.col.get("balance") or "", ""))

        # Category
        csv_cat = (raw.get(L.col.get("category") or "", "") or "").strip()
        if csv_cat:
            category = csv_cat
        elif txn_type == "credit":
            category = _guess_income_category(desc)
        else:
            category = _guess_expense_category(desc)

        return {"date": dt, "description": desc, "amount": amount,
                "type": txn_type, "category": category, "balance": balance}

    @staticmethod
    def _parse_date(s: str) -> datetime:
        if not s:
            return datetime.now()
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y",
                    "%m/%d/%y", "%d-%m-%Y", "%Y/%m/%d", "%d %b %Y",
                    "%b %d, %Y", "%d-%b-%Y", "%d %B %Y", "%Y%m%d",
                    "%d.%m.%Y", "%d.%m.%y", "%Y-%m-%dT%H:%M:%S",
                    "%m/%d/%Y %H:%M", "%d/%m/%Y %H:%M"):
            try:
                return datetime.strptime(s.strip(), fmt)
            except ValueError:
                continue
        return datetime.now()

    # ── Display ─────────────────────────────────────────────────────────────

    def _update_summary(self):
        total_debit = sum(r["amount"] for r in self._rows if r["type"] == "debit")
        total_credit = sum(r["amount"] for r in self._rows if r["type"] == "credit")
        n_debit = sum(1 for r in self._rows if r["type"] == "debit")
        n_credit = sum(1 for r in self._rows if r["type"] == "credit")
        self.summary_label.setText(
            f"📉 {n_debit} debits (${total_debit:,.2f})  |  "
            f"📈 {n_credit} credits (${total_credit:,.2f})  |  "
            f"Net: ${total_credit - total_debit:,.2f}")

    def _apply_filter(self):
        idx = self.filter_combo.currentIndex()
        if idx == 1:
            visible = [r for r in self._rows if r["type"] == "debit"]
        elif idx == 2:
            visible = [r for r in self._rows if r["type"] == "credit"]
        else:
            visible = self._rows
        self._populate(visible)

    def _populate(self, rows: list):
        self.preview_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            cb = QCheckBox()
            cb.setChecked(True)
            self.preview_table.setCellWidget(i, 0, cb)
            self.preview_table.setItem(i, 1, QTableWidgetItem(
                r["date"].strftime("%Y-%m-%d")))
            self.preview_table.setItem(i, 2, QTableWidgetItem(r["description"]))

            type_item = QTableWidgetItem(r["type"].upper())
            if r["type"] == "credit":
                type_item.setForeground(QColor("#3fb950"))
            else:
                type_item.setForeground(QColor("#f85149"))
            self.preview_table.setItem(i, 3, type_item)

            amt_text = f"${r['amount']:,.2f}"
            amt_item = QTableWidgetItem(amt_text)
            if r["type"] == "credit":
                amt_item.setForeground(QColor("#3fb950"))
            else:
                amt_item.setForeground(QColor("#f85149"))
            self.preview_table.setItem(i, 4, amt_item)

            self.preview_table.setItem(i, 5, QTableWidgetItem(r["category"]))

            bal_text = f"${r['balance']:,.2f}" if r.get("balance") is not None else ""
            self.preview_table.setItem(i, 6, QTableWidgetItem(bal_text))

        self.count_label.setText(f"{len(rows)} transactions shown  ({len(self._rows)} total)")

    # ── Import to DB ────────────────────────────────────────────────────────

    def _do_import(self):
        from src.database.config import get_session
        from src.database.operations import BudgetManager
        session = get_session()
        imported_debits = 0
        imported_credits = 0
        try:
            period = BudgetManager.get_or_create_period(session, self._year, self._month)
            idx = self.filter_combo.currentIndex()
            if idx == 1:
                visible = [r for r in self._rows if r["type"] == "debit"]
            elif idx == 2:
                visible = [r for r in self._rows if r["type"] == "credit"]
            else:
                visible = self._rows

            for i, r in enumerate(visible):
                cb = self.preview_table.cellWidget(i, 0)
                if not cb or not cb.isChecked():
                    continue
                title = r["description"][:255]
                if r["type"] == "credit":
                    title = f"[INCOME] {title}"

                BudgetManager.add_entry(
                    session, period.id,
                    title=title,
                    amount=r["amount"] if r["type"] == "debit" else -r["amount"],
                    category=r["category"],
                    entry_date=r["date"],
                    notes=f"{r['type'].upper()} — imported from bank statement",
                )
                if r["type"] == "debit":
                    imported_debits += 1
                else:
                    imported_credits += 1
        finally:
            session.close()

        QMessageBox.information(
            self, "Import Complete",
            f"Imported {imported_debits} expenses and {imported_credits} income entries.")
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
#  4.  BULK FOLDER SCAN  →  Document Vault
# ═══════════════════════════════════════════════════════════════════════════════

_DOC_CATEGORY_KEYWORDS = {
    "passport": ["passport"],
    "tax_documents": ["tax", "w2", "w-2", "1099", "1040", "irs", "tax return"],
    "property_documents": ["property", "deed", "title", "lease", "rental"],
    "certificates": ["certificate", "diploma", "degree", "certification"],
    "immigration_documents": ["visa", "immigration", "i-94", "i-20", "green card", "ead"],
    "medical_records": ["medical", "health", "lab", "prescription", "diagnosis", "xray", "vaccine"],
    "insurance_documents": ["insurance", "policy", "claim", "coverage"],
    "financial_documents": ["bank", "statement", "investment", "stock", "401k", "ira"],
    "legal_documents": ["legal", "contract", "agreement", "court", "attorney", "will", "trust"],
}

_DOC_TYPE_MAP = {
    ".pdf": "pdf", ".jpg": "image", ".jpeg": "image", ".png": "image",
    ".gif": "image", ".bmp": "image",
    ".doc": "word", ".docx": "word",
    ".xls": "excel", ".xlsx": "excel",
    ".txt": "text",
}


def _guess_doc_category(filename: str) -> str:
    name_lower = filename.lower()
    for cat, keywords in _DOC_CATEGORY_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return cat
    return "other"


class BulkDocumentImportDialog(QDialog):
    """Scan a folder and import documents into the vault."""

    MAX_FILE_SIZE_MB = 50

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk Import Documents from Folder")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        self._files = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setStyleSheet("""
            QDialog { background-color: #0d1117; color: #e6eef8; }
            QLabel { color: #c7d2e0; }
            QTableWidget { background-color: #161b22; color: #e6eef8; border: 1px solid #30363d; border-radius: 6px; }
            QHeaderView::section { background: #1c2128; color: #8b949e; padding: 6px; border: none;
                                   border-bottom: 1px solid #30363d; font-weight: bold; }
        """)

        info = QLabel(
            "Select a folder to scan for documents (PDF, images, Word, Excel, text).\n"
            "Categories are auto-detected from filenames. Files over 50 MB are skipped."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        browse_btn = PremiumButton("Select Folder…", style=PremiumButton.Style.PRIMARY, icon_name="upload")
        browse_btn.clicked.connect(self._browse)
        layout.addWidget(browse_btn)

        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(5)
        self.preview_table.setHorizontalHeaderLabels(["Import", "Filename", "Size", "Type", "Category (auto)"])
        self.preview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setAlternatingRowColors(True)
        layout.addWidget(self.preview_table, 1)

        self.count_label = QLabel("0 files found")
        self.count_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        layout.addWidget(self.count_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = PremiumButton("Cancel", style=PremiumButton.Style.FLAT)
        cancel_btn.clicked.connect(self.reject)
        import_btn = PremiumButton("Import Selected", style=PremiumButton.Style.SUCCESS, icon_name="download")
        import_btn.clicked.connect(self._do_import)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(import_btn)
        layout.addLayout(btn_row)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not folder:
            return
        valid_exts = set(_DOC_TYPE_MAP.keys())
        self._files = []
        for p in Path(folder).rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in valid_exts:
                continue
            size_mb = p.stat().st_size / (1024 * 1024)
            if size_mb > self.MAX_FILE_SIZE_MB:
                continue
            self._files.append({
                "path": str(p),
                "name": p.name,
                "size": p.stat().st_size,
                "type": _DOC_TYPE_MAP.get(p.suffix.lower(), "other"),
                "category": _guess_doc_category(p.name),
            })
        self._populate()

    def _populate(self):
        self.preview_table.setRowCount(len(self._files))
        for i, f in enumerate(self._files):
            cb = QCheckBox()
            cb.setChecked(True)
            self.preview_table.setCellWidget(i, 0, cb)
            self.preview_table.setItem(i, 1, QTableWidgetItem(f["name"]))
            size_str = f"{f['size'] / 1024:.0f} KB" if f["size"] < 1024 * 1024 else f"{f['size'] / (1024 * 1024):.1f} MB"
            self.preview_table.setItem(i, 2, QTableWidgetItem(size_str))
            self.preview_table.setItem(i, 3, QTableWidgetItem(f["type"].upper()))
            self.preview_table.setItem(i, 4, QTableWidgetItem(f["category"].replace("_", " ").title()))
        self.count_label.setText(f"{len(self._files)} files found")

    def _do_import(self):
        from src.database.config import get_session
        from src.database.operations import DocumentManager
        from src.database.models import DocumentType, DocumentCategory
        docs_dir = Path("data/documents")
        docs_dir.mkdir(parents=True, exist_ok=True)
        session = get_session()
        imported = 0
        type_map = {"pdf": DocumentType.PDF, "image": DocumentType.IMAGE, "word": DocumentType.WORD,
                     "excel": DocumentType.EXCEL, "text": DocumentType.TEXT, "other": DocumentType.OTHER}
        cat_map = {c.value: c for c in DocumentCategory}
        try:
            for i, f in enumerate(self._files):
                cb = self.preview_table.cellWidget(i, 0)
                if not cb or not cb.isChecked():
                    continue
                src_path = Path(f["path"])
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_name = f"{ts}_{i:04d}_{src_path.name}"
                dest_path = docs_dir / dest_name
                shutil.copy2(src_path, dest_path)

                cat_enum = cat_map.get(f["category"], DocumentCategory.OTHER)
                doc_type = type_map.get(f["type"], DocumentType.OTHER)

                DocumentManager.create_document(
                    session=session,
                    original_filename=src_path.name,
                    stored_filename=dest_name,
                    file_path=str(dest_path),
                    file_size=f["size"],
                    file_type=doc_type,
                    mime_type=src_path.suffix,
                    title=src_path.stem.replace("_", " ").replace("-", " ").title(),
                    category=cat_enum,
                )
                imported += 1
        finally:
            session.close()
        QMessageBox.information(self, "Import Complete", f"Imported {imported} documents into the vault.")
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
#  5.  ACTIVITY QUICK-TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

ACTIVITY_TEMPLATES = [
    {"title": "Pay Rent / Mortgage", "category": "payment", "recurrence": "monthly",
     "emoji": "🏠", "description": "Monthly housing payment"},
    {"title": "Pay Electricity Bill", "category": "payment", "recurrence": "monthly",
     "emoji": "⚡", "description": "Monthly electric utility bill"},
    {"title": "Pay Water Bill", "category": "payment", "recurrence": "monthly",
     "emoji": "💧", "description": "Monthly water utility bill"},
    {"title": "Pay Internet Bill", "category": "payment", "recurrence": "monthly",
     "emoji": "🌐", "description": "Monthly internet/cable bill"},
    {"title": "Pay Phone Bill", "category": "payment", "recurrence": "monthly",
     "emoji": "📱", "description": "Monthly phone bill"},
    {"title": "Car Insurance Payment", "category": "payment", "recurrence": "monthly",
     "emoji": "🚗", "description": "Auto insurance premium"},
    {"title": "Health Insurance Premium", "category": "payment", "recurrence": "monthly",
     "emoji": "🏥", "description": "Monthly health insurance payment"},
    {"title": "Netflix / Streaming", "category": "subscription", "recurrence": "monthly",
     "emoji": "📺", "description": "Monthly streaming subscription"},
    {"title": "Gym Membership", "category": "subscription", "recurrence": "monthly",
     "emoji": "💪", "description": "Monthly gym / fitness membership"},
    {"title": "Grocery Shopping", "category": "task", "recurrence": "weekly",
     "emoji": "🛒", "description": "Weekly grocery run"},
    {"title": "Laundry", "category": "maintenance", "recurrence": "weekly",
     "emoji": "👕", "description": "Weekly laundry / dry cleaning"},
    {"title": "House Cleaning", "category": "maintenance", "recurrence": "weekly",
     "emoji": "🧹", "description": "Weekly home cleaning"},
    {"title": "Doctor Checkup", "category": "health", "recurrence": "yearly",
     "emoji": "👨‍⚕️", "description": "Annual health checkup"},
    {"title": "Dentist Visit", "category": "health", "recurrence": "biweekly",
     "emoji": "🦷", "description": "Regular dental appointment"},
    {"title": "Tax Filing Deadline", "category": "task", "recurrence": "yearly",
     "emoji": "📊", "description": "Annual tax return deadline (April 15)"},
    {"title": "Car Registration Renewal", "category": "task", "recurrence": "yearly",
     "emoji": "🚙", "description": "Annual vehicle registration renewal"},
    {"title": "Passport Renewal", "category": "task", "recurrence": "once",
     "emoji": "🛂", "description": "Renew passport before expiry"},
    {"title": "Review Monthly Budget", "category": "task", "recurrence": "monthly",
     "emoji": "💰", "description": "Monthly budget review and adjustment"},
    {"title": "Backup Personal Data", "category": "maintenance", "recurrence": "monthly",
     "emoji": "💾", "description": "Monthly backup of important files"},
    {"title": "Credit Card Payment", "category": "payment", "recurrence": "monthly",
     "emoji": "💳", "description": "Monthly credit card bill"},
]


class QuickTemplatesDialog(QDialog):
    """Pick common activities from pre-built templates."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quick-Add from Templates")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setStyleSheet("""
            QDialog { background-color: #0d1117; color: #e6eef8; }
            QLabel { color: #c7d2e0; }
        """)

        info = QLabel("Select activities to add from common templates:")
        info.setFont(QFont("Segoe UI", 11))
        layout.addWidget(info)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(10)

        self._checks = []
        for i, tmpl in enumerate(ACTIVITY_TEMPLATES):
            cb = QCheckBox(f"{tmpl['emoji']}  {tmpl['title']}")
            cb.setFont(QFont("Segoe UI", 10))
            cb.setToolTip(f"{tmpl['description']}\nCategory: {tmpl['category'].title()} | Recurrence: {tmpl['recurrence'].title()}")
            cb.setStyleSheet("""
                QCheckBox { padding: 8px 12px; background: #161b22; border: 1px solid #30363d;
                            border-radius: 8px; color: #e6eef8; }
                QCheckBox:hover { border: 1px solid #58a6ff; background: #1c2128; }
                QCheckBox::indicator { width: 18px; height: 18px; }
                QCheckBox::indicator:checked { background: #58a6ff; border-radius: 4px; }
            """)
            grid.addWidget(cb, i // 2, i % 2)
            self._checks.append((cb, tmpl))

        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = PremiumButton("Cancel", style=PremiumButton.Style.FLAT)
        cancel_btn.clicked.connect(self.reject)
        add_btn = PremiumButton("Add Selected", style=PremiumButton.Style.SUCCESS, icon_name="add")
        add_btn.clicked.connect(self._do_add)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(add_btn)
        layout.addLayout(btn_row)

    def _do_add(self):
        from src.database.config import get_session
        from src.database.operations import ActivityManager
        from src.database.models import RecurrenceType, CategoryType
        rec_map = {r.value: r for r in RecurrenceType}
        cat_map = {c.value: c for c in CategoryType}
        session = get_session()
        added = 0
        try:
            for cb, tmpl in self._checks:
                if not cb.isChecked():
                    continue
                now = datetime.now()
                ActivityManager.create_activity(
                    session,
                    title=tmpl["title"],
                    description=tmpl["description"],
                    category=cat_map.get(tmpl["category"], CategoryType.TASK),
                    recurrence_type=rec_map.get(tmpl["recurrence"], RecurrenceType.ONCE),
                    start_date=now,
                    next_due_date=now + timedelta(days=1),
                    reminder_days_before=1,
                )
                added += 1
        finally:
            session.close()
        QMessageBox.information(self, "Templates Added", f"Added {added} activities from templates.")
        self.accept()
