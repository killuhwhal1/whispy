"""
Clipboard integration for Ubuntu/Linux.

Uses subprocess to call xclip or xsel as a fallback chain.
pyperclip is tried first as it handles both X11 and Wayland detection.
"""

from __future__ import annotations

import subprocess


def copy_text(text: str) -> bool:
    """
    Copy text to the system clipboard.
    Returns True on success, False on failure.
    """
    # Try pyperclip first (handles backend selection automatically)
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    # Fallback: xclip
    try:
        proc = subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text.encode(),
            check=True,
            timeout=5,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    # Fallback: xsel
    try:
        subprocess.run(
            ["xsel", "--clipboard", "--input"],
            input=text.encode(),
            check=True,
            timeout=5,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    # Fallback: wl-copy (Wayland)
    try:
        subprocess.run(
            ["wl-copy"],
            input=text.encode(),
            check=True,
            timeout=5,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    return False
