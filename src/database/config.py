"""
Database configuration and initialization
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get the database path - use user's home directory for persistence
# This ensures data persists even when running as a bundled EXE
try:
    # Try to use user's home directory (works in development and bundled EXE)
    DATABASE_DIR = os.path.join(Path.home(), '.mynexus', 'data')
except:
    # Fallback to relative path if home directory is not accessible
    DATABASE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')

os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_PATH = os.path.join(DATABASE_DIR, 'projconnect.db')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Print debug info
if os.environ.get('DEBUG_DB'):
    print(f"[DB] Database location: {DATABASE_PATH}")

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def init_db():
    """Initialize database tables and run pending migrations"""
    Base.metadata.create_all(bind=engine)
    from src.database.migrations import run_migrations
    run_migrations()


def get_session():
    """Get a database session"""
    return SessionLocal()
