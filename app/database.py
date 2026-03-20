"""
Database utilities for the Surtax Oversight Pro application.
Uses PostgreSQL via psycopg2 with DATABASE_URL.
"""

import os
import psycopg2
import psycopg2.extras
from pathlib import Path
from flask import g, current_app
from contextlib import contextmanager


def get_database_url() -> str:
    """Get database URL from environment."""
    url = os.environ.get('DATABASE_URL', '')
    # Render provides postgres:// but psycopg2 needs postgresql://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url


def get_db():
    """Get database connection for the current request."""
    if 'db' not in g:
        g.db = psycopg2.connect(get_database_url())
        g.db.autocommit = True
    return g.db


def close_db(e=None):
    """Close database connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


@contextmanager
def get_db_connection(database_url: str = None):
    """Context manager for database connections outside request context."""
    if database_url is None:
        database_url = get_database_url()

    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    try:
        yield conn
    finally:
        conn.close()


def get_cursor(db):
    """Get a RealDictCursor from a connection."""
    return db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def init_db(database_url: str = None):
    """Initialize database with schema."""
    if database_url is None:
        database_url = get_database_url()

    schema_path = Path(__file__).parent / 'models' / 'schema.sql'

    with get_db_connection(database_url) as conn:
        conn.autocommit = False
        cursor = conn.cursor()
        with open(schema_path, 'r') as f:
            cursor.execute(f.read())
        conn.commit()
        conn.autocommit = True


def init_app(app):
    """Initialize database handling for Flask app."""
    app.teardown_appcontext(close_db)
