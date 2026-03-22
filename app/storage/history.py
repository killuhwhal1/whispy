"""
Transcript history: save, query, delete.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.transcribe.models import TranscriptionResult


class HistoryStore:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save(
        self,
        result: TranscriptionResult,
        copied: bool = False,
        audio_path: str | None = None,
    ) -> str:
        """Persist a transcription result. Returns the new record id."""
        record_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            """
            INSERT INTO transcripts
                (id, created_at, text, backend, model, duration_seconds, copied, audio_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                now,
                result.text,
                result.backend,
                result.model,
                result.duration_seconds,
                1 if copied else 0,
                audio_path,
            ),
        )
        self.conn.commit()
        return record_id

    def clear_audio_path(self, audio_path: str) -> None:
        """Null out audio_path for any records pointing to a deleted file."""
        self.conn.execute(
            "UPDATE transcripts SET audio_path = NULL WHERE audio_path = ?",
            (audio_path,),
        )
        self.conn.commit()

    def mark_copied(self, record_id: str) -> None:
        self.conn.execute(
            "UPDATE transcripts SET copied = 1 WHERE id = ?", (record_id,)
        )
        self.conn.commit()

    def get_recent(self, limit: int = 50) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM transcripts ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]

    def get_by_id(self, record_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM transcripts WHERE id = ?", (record_id,)
        ).fetchone()
        return dict(row) if row else None

    def delete(self, record_id: str) -> None:
        self.conn.execute("DELETE FROM transcripts WHERE id = ?", (record_id,))
        self.conn.commit()

    def search(self, query: str, limit: int = 50) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM transcripts WHERE text LIKE ? ORDER BY created_at DESC LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
        return [dict(row) for row in rows]
