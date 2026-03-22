"""
Configuration loader for whispy.
Reads a TOML config file (default: ~/.config/whispy/config.toml).
Falls back to sensible defaults if the file does not exist.
"""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_CONFIG_PATH = Path.home() / ".config" / "whispy" / "config.toml"


@dataclass
class TranscriptionConfig:
    backend: str = "local"
    model: str = "base"
    language: str = "en"


@dataclass
class AudioConfig:
    device: str = "default"
    sample_rate: int = 16000
    channels: int = 1
    save_audio: bool = False


@dataclass
class OutputConfig:
    auto_copy: bool = True
    export_dir: str = "~/transcripts"


@dataclass
class HistoryConfig:
    max_items: int = 500
    db_path: str = "~/.local/share/whispy/transcripts.db"


@dataclass
class AppConfig:
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    history: HistoryConfig = field(default_factory=HistoryConfig)


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or DEFAULT_CONFIG_PATH

    if not config_path.exists():
        return AppConfig()

    with open(config_path, "rb") as f:
        raw = tomllib.load(f)

    cfg = AppConfig()

    if "transcription" in raw:
        t = raw["transcription"]
        cfg.transcription.backend = t.get("backend", cfg.transcription.backend)
        cfg.transcription.model = t.get("model", cfg.transcription.model)
        cfg.transcription.language = t.get("language", cfg.transcription.language)

    if "audio" in raw:
        a = raw["audio"]
        cfg.audio.device = a.get("device", cfg.audio.device)
        cfg.audio.sample_rate = a.get("sample_rate", cfg.audio.sample_rate)
        cfg.audio.channels = a.get("channels", cfg.audio.channels)
        cfg.audio.save_audio = a.get("save_audio", cfg.audio.save_audio)

    if "output" in raw:
        o = raw["output"]
        cfg.output.auto_copy = o.get("auto_copy", cfg.output.auto_copy)
        cfg.output.export_dir = o.get("export_dir", cfg.output.export_dir)

    if "history" in raw:
        h = raw["history"]
        cfg.history.max_items = h.get("max_items", cfg.history.max_items)
        cfg.history.db_path = h.get("db_path", cfg.history.db_path)

    return cfg


def write_default_config(path: Path | None = None) -> Path:
    """Write a default config file if it doesn't exist. Returns the path."""
    config_path = path or DEFAULT_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if not config_path.exists():
        config_path.write_text(
            """\
[transcription]
backend = "local"
model = "base"
language = "en"

[audio]
device = "default"
sample_rate = 16000
channels = 1
save_audio = false

[output]
auto_copy = true
export_dir = "~/transcripts"

[history]
max_items = 500
db_path = "~/.local/share/whispy/transcripts.db"
"""
        )

    return config_path
