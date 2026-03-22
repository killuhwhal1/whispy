"""
Custom Textual messages used to communicate between app components.
"""

from textual.message import Message


class TranscriptionComplete(Message):
    """Fired when transcription finishes successfully."""

    def __init__(self, text: str, record_id: str, duration: float) -> None:
        super().__init__()
        self.text = text
        self.record_id = record_id
        self.duration = duration


class TranscriptionError(Message):
    """Fired when transcription fails."""

    def __init__(self, error: str) -> None:
        super().__init__()
        self.error = error


class RecordingStarted(Message):
    """Fired when recording begins."""


class RecordingStopped(Message):
    """Fired when recording stops (before transcription)."""


class StatusUpdate(Message):
    """Generic status message update."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message
