"""
App state definitions shared across all components.
"""

from enum import Enum, auto


class AppStatus(Enum):
    IDLE = "Idle"
    RECORDING = "Recording"
    TRANSCRIBING = "Transcribing"
    COMPLETED = "Completed"
    ERROR = "Error"
