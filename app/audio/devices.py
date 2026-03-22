"""
Audio device discovery helpers.
"""

from __future__ import annotations


def list_devices() -> list[dict]:
    """
    Return a list of available input audio devices.
    Each dict has: index, name, channels, sample_rate, is_default.
    """
    try:
        import sounddevice as sd  # noqa: F401 — lazy, requires PortAudio

        devices = []
        default_input = sd.default.device[0]
        for idx, dev in enumerate(sd.query_devices()):
            if dev["max_input_channels"] > 0:
                devices.append(
                    {
                        "index": idx,
                        "name": dev["name"],
                        "channels": dev["max_input_channels"],
                        "sample_rate": int(dev["default_samplerate"]),
                        "is_default": idx == default_input,
                    }
                )
        return devices
    except Exception as e:
        return [{"index": -1, "name": f"Error listing devices: {e}", "channels": 1, "sample_rate": 16000, "is_default": True}]


def get_default_device_index() -> int | None:
    """Return the index of the default input device, or None."""
    try:
        import sounddevice as sd
        return sd.default.device[0]
    except Exception:
        return None
