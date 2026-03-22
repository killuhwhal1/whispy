
---

## `02-audio-capture.md`

```md
# Audio Capture Component

## Purpose

The Audio Capture component records microphone input from the user's system and prepares it for transcription.

It must be reliable, low-friction, and simple to control.

## Goals

This component should:

- detect available input devices
- let the app use a default microphone automatically
- support choosing a specific microphone
- start and stop cleanly
- buffer audio safely
- produce audio in a format suitable for transcription

## Recommended Stack

- `sounddevice` for capture
- `numpy` for audio buffers
- optional `wave` or `soundfile` for saving temp audio
- optional Silero VAD for chunking support

## Audio Requirements

A reasonable baseline configuration:

- mono audio
- 16 kHz sample rate
- 16-bit PCM or float converted appropriately
- low-latency chunk handling

This is enough for most speech-to-text pipelines.

## Key Design Decision

The user controls when recording ends.

That means:
- silence should not automatically stop recording
- the app must continue listening during pauses
- VAD can be used internally, but only for chunking or cleanup

## Responsibilities

### 1. Device Discovery
The component should list available microphones and identify:
- default input device
- device names
- channels supported
- sample rates if available

### 2. Recording Control
The component should expose methods like:
- `start()`
- `stop()`
- `cancel()`
- `get_audio_data()`

### 3. Buffer Management
During recording, audio data should be appended to an in-memory buffer.

The implementation should avoid:
- blocking the UI
- losing chunks
- growing unbounded for very long sessions without warning

### 4. Optional Temp File Export
The component may save recorded audio to a temporary WAV file before transcription if that simplifies backend integration.

## Suggested Interface

```python
class AudioRecorder:
    def start(self) -> None:
        pass

    def stop(self) -> bytes:
        pass

    def cancel(self) -> None:
        pass

    def list_devices(self) -> list[dict]:
        pass
