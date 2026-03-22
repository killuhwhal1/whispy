"""
Custom Textual widgets for whispy.
"""

from __future__ import annotations

from datetime import datetime

from rich.text import Text
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView, Static

from app.core.state import AppStatus


STATUS_STYLES = {
    AppStatus.IDLE: "dim",
    AppStatus.RECORDING: "bold red",
    AppStatus.TRANSCRIBING: "bold yellow",
    AppStatus.COMPLETED: "bold green",
    AppStatus.ERROR: "bold red",
}


class MicIndicator(Static):
    """
    A circle that shows microphone / recording state.

      idle      →  ○  dim grey
      no_mic    →  ●  yellow
      recording →  ●  red, throbbing (color cycles bright→dim→bright)
    """

    DEFAULT_CSS = """
    MicIndicator {
        width: 5;
        height: 3;
        content-align: center middle;
        text-style: bold;
    }
    """

    # "idle" | "no_mic" | "recording"
    mic_state: reactive[str] = reactive("idle")
    # Throb phase 0-7, drives color brightness when recording
    _phase: reactive[int] = reactive(0)

    # Smooth red throb: bright → dim → bright across 8 steps
    _THROB = [
        "#ff2222", "#dd1111", "#bb0000", "#880000",
        "#880000", "#bb0000", "#dd1111", "#ff2222",
    ]

    def render(self) -> Text:
        t = Text()
        if self.mic_state == "idle":
            t.append("○", style="dim white")
        elif self.mic_state == "no_mic":
            t.append("●", style="bold yellow")
        else:  # recording
            color = self._THROB[self._phase % len(self._THROB)]
            t.append("●", style=f"bold {color}")
        return t

    def watch_mic_state(self, state: str) -> None:
        if state == "recording":
            self._timer = self.set_interval(0.12, self._tick_throb)
        else:
            if hasattr(self, "_timer"):
                self._timer.stop()
            self._phase = 0

    def _tick_throb(self) -> None:
        self._phase = (self._phase + 1) % len(self._THROB)


class StatusBar(Static):
    """Text status line: state label, timer, backend, mic name, messages."""

    status: reactive[AppStatus] = reactive(AppStatus.IDLE)
    elapsed: reactive[float] = reactive(0.0)
    backend_name: reactive[str] = reactive("Local Whisper")
    mic_name: reactive[str] = reactive("Default")
    message: reactive[str] = reactive("")

    def render(self) -> Text:
        style = STATUS_STYLES.get(self.status, "")

        if self.status == AppStatus.RECORDING:
            mins = int(self.elapsed) // 60
            secs = int(self.elapsed) % 60
            timer_str = f"  {mins:02d}:{secs:02d}"
        else:
            timer_str = ""

        msg_str = f"  — {self.message}" if self.message else ""

        t = Text()
        t.append("Status: ", style="bold")
        t.append(f"{self.status.value}{timer_str}", style=style)
        t.append(f"   Backend: {self.backend_name}   Mic: {self.mic_name}", style="dim")
        t.append(msg_str, style="italic cyan")
        return t


class TranscriptPanel(Static):
    """Displays the latest transcript text."""

    transcript: reactive[str] = reactive("")
    copied: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    TranscriptPanel {
        border: round $accent;
        padding: 1 2;
        height: 1fr;
        overflow-y: auto;
    }
    """

    def render(self) -> Text:
        t = Text()
        t.append("Latest Transcript\n", style="bold underline")
        if self.transcript:
            t.append(self.transcript)
            if self.copied:
                t.append("\n\n[Copied to clipboard]", style="dim green")
        else:
            t.append("(nothing yet)", style="dim")
        return t


class HistoryList(Widget):
    """Shows recent transcript history as a scrollable list."""

    DEFAULT_CSS = """
    HistoryList {
        border: round $accent;
        padding: 0 1;
        height: 1fr;
        overflow-y: auto;
    }
    HistoryList Label {
        color: $text;
    }
    """

    # Parallel list of record IDs matching ListView order
    _record_ids: list[str] = []

    def compose(self) -> ComposeResult:
        yield Label("History", id="history-title")
        yield ListView(id="history-listview")

    def update_items(self, records: list[dict]) -> None:
        lv: ListView = self.query_one("#history-listview", ListView)
        lv.clear()
        self._record_ids = []
        for rec in records:
            ts = rec.get("created_at", "")
            try:
                dt = datetime.fromisoformat(ts)
                ts_short = dt.strftime("%m/%d %H:%M")
            except Exception:
                ts_short = ts[:16]
            preview = rec.get("text", "")[:60].replace("\n", " ")
            # No ID on ListItem — avoids DuplicateIds on refresh
            lv.append(ListItem(Label(f"{ts_short}  {preview}")))
            self._record_ids.append(rec["id"])

    def get_selected_id(self) -> str | None:
        lv: ListView = self.query_one("#history-listview", ListView)
        idx = lv.index
        if idx is not None and 0 <= idx < len(self._record_ids):
            return self._record_ids[idx]
        return None
