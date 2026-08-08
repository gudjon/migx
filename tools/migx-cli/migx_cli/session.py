"""Live session status + night log for the coaching agent.

While a set is running (or while the DJ preps in TUI), something has to answer
*which track is the feedback about?* This module owns two small files at the
library root — both written **off any audio callback** by CLI or TUI:

    <library>/_live.json       # current "now" binding + room (mutable)
    <library>/_session.jsonl   # append-only night log (bind / room / feedback / clear)

Coding agents read `session.now --json` and attach `track.feedback` /
`track.note` / `track.cue` to that identity. After the night,
`session.show` reconstructs the ordered plays and floor judgments from the
JSONL. No MCP; no engine thread; house physics untouched.

LifetimeSession-local** room state (crowd/theme/energy for *this night*) lives on
`_live.json` and is mirrored into the log. Lifetime track judgments stay on
the track sidecar (`feedback.py`).
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from . import sidecar, tags

SCHEMA = "migx.live-status/1"
EVENT_SCHEMA = "migx.session-event/1"
SHOW_SCHEMA = "migx.session-log/1"
LIVE_FILE = "_live.json"
LOG_FILE = "_session.jsonl"

# Closed vocabulary for log event kinds (lint-checkable; agent maps speech
# into these via bind/room/feedback/clear, never free-form event types).
EVENT_TYPES = ("bind", "room", "feedback", "clear")


def live_path(root: Path | str) -> Path:
    return Path(root).expanduser() / LIVE_FILE


def log_path(root: Path | str) -> Path:
    return Path(root).expanduser() / LOG_FILE


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


def append_event(
    root: Path | str,
    event_type: str,
    **fields: Any,
) -> dict[str, Any]:
    """Append one typed event to the night JSONL. Returns the event dict.

    Append-only by design: a night is a history, not a mutable document.
    Concurrent writers are safe enough for dogfood (O_APPEND + one line each);
    readers skip corrupt lines.
    """
    if event_type not in EVENT_TYPES:
        raise ValueError(
            f"event type must be one of {', '.join(EVENT_TYPES)}, "
            f"got {event_type!r}"
        )
    event: dict[str, Any] = {
        "schema": EVENT_SCHEMA,
        "at": fields.pop("at", None) or _now(),
        "type": event_type,
    }
    for key, value in fields.items():
        if value is not None:
            event[key] = value
    path = log_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
    # O_APPEND so two CLI processes don't clobber each other on the same night.
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)
    return event


def read_events(
    root: Path | str,
    *,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """All parseable events from the night log, oldest first.

    If *limit* is set, return only the last *limit* events (still oldest→newest
    within that window).
    """
    path = log_path(root)
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("type") in EVENT_TYPES:
            events.append(obj)
    if limit is not None and limit >= 0:
        events = events[-limit:]
    return events


def reconstruct(
    root: Path | str,
    *,
    limit: int | None = None,
) -> dict[str, Any]:
    """Rebuild the night: ordered plays, room arc, feedback attached to plays.

    A *play* starts at each `bind` and collects subsequent `feedback` events
    whose path matches (or that lack a path while that bind is current).
    `room` events update the running room; `clear` ends the live slot without
    erasing the log.
    """
    events = read_events(root, limit=limit)
    plays: list[dict[str, Any]] = []
    room: dict[str, Any] = {}
    current: dict[str, Any] | None = None

    def _close_play() -> None:
        nonlocal current
        if current is not None:
            plays.append(current)
            current = None

    for ev in events:
        kind = ev.get("type")
        if kind == "bind":
            _close_play()
            current = {
                "at": ev.get("at"),
                "path": ev.get("path"),
                "title": ev.get("title"),
                "artists": ev.get("artists") or [],
                "deck": ev.get("deck"),
                "source": ev.get("source"),
                "feedback": [],
            }
        elif kind == "feedback":
            entry = {
                k: ev[k]
                for k in (
                    "at",
                    "fit",
                    "placement",
                    "segment",
                    "transition",
                    "note",
                )
                if k in ev
            }
            path = ev.get("path")
            if current is not None and (
                path is None or path == current.get("path")
            ):
                current["feedback"].append(entry)
            else:
                # Feedback without a matching open bind still shows as a play
                # stub so the night is not silent about the judgment.
                plays.append(
                    {
                        "at": ev.get("at"),
                        "path": path,
                        "title": ev.get("title"),
                        "artists": ev.get("artists") or [],
                        "deck": None,
                        "source": "feedback-only",
                        "feedback": [entry],
                    }
                )
        elif kind == "room":
            for key in ("theme", "energy", "note"):
                if ev.get(key) is not None:
                    room[key] = ev[key]
        elif kind == "clear":
            _close_play()

    if current is not None:
        plays.append(current)

    return {
        "schema": SHOW_SCHEMA,
        "log": str(log_path(root)),
        "event_count": len(events),
        "events": events,
        "plays": plays,
        "room": room,
    }


def format_show(doc: dict[str, Any]) -> str:
    """Human timeline for session.show (no JSON)."""
    events = doc.get("events") or []
    if not events:
        return "session log empty — bind a track or record feedback first"
    lines = [f"session log  ({doc.get('event_count', 0)} events)"]
    for ev in events:
        at = (ev.get("at") or "")[-9:-1]  # HH:MM:SS from ISO Z stamp
        kind = ev.get("type") or "?"
        if kind == "bind":
            deck = f"  [{ev['deck']}]" if ev.get("deck") else ""
            title = ev.get("title") or Path(ev.get("path") or "?").name
            lines.append(f"  {at}  bind      {title}{deck}")
        elif kind == "feedback":
            bits = [
                f"{k}={ev[k]}"
                for k in ("fit", "placement", "segment", "transition")
                if ev.get(k) is not None
            ]
            if ev.get("note"):
                bits.append(f'note="{ev["note"]}"')
            title = ev.get("title") or Path(ev.get("path") or "?").name
            detail = " ".join(bits) if bits else "—"
            lines.append(f"  {at}  feedback  {title}  {detail}")
        elif kind == "room":
            bits = [
                f"{k}={ev[k]}"
                for k in ("theme", "energy", "note")
                if ev.get(k) is not None
            ]
            lines.append(f"  {at}  room      {', '.join(bits) or '—'}")
        elif kind == "clear":
            lines.append(f"  {at}  clear")
        else:
            lines.append(f"  {at}  {kind}")
    room = doc.get("room") or {}
    if room:
        bits = [f"{k}={v}" for k, v in room.items() if v]
        if bits:
            lines.append("room now: " + ", ".join(bits))
    plays = doc.get("plays") or []
    lines.append(f"plays: {len(plays)}")
    return "\n".join(lines)


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
    append_event(
        root,
        "bind",
        path=doc["path"],
        title=doc.get("title"),
        artists=doc.get("artists") or [],
        deck=doc.get("deck"),
        source=source,
        position_s=position_s,
    )
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
    append_event(root, "room", theme=theme, energy=energy, note=note)
    return read(root)


def log_feedback(
    root: Path | str,
    audio: Path | str,
    *,
    fit: str | None = None,
    placement: str | None = None,
    segment: str | None = None,
    transition: int | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    """Mirror a track.feedback verdict into the night log (session-local)."""
    audio = Path(audio).expanduser()
    ident = _identity(audio) if audio.is_file() else {
        "path": str(audio),
        "title": audio.stem,
        "artists": [],
    }
    return append_event(
        root,
        "feedback",
        path=ident.get("path") or str(audio),
        title=ident.get("title"),
        artists=ident.get("artists") or [],
        fit=fit,
        placement=placement,
        segment=segment,
        transition=transition,
        note=note,
    )


def clear(root: Path | str) -> None:
    """Remove live binding (end of set / prep). Night log stays for session.show."""
    append_event(root, "clear")
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
