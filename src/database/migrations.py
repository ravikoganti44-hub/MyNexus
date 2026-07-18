"""
Lightweight schema migration runner for SQLite.
Tracks applied migrations in a _migrations table.
Each migration is a (version, description, sql) tuple.
"""
import logging
from sqlalchemy import text
from src.database.config import engine

logger = logging.getLogger(__name__)

# Define migrations in order.  Each is (version_int, description, list_of_sql_statements).
MIGRATIONS: list[tuple[int, str, list[str]]] = [
    (1, "Add tags column to activities", [
        "ALTER TABLE activities ADD COLUMN tags TEXT DEFAULT ''",
    ]),
]


def _ensure_migration_table():
    """Create the _migrations tracking table if it doesn't exist."""
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS _migrations ("
            "  version INTEGER PRIMARY KEY,"
            "  description TEXT,"
            "  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")"
        ))
        conn.commit()


def _get_applied_versions() -> set[int]:
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT version FROM _migrations")).fetchall()
    return {r[0] for r in rows}


def run_migrations():
    """Apply any pending migrations. Safe to call on every startup."""
    _ensure_migration_table()
    applied = _get_applied_versions()

    with engine.connect() as conn:
        for version, desc, stmts in MIGRATIONS:
            if version in applied:
                continue
            logger.info("Applying migration %d: %s", version, desc)
            for sql in stmts:
                conn.execute(text(sql))
            conn.execute(
                text("INSERT INTO _migrations (version, description) VALUES (:v, :d)"),
                {"v": version, "d": desc},
            )
            conn.commit()
            logger.info("Migration %d applied.", version)
