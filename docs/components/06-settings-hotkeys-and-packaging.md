
---

## `06-settings-hotkeys-and-packaging.md`

```md
# Settings, Hotkeys, and Packaging Component

## Purpose

This component covers operational polish:
- user preferences
- keyboard shortcuts
- app startup behavior
- packaging and distribution

These are not the core transcription features, but they matter a lot for daily usability.

## Goals

This component should:

- let users configure behavior
- make controls easy to remember
- support installation and launch on Ubuntu/Linux
- prepare the project for repeatable use

## Settings to Support

### Backend Settings
- local backend enabled
- API backend enabled
- default backend
- model selection

### Recording Settings
- microphone device
- sample rate
- save raw audio toggle
- optional max recording length warning

### Output Settings
- auto-copy enabled
- export folder
- include metadata in exports

### UI Settings
- theme later if desired
- show timestamps
- history limit

## Config Format

Use a simple local config file such as:

- TOML
- YAML
- JSON

TOML is a strong default because it is human-readable and structured without being noisy.

Example:

```toml
[transcription]
backend = "local"
model = "small.en"

[audio]
device = "default"
sample_rate = 16000

[output]
auto_copy = true
export_dir = "~/transcripts"

[history]
max_items = 500
