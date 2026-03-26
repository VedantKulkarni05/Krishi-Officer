import os
from pathlib import Path
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get('DATABASE_URL')

if not DB_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set it in Render dashboard or .env file."
    )

# Lazy-loaded connection pool: created on first use.
_pool = None


def _get_pool():
    """Lazily initialize and return the connection pool."""
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.SimpleConnectionPool(2, 10, DB_URL)
    return _pool


def get_db_connection():
    """Get a connection from the pool (non-blocking)."""
    return _get_pool().getconn()


def release_db_connection(conn):
    """Return a connection back to the pool after use."""
    if conn is None:
        return

    # If connection is already closed, it cannot be returned to the pool.
    if getattr(conn, "closed", 1) != 0:
        return

    try:
        _get_pool().putconn(conn)
    except pool.PoolError:
        # Fallback for edge cases where this connection is no longer tracked
        # by the current pool instance.
        try:
            conn.close()
        except Exception:
            pass


def initialize_database():
    """Apply schema.sql on startup so required tables always exist."""
    conn = None
    cur = None
    schema_path = Path(__file__).resolve().parent / "schema.sql"

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        with schema_path.open("r", encoding="utf-8") as schema_file:
            cur.execute(schema_file.read())

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            release_db_connection(conn)