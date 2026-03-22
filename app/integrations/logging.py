"""
Logging setup for whispy.
Writes to ~/.local/share/whispy/whispy.log at DEBUG level.
The TUI captures stderr so we route to file only.
"""

import logging
import sys
from pathlib import Path


LOG_PATH = Path.home() / ".local" / "share" / "whispy" / "whispy.log"


def setup_logging(level: int = logging.DEBUG) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("faster_whisper").setLevel(logging.WARNING)
    logging.getLogger("sounddevice").setLevel(logging.WARNING)
