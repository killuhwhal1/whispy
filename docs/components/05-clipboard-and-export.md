
---

## `05-clipboard-and-export.md`

```md
# Clipboard and Export Component

## Purpose

This component makes transcripts immediately useful outside the app.

The fastest path to usability is:
- show transcript
- copy transcript
- paste anywhere

## Goals

This component should:

- auto-copy the final transcript after successful transcription
- let the user manually copy the latest transcript
- let the user copy a history item
- export transcripts to files

## Recommended Stack

- `pyperclip` or a native clipboard helper
- Python standard library for file export

## Core Features

### 1. Auto-Copy
After a final transcript is produced:
- copy it to clipboard automatically if enabled
- show a status message such as `Copied to clipboard`

### 2. Manual Copy
The user should be able to:
- copy latest transcript
- copy selected history item

### 3. Export
Allow exporting as:
- `.txt`
- `.md`
- `.json`

## Suggested Interface

```python
def copy_text(text: str) -> None:
    pass

def export_transcript(record: dict, path: str, format: str) -> None:
    pass
