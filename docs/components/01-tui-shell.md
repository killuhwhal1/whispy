
---

## `01-tui-shell.md`

```md
# TUI Shell Component

## Purpose

The TUI Shell is the visible interface of the application. It is responsible for presenting controls, status, transcripts, and history in a clean terminal-based layout.

This component should feel simple, fast, and keyboard-first.

## Goals

The TUI should allow the user to:

- see whether the app is idle, recording, transcribing, or failed
- start recording
- stop recording
- view the latest transcript
- browse past transcripts
- copy or export transcripts
- change simple settings

## Recommended Stack

- **Framework:** Textual
- **Language:** Python

Textual is a good fit because it supports:
- layout composition
- widgets
- event-driven behavior
- keyboard bindings
- app-like terminal interfaces

## Main Views

### 1. Main Screen
This is the default screen shown at startup.

It should include:
- app title
- current status
- recording timer
- latest transcript panel
- history list
- footer with keybindings

### 2. History Screen
A dedicated view for browsing previous transcripts.

It should support:
- selecting an item
- viewing full text
- copying selected transcript
- deleting an item
- searching history

### 3. Settings Screen
A simple settings page for:
- transcription backend
- model choice
- auto-copy toggle
- microphone selection
- export preferences

## Suggested Layout

```text
+------------------------------------------------------+
| Voice Dictation TUI                                  |
+------------------------------------------------------+
| Status: Idle                                         |
| Backend: Local Whisper                               |
| Mic: Default                                         |
| Timer: 00:00                                         |
+--------------------------+---------------------------+
| Latest Transcript        | History                   |
|                          |                           |
| [transcript text here]   | - item 1                 |
|                          | - item 2                 |
|                          | - item 3                 |
+--------------------------+---------------------------+
| r Start/Stop | c Copy | e Export | h History | q Quit |
+------------------------------------------------------+
