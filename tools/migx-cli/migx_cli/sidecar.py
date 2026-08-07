"""Per-track sidecar — DJ notes and timed cues, beside the audio.

Uses the sidecar the C++ side already writes, rather than inventing a second
one (`src/library/dao/trackdao.cpp` → `exportToSidecar`):

    Collection/J/Jon Hopkins - Reckoning.mp3
    Collection/J/Jon Hopkins - Reckoning.mp3.migx/
        track.json      <- bpm, key, replaygain, peak, cues, energy_curve

`filesystem-driven-architecture.md` settles the ownership question:
**sidecar is the source of truth for musical metadata, the DB is a derived
index.** So a note written here is authoritative, greppable, diffable, and
survives a library rebuild.

Two additions to the existing object, both optional so the DAO ignores them:

    "notes": "girly song, works after a vocal house run"
    "tags":  ["girly", "peak-time", "closer"]

Timed bookmarks are **not** a new concept — they are `cues`, the same array
`cuesToJson()` writes, with `position` in seconds and `label` carrying the
reminder ("start mixing here, intro is over").

Every write is read-modify-write and preserves unknown keys. The analyzer may
have written a beatgrid and an energy curve into this file; a note must never
cost you those.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

SIDECAR_DIR_SUFFIX = ".migx"
TRACK_FILE = "track.json"

# Mixxx cue types; a plain bookmark is a "hotcue" only when numbered.
CUE_MANUAL = "manual"


def sidecar_dir(audio: Path | str) -> Path:
    audio = Path(audio)
    return audio.with_name(audio.name + SIDECAR_DIR_SUFFIX)


def track_file(audio: Path | str) -> Path:
    return sidecar_dir(audio) / TRACK_FILE


def read(audio: Path | str) -> dict[str, Any]:
    """The sidecar object, or {} when there is none. Never raises."""
    path = track_file(audio)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write(audio: Path | str, data: dict[str, Any]) -> Path:
    """Atomically replace the sidecar: temp file then rename.

    A half-written track.json would lose cues the analyzer spent minutes on,
    and a crash mid-write is exactly when you least want that.
    """
    path = track_file(audio)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return path


def set_note(
    audio: Path | str,
    note: str | None = None,
    tags: list[str] | None = None,
    append: bool = False,
) -> dict[str, Any]:
    """Set or extend the track-level note and tags. Preserves everything else."""
    data = read(audio)
    if note is not None:
        existing = (data.get("notes") or "").strip()
        data["notes"] = (
            f"{existing}; {note}".strip("; ") if append and existing else note
        )
    if tags is not None:
        current = list(data.get("tags") or []) if append else []
        for tag in tags:
            tag = tag.strip()
            if tag and tag not in current:
                current.append(tag)
        data["tags"] = current
    write(audio, data)
    return data


def parse_position(value: str) -> float:
    """Accept 90, 1:30, or 1m30s — a DJ thinks in minutes, not seconds."""
    text = str(value).strip().lower()
    if ":" in text:
        parts = [float(p) for p in text.split(":")]
        seconds = 0.0
        for part in parts:
            seconds = seconds * 60 + part
        return seconds
    if "m" in text or "s" in text:
        minutes = 0.0
        rest = text
        if "m" in rest:
            head, _, rest = rest.partition("m")
            minutes = float(head or 0)
        secs = float(rest.replace("s", "") or 0)
        return minutes * 60 + secs
    return float(text)


def add_cue(
    audio: Path | str,
    position: float,
    label: str,
    color: str | None = None,
    hotcue: int | None = None,
) -> dict[str, Any]:
    """Add a timed bookmark, kept sorted by position.

    Written in the shape `cuesToJson()` already emits, so the same array is
    readable by the engine side rather than being a parallel format.
    """
    data = read(audio)
    cues = list(data.get("cues") or [])
    entry: dict[str, Any] = {
        "type": CUE_MANUAL,
        "position": round(float(position), 3),
        "label": label,
    }
    if color:
        entry["color"] = color
    if hotcue is not None:
        entry["hotcue"] = int(hotcue)
    cues.append(entry)
    cues.sort(
        key=lambda c: (c.get("position") is None, c.get("position") or 0)
    )
    data["cues"] = cues
    write(audio, data)
    return data


def remove_cue(audio: Path | str, index: int) -> dict[str, Any]:
    data = read(audio)
    cues = list(data.get("cues") or [])
    if 0 <= index < len(cues):
        cues.pop(index)
        data["cues"] = cues
        write(audio, data)
    return data


def fmt_position(seconds: Any) -> str:
    try:
        total = int(float(seconds))
    except (TypeError, ValueError):
        return "--:--"
    return f"{total // 60}:{total % 60:02d}"
