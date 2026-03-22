"""
Transcript export to files (.txt, .md, .json).
"""

from __future__ import annotations

import json
from pathlib import Path


def export_transcript(record: dict, path: str, fmt: str = "txt") -> Path:
    """
    Export a transcript record to a file.

    Args:
        record: dict with keys: id, created_at, text, backend, model, etc.
        path: destination file path (will be created if missing)
        fmt: "txt", "md", or "json"

    Returns:
        The resolved Path of the written file.
    """
    out = Path(path).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        out.write_text(json.dumps(record, indent=2, ensure_ascii=False))
    elif fmt == "md":
        ts = record.get("created_at", "")
        text = record.get("text", "")
        out.write_text(f"# Transcript\n\n**Date:** {ts}\n\n{text}\n")
    else:  # txt default
        out.write_text(record.get("text", ""))

    return out
