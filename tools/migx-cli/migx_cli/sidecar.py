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
import sys
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
    """The sidecar object, or {} when there is none. Never raises.

    A CORRUPT sidecar is preserved before `{}` is returned. Returning `{}` for
    damaged JSON is indistinguishable from "this track has no sidecar", so the
    track reads as merely unanalysed — and the next `library.analyze` rewrites
    it, destroying the DJ's cues, notes and feedback for good. The audio is
    replaceable; hand-made cue points are not.

    So the bad file is moved aside to `track.json.corrupt` and the damage is
    reported on stderr. `{}` is still returned, because callers legitimately
    rely on this never raising — but the data survives and a human is told
    (`P-34`: classified failure, never a silent default).
    """
    path = track_file(audio)
    if not path.is_file():
        return {}
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"warning: cannot read sidecar {path}: {exc}", file=sys.stderr)
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        salvage = path.with_suffix(path.suffix + ".corrupt")
        try:
            if not salvage.exists():
                path.rename(salvage)
                where = f" — preserved at {salvage.name}"
            else:
                where = f" — earlier copy already at {salvage.name}"
        except OSError:
            where = " — could NOT preserve it"
        print(
            f"warning: corrupt sidecar {path} ({exc}){where}",
            file=sys.stderr,
        )
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


# ---------------------------------------------------------------------------
# Package identity — a re-attachment key, deliberately NOT an authority.
# ---------------------------------------------------------------------------

IDENTITY_FILE = "identity.json"


def identity_path(audio: Path | str) -> Path:
    return sidecar_dir(audio) / IDENTITY_FILE


def record_identity(audio: Path | str, isrc: str | None) -> Path | None:
    """Stamp the recording's ISRC inside the package.

    A package is otherwise located only by ADJACENCY — `X.mp3.migx/` is found
    by sitting beside `X.mp3`. Renames survive that (rename.py moves both), but
    a re-downloaded or restored copy of the same recording cannot claim the old
    package, so hand-made cues and floor judgments stay attached to the file
    that was replaced. For a package billed as portable that is the weak link.

    Written as **provenance, not authority**: `authority` names the tags as the
    owner, so if this copy and the file's tag ever disagree, the TAG wins. The
    stamp exists to answer "which package belongs to this recording", never
    "what is this recording".
    """
    if not isrc:
        return None
    normalised = isrc.replace("-", "").strip().upper()
    if not normalised:
        return None
    path = identity_path(audio)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(
        path,
        {
            "schema": "migx.package-identity/1",
            "isrc": normalised,
            "authority": "file-tags",
            "note": (
                "Re-attachment key only. The audio file's tag is the source of "
                "truth for identity; on conflict the tag wins."
            ),
        },
    )
    return path


def read_identity(audio: Path | str) -> dict[str, Any]:
    path = identity_path(audio)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_json_atomic(path: Path, data: dict[str, Any]) -> Path:
    """temp + fsync + rename, so no reader ever sees half a file."""
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
