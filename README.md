# OpenAI backend (fast, ~1-3s)
  export OPENAI_API_KEY=sk-...                                                                                                                              
  python3 -m app.main --backend openai
                                                                                                                                                            
  # Local backend (slow but free)                                                                                                                           
  python3 -m app.main --backend local
                                                                                                                                                            
  # No arg = whatever's in config.toml (defaults to local)                                                                                                  
  python3 -m app.main
                                                                                                                                                            
  The --backend flag overrides the config file without modifying it, so you can switch on the fly. The OpenAI key is read from the environment only — never 
  stored anywhere.


---

Initial Milestone Plan
Milestone 1: Working local prototype

start/stop recording

save audio in memory or temp file

transcribe locally

show result in TUI

copy final transcript to clipboard

Milestone 2: Better UX

transcript history

retry transcription

delete history items

configurable hotkeys

device selection

Milestone 3: Optional advanced features

API fallback

partial/live transcript updates

export to markdown/txt/json

session tags

search history

Non-Goals for v1

These are intentionally out of scope for the first version:

direct insertion into every focused text field

browser extension support

speaker diarization

real-time multi-user streaming

advanced editing inside the app

mobile support

Definition of Success

The project is successful if the user can:

open the app

press one key to record

press one key to stop

see a clean transcript

have it copied automatically

trust that the app will not cut them off mid-thought


---

Core States

The UI should reflect these application states:

idle

recording

transcribing

completed

error

Each state should update:

status line

button/key labels

enabled actions

visual emphasis

Keybindings

Suggested defaults:

r → start/stop recording

s → stop recording

c → copy latest transcript

e → export latest transcript

h → open history

/ → search history

d → delete selected history entry

p → pin/favorite a transcript

q → quit

? → help



---


Required Widgets
Status Panel

Shows:

current state

backend

selected microphone

timer

current model

Transcript Panel

Shows:

live partial transcript if supported

final transcript after completion

scrollable text for long results

History List

Shows:

timestamp

preview text

backend used

tags or status markers

Footer Help Bar

Shows active hotkeys and actions.

Event Flow
Start Recording

User presses r.

UI dispatches start_recording.

Status changes to recording.

Timer starts.

Transcript panel clears or indicates new session.

Stop Recording

User presses r or s.

UI dispatches stop_recording.

Status changes to transcribing.

Timer stops.

Transcript panel shows progress message.

Transcription Complete

Transcription engine returns final text.

Latest transcript updates.

Status changes to completed.

Clipboard copy runs if enabled.

Transcript is saved to history.

Design Principles

keep the UI calm and uncluttered

minimize nested menus

avoid modal-heavy flows

make primary actions obvious

support mouse only as a bonus, not a requirement

Error Handling

The TUI should clearly show errors such as:

no microphone found

permission denied

model missing

transcription failed

API unavailable

Errors should be visible in a dedicated status area and optionally logged.

Files to Create

Suggested files:

app/tui/app.py

app/tui/screens.py

app/tui/widgets.py

app/tui/actions.py

Definition of Done

This component is complete when:

the app launches into a usable terminal screen

the user can start and stop recording from the TUI

the latest transcript is displayed clearly

the history list updates after each completed session

common errors are visible and understandable



---


Internal Flow
Start

open audio stream

clear prior buffer

mark state as recording

begin collecting chunks

During Recording

receive audio frames in callback

append to buffer

optionally compute signal level for UI meter

Stop

close stream

combine buffered chunks

normalize/convert if needed

return audio payload for transcription

Optional Features
Audio Level Meter

A basic volume indicator can improve UX.

Silence Markers

VAD can mark probable pauses in speech, useful for debugging or future partial transcription support.

Noise Handling

Do not overcomplicate v1 with advanced DSP. Basic clean recording is enough.

Failure Cases

Handle:

no input device

stream open failure

permission denied

disconnected microphone

invalid sample rate or backend error

Files to Create

Suggested files:

app/audio/recorder.py

app/audio/devices.py

app/audio/vad.py

Implementation Notes

run recording in a way that does not block the TUI event loop

use thread-safe communication between recorder and app state

keep the interface small and easy to replace later

Definition of Done

This component is complete when:

the app can detect a microphone

the user can record audio successfully

the recording can be stopped cleanly

the resulting audio can be passed to the transcription engine

the app does not end the session early due to pauses in speech


---


Local Backend Requirements

The local backend should:

lazily load the model at startup or on first use

keep the model in memory if feasible

return transcript text

surface errors clearly

avoid reloading the model unnecessarily

API Backend Requirements

The API backend should:

be optional

use an API key from environment or config

upload audio safely

return transcript text in the same normalized structure as local mode

report network and auth errors clearly

