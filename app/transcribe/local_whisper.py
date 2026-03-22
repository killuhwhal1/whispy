"""
Local transcription backend using faster-whisper.

The model is loaded once and reused across calls to avoid reload overhead.
"""

from __future__ import annotations

import io
import tempfile
import time
import wave
from pathlib import Path
from typing import Optional

import numpy as np

from app.transcribe.models import TranscriptionResult


class LocalWhisperBackend:
    def __init__(self, model_name: str = "base", language: str = "en") -> None:
        self.model_name = model_name
        self.language = language if language != "auto" else None
        self._model = None  # lazy-loaded on first use

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            # Use int8 compute type for broad hardware compatibility
            self._model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
        return self._model

    def transcribe(
        self,
        audio: np.ndarray | None = None,
        audio_path: str | None = None,
        sample_rate: int = 16000,
    ) -> TranscriptionResult:
        model = self._load_model()

        start = time.time()

        if audio_path is not None:
            source = audio_path
        elif audio is not None:
            # faster-whisper can accept a numpy float32 array directly
            source = audio.astype(np.float32)
        else:
            raise ValueError("Either audio or audio_path must be provided")

        segments_gen, info = model.transcribe(
            source,
            language=self.language,
            beam_size=5,
            vad_filter=False,  # VAD off — do not let it trim the user's speech
        )

        segments = []
        full_text_parts = []
        for seg in segments_gen:
            segments.append({"start": seg.start, "end": seg.end, "text": seg.text})
            full_text_parts.append(seg.text)

        duration = time.time() - start
        text = " ".join(full_text_parts).strip()

        return TranscriptionResult(
            text=text,
            backend="local",
            model=self.model_name,
            duration_seconds=duration,
            language=info.language if info else self.language or "en",
            segments=segments,
        )
