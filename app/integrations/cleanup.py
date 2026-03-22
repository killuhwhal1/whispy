"""
Recording file cleanup.

Recordings are saved to ~/.local/share/whispy/recordings/ and kept for
RECORDING_TTL_HOURS (default 12h). On each app start, files older than
the TTL are deleted and their DB audio_path references are cleared.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

log = logging.getLogger(__name__)

RECORDINGS_DIR = Path.home() / ".local" / "share" / "whispy" / "recordings"
RECORDING_TTL_HOURS = 12


def recording_path(record_id: str) -> Path:
    """Return the canonical WAV path for a given record id."""
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    return RECORDINGS_DIR / f"{record_id}.wav"


def cleanup_old_recordings(store) -> int:
    """
    Delete WAV files older than RECORDING_TTL_HOURS and clear their DB paths.
    Returns the number of files deleted.
    """
    if not RECORDINGS_DIR.exists():
        return 0

    cutoff = time.time() - RECORDING_TTL_HOURS * 3600
    deleted = 0

    for wav in RECORDINGS_DIR.glob("*.wav"):
        try:
            if wav.stat().st_mtime < cutoff:
                store.clear_audio_path(str(wav))
                wav.unlink()
                deleted += 1
                log.debug("Deleted old recording: %s", wav.name)
        except Exception as e:
            log.warning("Failed to delete %s: %s", wav, e)

    if deleted:
        log.info("Cleaned up %d recording(s) older than %dh", deleted, RECORDING_TTL_HOURS)

    return deleted