Session Behavior
Important rule

The transcription engine should not decide when recording ends.

It only processes the audio once the app stops recording.

For future partial transcript mode

If streaming or chunk-based transcription is added later:

partial output should be marked as provisional

final text should replace or merge partial text cleanly

Suggested Result Object
{
  "id": "uuid",
  "text": "Final transcript text here.",
  "backend": "local",
  "model": "small.en",
  "language": "en",
  "created_at": "2026-03-21T12:00:00Z",
  "duration_seconds": 18.2,
  "segments": [
    {
      "start": 0.0,
      "end": 4.3,
      "text": "Final transcript text here."
    }
  ],
  "error": None
}
Error Cases

Handle these clearly:

model not installed

unsupported model name

invalid audio input

local inference failure

API timeout

missing API key

rate limit or billing error

Performance Concerns

For v1:

prioritize reliability over streaming complexity

keep the code path simple

avoid unnecessary audio transformations

optionally cache the model between transcriptions

Files to Create

Suggested files:

app/transcribe/engine.py

app/transcribe/local_whisper.py

app/transcribe/openai_backend.py

app/transcribe/models.py

Definition of Done

This component is complete when:

recorded audio can be transcribed locally

final transcript text is returned in a standard result shape

optional API mode works behind a config toggle

transcription failures are recoverable and clearly reported


---


You may later add:

favorite flag

session title

error status

language

Responsibilities
1. Save Transcript

After a successful transcription, save the final result immediately.

2. Load Recent History

When the app starts, load recent entries for display in the history panel.

3. Search

Allow searching by:

transcript text

tags

date range later if needed

4. Delete

Allow deleting one or more entries from history.

5. Update Metadata

Examples:

mark item as copied

tag an item

mark favorite

Suggested Interface
class TranscriptStore:
    def save(self, record: dict) -> None:
        pass

    def list_recent(self, limit: int = 50) -> list[dict]:
        pass

    def search(self, query: str) -> list[dict]:
        pass

    def delete(self, transcript_id: str) -> None:
        pass
UX Expectations

The history system should feel:

fast

searchable

easy to inspect

safe to delete from

A history row in the TUI should show:

timestamp

short text preview

backend

maybe duration

Data Retention

For v1:

keep everything locally by default

do not auto-delete without user choice

Optional later settings:

delete after N days

keep only last N items

store raw audio or not

Privacy Considerations

Because transcripts may contain sensitive spoken content:

all history should remain local unless the user explicitly exports it

the app should avoid sending history to remote services automatically

Files to Create

Suggested files:

app/storage/db.py

app/storage/history.py

app/storage/settings.py

Definition of Done

This component is complete when:

every finished transcript is saved

the user can browse recent transcripts

the user can search history

the user can delete a transcript

the database remains small, stable, and easy to inspect


---


Export Format Suggestions
TXT

Plain transcript only.

Markdown

Useful for notes or journaling.

Example:

# Transcript

- Date: 2026-03-21 12:00
- Backend: local
- Model: small.en

## Text

This is the transcribed text.
JSON

Best for programmatic reuse.

Clipboard UX Rules

auto-copy should be configurable

copying should never silently fail without feedback

the user should always know what was copied

Error Cases

Handle:

clipboard backend unavailable

export path invalid

permission denied

unsupported export format

Files to Create

Suggested files:

app/integrations/clipboard.py

app/integrations/export.py

Definition of Done

This component is complete when:

the latest transcript can be copied

auto-copy works after transcription

history items can be copied

transcripts can be exported in at least txt and md format


---


Hotkeys

Suggested default hotkeys:

r start/stop recording

s stop recording

c copy latest transcript

e export latest transcript

h open history

/ search history

q quit

? help

These can remain static in v1, but the design should leave room for customization later.

Packaging Goals

The app should be easy to run in development and reasonably easy to distribute later.

Development Run

Support:

python -m app.main
Environment Setup

Provide:

requirements.txt or pyproject.toml

clear install instructions

model download/setup instructions

Packaging Later

Possible targets:

pip-installable package

standalone binary via PyInstaller

AppImage later if desired

Logging

Add a lightweight log file for debugging:

app start

device selection

recording start/stop

transcription success/failure

clipboard success/failure

Keep logs local.

Documentation to Include

The project should eventually include:

installation instructions

microphone troubleshooting

backend setup

model selection guidance

API key setup for optional cloud mode

Files to Create

Suggested files:

app/core/config.py

app/core/state.py

app/core/events.py

app/integrations/logging.py

Definition of Done

This component is complete when:

the app can read settings from a config file

hotkeys are documented and wired into the TUI

the app can be run consistently in development

the project is structured for later packaging and distribution
