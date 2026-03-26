import os
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
    _get_pool().putconn(conn)