"""
Database session management with proper context managers.
Eliminates session leak and ensures cleanup.
"""
from contextlib import contextmanager
from src.database.config import SessionLocal


@contextmanager
def db_session():
    """
    Context manager for database sessions.

    Usage::

        with db_session() as session:
            results = session.query(Model).all()
            # session auto-commits on success, auto-rolls-back on error
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
