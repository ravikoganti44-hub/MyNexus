"""
Data backup, export, and import utilities.
Supports full database backup and JSON export/import.
"""
import json
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

from src.database.config import DATABASE_PATH

logger = logging.getLogger(__name__)

BACKUP_DIR = os.path.join(Path.home(), ".mynexus", "backups")


def create_backup(label: str = "") -> str:
    """
    Create a timestamped copy of the SQLite database.
    Returns the backup file path on success.
    """
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{label}" if label else ""
    backup_name = f"mynexus_backup_{ts}{suffix}.db"
    dest = os.path.join(BACKUP_DIR, backup_name)
    shutil.copy2(DATABASE_PATH, dest)
    logger.info("Backup created: %s", dest)
    return dest


def list_backups() -> list[dict]:
    """Return a list of available backups sorted newest-first."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backups = []
    for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if f.endswith(".db"):
            fpath = os.path.join(BACKUP_DIR, f)
            backups.append({
                "name": f,
                "path": fpath,
                "size": os.path.getsize(fpath),
                "modified": datetime.fromtimestamp(os.path.getmtime(fpath)),
            })
    return backups


def restore_backup(backup_path: str) -> bool:
    """
    Restore a backup by replacing the current database file.
    Creates a safety backup of the current DB first.
    """
    if not os.path.exists(backup_path):
        logger.error("Backup file not found: %s", backup_path)
        return False
    # Safety backup of current state
    create_backup(label="pre_restore")
    shutil.copy2(backup_path, DATABASE_PATH)
    logger.info("Database restored from: %s", backup_path)
    return True


def export_all_data(dest_path: str) -> bool:
    """
    Export all tables to a single JSON file for portability.
    """
    from src.database.config import get_session
    from src.database.models import (
        Activity, Integration, ConnectedApplication, Document,
        BudgetPeriod, BudgetLimit, BudgetEntry, NetWorthSnapshot,
    )
    session = get_session()
    try:
        def _serialize(obj):
            d = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            for k, v in d.items():
                if isinstance(v, datetime):
                    d[k] = v.isoformat()
                elif hasattr(v, "value"):
                    d[k] = v.value  # Enum
            return d

        data = {
            "export_date": datetime.now().isoformat(),
            "version": "1.0",
            "activities": [_serialize(a) for a in session.query(Activity).all()],
            "integrations": [_serialize(i) for i in session.query(Integration).all()],
            "connected_apps": [_serialize(c) for c in session.query(ConnectedApplication).all()],
            "documents": [_serialize(d) for d in session.query(Document).all()],
            "budget_periods": [_serialize(p) for p in session.query(BudgetPeriod).all()],
            "budget_limits": [_serialize(l) for l in session.query(BudgetLimit).all()],
            "budget_entries": [_serialize(e) for e in session.query(BudgetEntry).all()],
            "net_worth_snapshots": [_serialize(s) for s in session.query(NetWorthSnapshot).all()],
        }

        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info("Data exported to: %s", dest_path)
        return True
    except Exception as e:
        logger.error("Export failed: %s", e)
        return False
    finally:
        session.close()


def prune_old_backups(keep: int = 10) -> int:
    """Delete oldest backups keeping only the N most recent. Returns count deleted."""
    backups = list_backups()
    removed = 0
    for b in backups[keep:]:
        try:
            os.remove(b["path"])
            removed += 1
        except OSError:
            pass
    return removed
