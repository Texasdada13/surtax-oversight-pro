"""
Database utilities for the Surtax Oversight Pro application.
"""

import sqlite3
from pathlib import Path
from flask import g, current_app
from contextlib import contextmanager


def get_db_path() -> Path:
    """Get database path from current app config."""
    from app.config import get_database_path
    return get_database_path(current_app.config)


def get_db():
    """Get database connection for the current request."""
    if 'db' not in g:
        db_path = get_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(str(db_path))
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close database connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


@contextmanager
def get_db_connection(db_path: Path = None):
    """Context manager for database connections outside request context."""
    if db_path is None:
        from app.config import load_config, get_database_path
        config = load_config()
        db_path = get_database_path(config)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Path = None):
    """Initialize database with schema."""
    if db_path is None:
        from app.config import load_config, get_database_path
        config = load_config()
        db_path = get_database_path(config)

    schema_path = Path(__file__).parent / 'models' / 'schema.sql'

    with get_db_connection(db_path) as conn:
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        conn.commit()


def init_app(app):
    """Initialize database handling for Flask app."""
    app.teardown_appcontext(close_db)
