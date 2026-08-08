"""Prose beside the numbers — the half of a track that resists enumeration.

`track.json` holds machine truth: bpm, key, cues, energy, feedback verdicts.
This holds what only a DJ can assert, in the shape Skills and `AGENTS.md`
already use — small typed frontmatter for filtering, free Markdown for
judgment:

    Collection/J/Jon Hopkins - Reckoning.mp3.migx/
        track.json    machine
        notes.md      human

    ---
    mood: [hypnotic, late]
    floor: peak
    avoid_after: vocal-house
    ---

    Builds for two minutes before it commits — do not mix in early or you
    lose the arc. The break at 4:35 is the exit.

## Why two files and not one more JSON field

A note already existed as `notes:` inside `track.json`, and it was a single
escaped string: no line breaks that survive reading, no structure, and
invisible next to a hundred numeric keys. Prose in a JSON string is prose you
stop writing.

The split matches how the data is *used*: frontmatter is what you filter on
(`mood: peak` narrows a pool), the body is what you reason with. Cheap machine
dispatch, rich human context, one file each.

## The rule that keeps it honest

**Frontmatter must never restate what `track.json` owns.** No `bpm:` here — it
would drift the first time a track is re-analysed, and then two files disagree
about the same track with nothing to say which wins (MG-3). `RESERVED` is
enforced on write, not documented and hoped for.

Frontmatter is parsed by a deliberately small reader: scalars and inline lists
only. migx-cli carries **zero** third-party dependencies and this is not the
feature to break that for — and a note file that needs a YAML engine to read
is no longer a file a human edits in any editor.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import sidecar

NOTES_FILE = "notes.md"

# Owned by track.json. Repeating them here creates a second truth that drifts.
RESERVED = frozenset(
    {"bpm", "camelot", "key", "cues", "energy", "energy_curve",
     "duration_s", "isrc", "feedback", "replaygain"}
)


def notes_path(audio: Path | str) -> Path:
    return sidecar.sidecar_dir(audio) / NOTES_FILE


def parse(text: str) -> dict[str, Any]:
    """Split a note into `{"meta": {...}, "body": "..."}`.

    A file with no frontmatter is all body — the common case when someone
    types a sentence and saves. That must never be an error.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {"meta": {}, "body": text.strip()}

    meta: dict[str, Any] = {}
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
        raw = lines[index]
        if not raw.strip() or raw.lstrip().startswith("#") or ":" not in raw:
            continue
        name, _, value = raw.partition(":")
        name, value = name.strip(), value.strip()
        if not name:
            continue
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip("'\"") for v in value[1:-1].split(",")]
            meta[name] = [v for v in items if v]
        else:
            meta[name] = value.strip("'\"")
    if end is None:
        # Unterminated frontmatter: treat the whole thing as prose rather than
        # silently swallowing the text as metadata.
        return {"meta": {}, "body": text.strip()}
    return {"meta": meta, "body": "\n".join(lines[end + 1:]).strip()}


def render(meta: dict[str, Any], body: str) -> str:
    if not meta:
        return (body or "").strip() + "\n"
    out = ["---"]
    for name, value in meta.items():
        if isinstance(value, (list, tuple)):
            out.append(f"{name}: [{', '.join(str(v) for v in value)}]")
        else:
            out.append(f"{name}: {value}")
    out.append("---")
    out.append("")
    out.append((body or "").strip())
    return "\n".join(out).rstrip() + "\n"


def read(audio: Path | str) -> dict[str, Any]:
    path = notes_path(audio)
    if not path.is_file():
        return {"meta": {}, "body": ""}
    try:
        return parse(path.read_text(encoding="utf-8"))
    except OSError:
        return {"meta": {}, "body": ""}


def write(
    audio: Path | str,
    meta: dict[str, Any] | None = None,
    body: str | None = None,
) -> Path:
    """Write the note, preserving whichever half is not being changed.

    Refuses reserved keys rather than dropping them: silently ignoring a
    `bpm:` someone typed would leave them believing it was recorded.
    """
    current = read(audio)
    new_meta = current["meta"] if meta is None else dict(meta)
    clashes = sorted(set(new_meta) & RESERVED)
    if clashes:
        raise ValueError(
            f"{', '.join(clashes)} belong to track.json, not notes.md — "
            "keeping them in one place is what stops the two files disagreeing"
        )
    new_body = current["body"] if body is None else body
    path = notes_path(audio)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(new_meta, new_body), encoding="utf-8")
    return path
