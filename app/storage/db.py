"""
SQLite database setup and connection management.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS transcripts (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    text TEXT NOT NULL,
    backend TEXT NOT NULL,
    model TEXT,
    duration_seconds REAL,
    copied INTEGER NOT NULL DEFAULT 0,
    tags TEXT,
    audio_path TEXT
);
"""


def get_db_path(raw_path: str) -> Path:
    return Path(raw_path).expanduser().resolve()


def init_db(db_path: str) -> sqlite3.Connection:
    """Initialize the database, creating the schema if needed."""
    path = get_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
