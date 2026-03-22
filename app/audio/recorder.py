"""
Microphone recorder using sounddevice.

Records until stop() is called — does NOT auto-stop on silence.
Audio is buffered in memory and returned as raw float32 numpy array.
"""

from __future__ import annotations

import io
import threading
import wave
from typing import Optional

import numpy as np


class AudioRecorder:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        device: Optional[int] = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device  # None = system default

        self._chunks: list[np.ndarray] = []
        self._lock = threading.Lock()
        self._stream: Optional[sd.InputStream] = None
        self._recording = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self) -> None:
        if self._recording:
            return

        import sounddevice as sd  # lazy import — requires PortAudio at runtime

        self._chunks = []
        self._recording = True

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            device=self.device,
            callback=self._audio_callback,
            # blocksize gives ~100ms chunks which is comfortable overhead
            blocksize=int(self.sample_rate * 0.1),
        )
        self._stream.start()

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time,
        status,
    ) -> None:
        with self._lock:
            self._chunks.append(indata.copy())

    def stop(self) -> np.ndarray:
        """Stop recording and return the full audio as a float32 numpy array."""
        if not self._recording:
            return np.array([], dtype=np.float32)

        self._recording = False

        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if not self._chunks:
                return np.array([], dtype=np.float32)
            audio = np.concatenate(self._chunks, axis=0)

        # Return as 1-D float32 (mono)
        if audio.ndim > 1:
            audio = audio[:, 0]
        return audio.astype(np.float32)

    def cancel(self) -> None:
        """Stop recording and discard all audio."""
        if not self._recording:
            return
        self._recording = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            self._chunks = []

    def stop_to_wav_bytes(self) -> bytes:
        """Stop and return the audio as WAV bytes suitable for writing to a file."""
        audio = self.stop()
        return audio_to_wav_bytes(audio, self.sample_rate)

    def list_devices(self) -> list[dict]:
        from app.audio.devices import list_devices
        return list_devices()


def audio_to_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
    """Convert a float32 numpy array to WAV-format bytes (16-bit PCM)."""
    pcm = (audio * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()


def save_audio_to_file(audio: np.ndarray, sample_rate: int, path: str) -> None:
    """Write a float32 numpy array to a WAV file at the given path."""
    import pathlib
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    wav_bytes = audio_to_wav_bytes(audio, sample_rate)
    pathlib.Path(path).write_bytes(wav_bytes)
