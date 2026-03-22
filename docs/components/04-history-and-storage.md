
---

## `04-history-and-storage.md`

```md
# History and Storage Component

## Purpose

This component stores transcripts and related metadata so the user can review past dictation sessions.

It turns the app from a one-time transcription tool into a reusable productivity utility.

## Goals

This component should:

- save completed transcripts
- store metadata such as timestamps and backend used
- allow history browsing
- support searching and deleting entries
- keep implementation simple and local

## Recommended Stack

- SQLite
- Python standard library `sqlite3` or a light wrapper

SQLite is ideal because it is:
- simple
- local
- fast enough
- easy to back up
- easy to inspect manually

## What Should Be Stored

Each transcript record should include:

- unique id
- created timestamp
- transcript text
- backend used
- model used
- duration
- copied-to-clipboard flag
- optional tags
- optional audio file path if retained

## Suggested Schema

```sql
CREATE TABLE transcripts (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    text TEXT NOT NULL,
    backend TEXT NOT NULL,
    model TEXT,
    duration_seconds REAL,
    copied INTEGER NOT NULL DEFAULT 0,
    tags TEXT,
    audio_path TEXT
);
