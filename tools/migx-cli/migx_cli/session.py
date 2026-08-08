"""Live session status — what is "now" for the coaching agent.

While a set is running (or while the DJ preps in TUI), something has to answer
*which track is the feedback about?* This module owns a small JSON file at the
library root:

    <library>/_live.json

Written **off any audio callback** by CLI or TUI. Coding agents read it with
`session.now --json` and attach `track.feedback` / `track.note` / `track.cue`
to that identity. No MCP; no engine thread; house physics untouched.

Also carries session-local **room** state (crowd/theme/energy for *this night*,
not lifetime track quality). Lifetime judgments stay on the track sidecar
(`feedback.py`).
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from . import layout, sidecar, tags

SCHEMA = "migx.live-status/1"
LIVE_FILE = "_live.json"


def live_path(root: Path | str) -> Path:
    return Path(root).expanduser() / LIVE_FILE


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read(root: Path | str) -> dict[str, Any]:
    """Current live status, or an empty schema shell if missing."""
    path = live_path(root)
    if not path.is_file():
        return {"schema": SCHEMA, "path": None, "room": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": SCHEMA, "path": None, "room": {}, "error": "corrupt"}
    if not isinstance(data, dict):
        return {"schema": SCHEMA, "path": None, "room": {}}
    data.setdefault("schema", SCHEMA)
    data.setdefault("room", {})
    return data


def write(root: Path | str, data: dict[str, Any]) -> Path:
    """Atomic replace of _live.json."""
    path = live_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {**data, "schema": SCHEMA, "updated_at": _now()}
    body = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return path


def _identity(audio: Path) -> dict[str, Any]:
    meta = tags.read(audio)
    side = sidecar.read(audio)
    artists = []
    if meta.get("artist"):
        artists = [meta["artist"]]
    return {
        "path": str(audio.resolve()),
        "title": meta.get("title") or audio.stem,
        "artists": artists,
        "isrc": meta.get("isrc") or side.get("isrc"),
        "bpm": side.get("bpm") or meta.get("bpm"),
        "camelot": side.get("camelot") or meta.get("camelot"),
        "duration_s": None,  # filled by caller if known
    }


def bind(
    root: Path | str,
    audio: Path | str,
    *,
    deck: str | None = None,
    position_s: float | None = None,
    source: str = "cli",
) -> dict[str, Any]:
    """Point 'now' at this track. Merges room state from previous status."""
    audio = Path(audio).expanduser()
    if not audio.is_file():
        raise FileNotFoundError(str(audio))
    prev = read(root)
    ident = _identity(audio)
    doc: dict[str, Any] = {
        **ident,
        "deck": deck or prev.get("deck"),
        "position_s": position_s,
        "room": prev.get("room") or {},
        "source": source,
    }
    write(root, doc)
    return read(root)


def set_room(
    root: Path | str,
    *,
    theme: str | None = None,
    energy: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    """Update session-local room/crowd context (this night only)."""
    doc = read(root)
    room = dict(doc.get("room") or {})
    for key, value in (("theme", theme), ("energy", energy), ("note", note)):
        if value is not None:
            room[key] = value
    doc["room"] = room
    write(root, doc)
    return read(root)


def clear(root: Path | str) -> None:
    """Remove live binding (end of set / prep). Keeps file absence as empty."""
    path = live_path(root)
    try:
        path.unlink(missing_ok=True)
    except TypeError:
        # py3.7-style; we are on modern Python
        if path.is_file():
            path.unlink()


def resolve_now_track(root: Path | str) -> Path | None:
    """Path of the bound track if the file still exists."""
    doc = read(root)
    raw = doc.get("path")
    if not raw:
        return None
    p = Path(raw)
    return p if p.is_file() else None
