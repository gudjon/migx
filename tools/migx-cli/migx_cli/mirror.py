"""Playlist mirror — a Spotify playlist as a dated, diffable local snapshot.

Schema: `migx.playlist-mirror/1` (see schema/migx.playlist-mirror.v1.json),
naming the existing convention from `output-verification-formats-naming.md`.

Why snapshots: Discover Weekly is regenerated every Monday and Release Radar
every Friday — the previous week is destroyed. A dated mirror gives Migx a
longitudinal taste corpus Spotify itself does not retain.

Identity only. `isrc` is the join key for resolving against files you own; no
audio is fetched, decoded, or stored here.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "migx.playlist-mirror/1"


def _entry(
    track: dict[str, Any], added_at: str | None, position: int
) -> dict[str, Any] | None:
    """Normalise one Spotify track object into a mirror entry."""
    if not track or track.get("type") != "track":
        return None  # local files / episodes / removed tracks
    album = track.get("album") or {}
    album_artists = [
        a.get("name", "") for a in album.get("artists", []) if a.get("name")
    ]

    return {
        "position": position,
        "spotify_id": track.get("id"),
        "uri": track.get("uri"),
        "title": track.get("name"),
        "artists": [
            a.get("name", "")
            for a in track.get("artists", [])
            if a.get("name")
        ],
        "album": album.get("name"),
        "album_artist": album_artists[0] if album_artists else None,
        "track_number": track.get("track_number"),
        "disc_number": track.get("disc_number"),
        "duration_ms": track.get("duration_ms"),
        "release_date": album.get("release_date"),
        "isrc": (track.get("external_ids") or {}).get("isrc"),
        "explicit": track.get("explicit"),
        "added_at": added_at,
    }


def build(
    *,
    source_id: str,
    source_name: str,
    owner: str | None,
    items: Iterable[dict[str, Any]],
    snapshot_id: str | None = None,
    captured_at: str | None = None,
) -> dict[str, Any]:
    """Build a mirror document from raw playlist/saved-track items."""
    entries: list[dict[str, Any]] = []
    skipped = 0
    for item in items:
        track = item.get("track") or {}
        entry = _entry(track, item.get("added_at"), len(entries))
        if entry is None:
            skipped += 1
            continue
        entries.append(entry)

    now = captured_at or _dt.datetime.now(_dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    iso_year, iso_week, _ = _dt.datetime.strptime(
        now[:10], "%Y-%m-%d"
    ).isocalendar()

    return {
        "schema": SCHEMA,
        "source": "spotify",
        "source_id": source_id,
        "source_name": source_name,
        "owner": owner,
        "snapshot_id": snapshot_id,
        "captured_at": now,
        "captured_week": f"{iso_year}-W{iso_week:02d}",
        "track_count": len(entries),
        "skipped_count": skipped,
        "tracks": entries,
    }


def slug(name: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in name.strip()]
    out = "".join(keep)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-") or "playlist"


def default_path(root: Path, doc: dict[str, Any]) -> Path:
    """`<root>/<slug>/<slug>-<week>.json` — weekly snapshots sort naturally."""
    name = slug(doc.get("source_name") or doc.get("source_id") or "playlist")
    return root / name / f"{name}-{doc['captured_week']}.json"


def write(doc: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path
