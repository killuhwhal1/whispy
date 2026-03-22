"""
Main Textual application for whispy.

Layout:
  Header
  [MicIndicator | StatusBar]
  [TranscriptPanel | HistoryList]
  Footer
"""

from __future__ import annotations

import logging
import threading
import time
import uuid

import numpy as np
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.timer import Timer
from textual.widgets import Footer, Header

from app.audio.recorder import AudioRecorder, save_audio_to_file
from app.core.config import AppConfig
from app.core.events import (
    RecordingStarted,
    RecordingStopped,
    TranscriptionComplete,
    TranscriptionError,
)
from app.core.state import AppStatus
from app.integrations.cleanup import cleanup_old_recordings, recording_path
from app.integrations.clipboard import copy_text
from app.storage.db import init_db
from app.storage.history import HistoryStore
from app.transcribe.engine import TranscriptionEngine
from app.tui.widgets import HistoryList, MicIndicator, StatusBar, TranscriptPanel

log = logging.getLogger(__name__)


class WhispyApp(App):
    """The main whispy TUI application."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #header-row {
        layout: horizontal;
        height: 3;
        background: $surface;
        border-bottom: solid $accent;
    }

    StatusBar {
        height: 3;
        padding: 1 1;
        width: 1fr;
        content-align: left middle;
    }

    #content-row {
        layout: horizontal;
        height: 1fr;
    }

    TranscriptPanel {
        width: 2fr;
    }

    HistoryList {
        width: 1fr;
    }
    """

    BINDINGS = [
        Binding("r", "toggle_recording", "Record/Stop", show=True, priority=True),
        Binding("s", "stop_recording", "Stop", show=False, priority=True),
        Binding("c", "copy_latest", "Copy", show=True, priority=True),
        Binding("t", "retry_transcription", "Retry", show=True, priority=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config
        self._status = AppStatus.IDLE
        self._latest_transcript: str = ""
        self._latest_record_id: str | None = None
        self._copied = False
        self._record_start_time: float = 0.0
        self._timer: Timer | None = None
        self._recorder_active: bool = False
        # Path of the most recently saved audio file (for retry)
        self._last_audio_path: str | None = None

        # Audio
        device_index = None
        if config.audio.device != "default":
            try:
                device_index = int(config.audio.device)
            except ValueError:
                pass
        self._recorder = AudioRecorder(
            sample_rate=config.audio.sample_rate,
            channels=config.audio.channels,
            device=device_index,
        )

        # Transcription engine (model loads lazily on first use)
        self._engine = TranscriptionEngine(config)

        # Storage
        conn = init_db(config.history.db_path)
        self._store = HistoryStore(conn)

    # ------------------------------------------------------------------ compose

    def compose(self) -> ComposeResult:
        from textual.containers import Container, Horizontal
        yield Header(show_clock=False)
        with Horizontal(id="header-row"):
            yield MicIndicator(id="mic-indicator")
            yield StatusBar(id="status-bar")
        with Container(id="content-row"):
            yield TranscriptPanel(id="transcript-panel")
            yield HistoryList(id="history-list")
        yield Footer()

    # ------------------------------------------------------------------ on_mount

    def on_mount(self) -> None:
        sb = self.query_one("#status-bar", StatusBar)
        backend = self.config.transcription.backend
        model = self.config.transcription.model
        sb.backend_name = f"OpenAI ({model})" if backend == "openai" else f"Local ({model})"
        sb.mic_name = (
            self.config.audio.device if self.config.audio.device != "default" else "Default"
        )
        # Clean up recordings older than 12h, then load history
        threading.Thread(target=self._startup_cleanup, daemon=True).start()

    def _startup_cleanup(self) -> None:
        n = cleanup_old_recordings(self._store)
        if n:
            log.info("Startup: removed %d expired recording(s)", n)
        self.call_from_thread(self._refresh_history)

    # ------------------------------------------------------------------ actions

    def action_toggle_recording(self) -> None:
        if self._status == AppStatus.RECORDING:
            self._do_stop_and_transcribe()
        elif self._status in (AppStatus.IDLE, AppStatus.COMPLETED, AppStatus.ERROR):
            self._do_start_recording()

    def action_stop_recording(self) -> None:
        if self._status == AppStatus.RECORDING:
            self._do_stop_and_transcribe()

    def action_copy_latest(self) -> None:
        if self._latest_transcript:
            ok = copy_text(self._latest_transcript)
            if ok and self._latest_record_id:
                self._store.mark_copied(self._latest_record_id)
            self.query_one("#transcript-panel", TranscriptPanel).copied = ok
            self.query_one("#status-bar", StatusBar).message = "Copied!" if ok else "Copy failed"
        else:
            self.query_one("#status-bar", StatusBar).message = "Nothing to copy"

    def action_retry_transcription(self) -> None:
        """Re-transcribe the selected history item using its saved audio file."""
        if self._status == AppStatus.RECORDING:
            return

        hist = self.query_one("#history-list", HistoryList)
        record_id = hist.get_selected_id()

        audio_path: str | None = None
        if record_id:
            rec = self._store.get_by_id(record_id)
            audio_path = rec.get("audio_path") if rec else None

        # Fall back to the most recently saved audio if nothing is selected
        if not audio_path:
            audio_path = self._last_audio_path

        if not audio_path:
            self.query_one("#status-bar", StatusBar).message = "No audio file to retry"
            return

        import pathlib
        if not pathlib.Path(audio_path).exists():
            self.query_one("#status-bar", StatusBar).message = "Audio file no longer exists (expired)"
            return

        self._set_status(AppStatus.TRANSCRIBING)
        self.query_one("#status-bar", StatusBar).message = f"Retrying: {pathlib.Path(audio_path).name}"
        threading.Thread(
            target=self._transcribe_thread,
            args=(None, audio_path),
            daemon=True,
        ).start()

    # ------------------------------------------------------------------ recording

    def _do_start_recording(self) -> None:
        mic = self.query_one("#mic-indicator", MicIndicator)
        sb = self.query_one("#status-bar", StatusBar)

        try:
            self._recorder.start()
            self._recorder_active = True
        except Exception as e:
            log.warning("Recorder unavailable (%s)", e)
            self._recorder_active = False
            mic.mic_state = "no_mic"
            sb.message = "No mic — audio disabled"

        self._record_start_time = time.monotonic()
        self._set_status(AppStatus.RECORDING)

        if self._recorder_active:
            mic.mic_state = "recording"

        self.query_one("#transcript-panel", TranscriptPanel).copied = False
        self._timer = self.set_interval(1.0, self._tick_timer)

        self.post_message(RecordingStarted())
        log.info("Recording started (audio=%s)", self._recorder_active)

    def _do_stop_and_transcribe(self) -> None:
        if self._timer:
            self._timer.stop()
            self._timer = None

        self.query_one("#mic-indicator", MicIndicator).mic_state = "idle"
        self._set_status(AppStatus.TRANSCRIBING)
        self.post_message(RecordingStopped())

        audio = np.array([], dtype=np.float32)
        if self._recorder_active:
            try:
                audio = self._recorder.stop()
            except Exception as e:
                log.warning("Failed to stop recorder cleanly: %s", e)
        self._recorder_active = False

        log.info("Recording stopped, audio samples: %d", len(audio))

        # Save audio to file before handing off to transcription thread
        audio_path: str | None = None
        if len(audio) > 0:
            rec_id = str(uuid.uuid4())
            path = recording_path(rec_id)
            try:
                save_audio_to_file(audio, self.config.audio.sample_rate, str(path))
                audio_path = str(path)
                self._last_audio_path = audio_path
                log.info("Saved recording to %s", audio_path)
            except Exception as e:
                log.warning("Could not save audio file: %s", e)

        threading.Thread(
            target=self._transcribe_thread,
            args=(audio, audio_path),
            daemon=True,
        ).start()

    def _transcribe_thread(
        self,
        audio: np.ndarray | None,
        audio_path: str | None = None,
    ) -> None:
        try:
            result = self._engine.transcribe(
                audio=audio,
                audio_path=audio_path,
                sample_rate=self.config.audio.sample_rate,
            )
        except Exception as e:
            import traceback
            full_error = traceback.format_exc()
            log.error("Transcription failed:\n%s", full_error)
            self.call_from_thread(
                self.post_message,
                TranscriptionError(error=f"{type(e).__name__}: {e}\n\n{full_error}"),
            )
            return

        record_id = self._store.save(result, copied=False, audio_path=audio_path)
        self.call_from_thread(
            self.post_message,
            TranscriptionComplete(
                text=result.text,
                record_id=record_id,
                duration=result.duration_seconds,
            ),
        )

    # ------------------------------------------------------------------ event handlers

    def on_transcription_complete(self, event: TranscriptionComplete) -> None:
        self._latest_transcript = event.text
        self._latest_record_id = event.record_id

        panel = self.query_one("#transcript-panel", TranscriptPanel)
        panel.transcript = event.text

        self._set_status(AppStatus.COMPLETED)
        sb = self.query_one("#status-bar", StatusBar)
        sb.message = f"Done in {event.duration:.1f}s"

        if self.config.output.auto_copy and event.text:
            ok = copy_text(event.text)
            if ok:
                self._store.mark_copied(event.record_id)
                panel.copied = True
                sb.message += "  • Copied!"

        self._refresh_history()

    def on_transcription_error(self, event: TranscriptionError) -> None:
        self._set_status(AppStatus.ERROR)
        self.query_one("#status-bar", StatusBar).message = "Transcription failed — see below"
        self.query_one("#transcript-panel", TranscriptPanel).transcript = f"[ERROR]\n{event.error}"
        log.error("Transcription error: %s", event.error)

    # ------------------------------------------------------------------ helpers

    def _set_status(self, status: AppStatus) -> None:
        self._status = status
        sb = self.query_one("#status-bar", StatusBar)
        sb.status = status
        if status != AppStatus.RECORDING:
            sb.elapsed = 0.0

    def _tick_timer(self) -> None:
        elapsed = time.monotonic() - self._record_start_time
        self.query_one("#status-bar", StatusBar).elapsed = elapsed

    def _refresh_history(self) -> None:
        records = self._store.get_recent(limit=self.config.history.max_items)
        self.query_one("#history-list", HistoryList).update_items(records)
