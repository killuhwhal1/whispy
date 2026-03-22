"""
Transcription engine dispatcher.

Selects the appropriate backend (local or cloud) based on configuration
and provides a unified transcribe() interface to the rest of the app.
"""

from __future__ import annotations

import numpy as np

from app.core.config import AppConfig
from app.transcribe.models import TranscriptionResult


class TranscriptionEngine:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._local_backend = None
        self._openai_backend = None

    def _get_local_backend(self):
        if self._local_backend is None:
            from app.transcribe.local_whisper import LocalWhisperBackend
            self._local_backend = LocalWhisperBackend(
                model_name=self.config.transcription.model,
                language=self.config.transcription.language,
            )
        return self._local_backend

    def _get_openai_backend(self):
        if self._openai_backend is None:
            from app.transcribe.openai_backend import OpenAIBackend
            self._openai_backend = OpenAIBackend(
                model=self.config.transcription.model
                if self.config.transcription.model != "base"
                else "whisper-1",
            )
        return self._openai_backend

    def transcribe(
        self,
        audio: np.ndarray | None = None,
        audio_path: str | None = None,
        sample_rate: int = 16000,
    ) -> TranscriptionResult:
        backend = self.config.transcription.backend

        if backend == "local":
            return self._get_local_backend().transcribe(
                audio=audio,
                audio_path=audio_path,
                sample_rate=sample_rate,
            )
        elif backend == "openai":
            return self._get_openai_backend().transcribe(
                audio=audio,
                audio_path=audio_path,
                sample_rate=sample_rate,
            )
        else:
            raise ValueError(f"Unsupported backend '{backend}'. Choose 'local' or 'openai'.")
