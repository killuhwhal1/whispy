
---

## `03-transcription-engine.md`

```md
# Transcription Engine Component

## Purpose

The Transcription Engine converts recorded audio into text.

It is the core functional component of the application.

## Goals

This component should:

- accept recorded audio input
- run transcription locally by default
- optionally use a cloud API backend
- return final text reliably
- optionally support partial updates later
- expose a clean interface to the rest of the app

## Recommended Backends

### Primary backend
- `faster-whisper`

### Optional backend
- OpenAI transcription API

The local backend should be the default experience.

## Why Local-First

Local transcription provides:
- privacy
- offline use
- lower long-term cost
- reduced network dependency
- fast iteration during development

## Responsibilities

### 1. Backend Selection
The engine should be able to choose between:
- local model
- cloud API

### 2. Model Configuration
For local mode, support configurable models such as:
- tiny
- base
- small
- medium

The app should default to a practical model rather than the heaviest option.

### 3. Audio Preprocessing
If needed, convert input audio into the format required by the selected backend.

### 4. Result Formatting
Normalize the returned data into a consistent structure for the rest of the app.

## Suggested Interface

```python
class TranscriptionEngine:
    def transcribe(self, audio_path: str | None = None, audio_bytes: bytes | None = None) -> dict:
        """
        Returns:
        {
            "text": "...",
            "backend": "local",
            "model": "small",
            "duration_seconds": 12.4,
            "language": "en",
            "segments": []
        }
        """
        pass
