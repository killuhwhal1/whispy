"""
OpenAI Whisper API transcription backend.

Requires the OPENAI_API_KEY environment variable (or passed explicitly).
Audio is uploaded as a WAV file and transcribed via the whisper-1 model.
Billed at $0.006 / minute of audio.
"""

from __future__ import annotations

import io
import os
import time
from pathlib import Path

import numpy as np

from app.transcribe.models import TranscriptionResult


class OpenAIBackend:
    def __init__(self, api_key: str | None = None, model: str = "whisper-1") -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Export it before running: export OPENAI_API_KEY=sk-..."
            )
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def transcribe(
        self,
        audio: np.ndarray | None = None,
        audio_path: str | None = None,
        sample_rate: int = 16000,
    ) -> TranscriptionResult:
        if audio_path is None and audio is None:
            raise ValueError("Either audio or audio_path must be provided")

        client = self._get_client()
        start = time.time()

        if audio_path is not None:
            with open(audio_path, "rb") as f:
                response = client.audio.transcriptions.create(
                    model=self.model,
                    file=(Path(audio_path).name, f, "audio/wav"),
                    response_format="verbose_json",
                )
        else:
            # No file on disk — build WAV bytes and send in-memory
            from app.audio.recorder import audio_to_wav_bytes
            import io
            wav_bytes = audio_to_wav_bytes(audio, sample_rate)
            response = client.audio.transcriptions.create(
                model=self.model,
                file=("audio.wav", io.BytesIO(wav_bytes), "audio/wav"),
                response_format="verbose_json",
            )

        duration = time.time() - start
        text = (response.text or "").strip()

        segments = []
        if hasattr(response, "segments") and response.segments:
            for seg in response.segments:
                segments.append({"start": seg.start, "end": seg.end, "text": seg.text})

        detected_language = getattr(response, "language", "en") or "en"

        return TranscriptionResult(
            text=text,
            backend="openai",
            model=self.model,
            duration_seconds=duration,
            language=detected_language,
            segments=segments,
        )
