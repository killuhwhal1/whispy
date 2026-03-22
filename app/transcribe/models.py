"""
Data models for transcription results.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TranscriptionResult:
    text: str
    backend: str
    model: str
    duration_seconds: float = 0.0
    language: str = "en"
    segments: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "backend": self.backend,
            "model": self.model,
            "duration_seconds": self.duration_seconds,
            "language": self.language,
            "segments": self.segments,
        }
