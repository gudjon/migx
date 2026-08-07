"""Resolve a batch of Spotify track links into an actionable sheet.

The workflow this serves: you have a handful of links you care about and you
want to know, for each one, *what it actually is* (exact recording, via ISRC)
and *whether you already own it*.

Deliberately mirror-first. The 83 mirrors already hold 3,700+ recordings with
their `spotify_id`, so a link you have saved anywhere is almost always a local
lookup — zero API calls, works offline, and immune to the development-mode
restriction that 403s `/v1/tracks` outright.
"""

from __future__ import annotations

import glob
import json
import os
import re
import urllib.parse
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "migx.track-sheet/1"

_ID_RE = re.compile(
    r"(?:spotify:track:|open\.spotify\.com/track/)([A-Za-z0-9]{22})"
)


def extract_ids(raw: Iterable[str]) -> list[str]:
    """Pull track ids out of URLs, URIs, or a bare list. Order preserved."""
    out: list[str] = []
    for item in raw:
        for line in str(item).splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            found = _ID_RE.findall(line)
            if found:
                out.extend(found)
            elif re.fullmatch(r"[A-Za-z0-9]{22}", line):
                out.append(line)
    seen: set[str] = set()
    return [i for i in out if not (i in seen or seen.add(i))]


def index_mirrors(mirror_root: Path) -> tuple[dict, dict]:
    """(spotify_id -> entry, spotify_id -> {playlist names})."""
    by_id: dict[str, dict[str, Any]] = {}
    on_lists: dict[str, set[str]] = {}
    pattern = str(Path(mirror_root).expanduser() / "**" / "*.json")
    for path in glob.glob(pattern, recursive=True):
        if "_pull-all" in os.path.basename(path):
            continue
        try:
            doc = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        name = doc.get("source_name") or Path(path).stem
        for entry in doc.get("tracks", []):
            sid = entry.get("spotify_id")
            if not sid:
                continue
            by_id.setdefault(sid, entry)
            on_lists.setdefault(sid, set()).add(name)
    return by_id, on_lists


def store_links(entry: dict[str, Any]) -> dict[str, str]:
    """Search URLs. ISRC first — it resolves to one exact recording."""
    artist = (entry.get("artists") or [""])[0]
    query = urllib.parse.quote(f"{artist} {entry.get('title') or ''}".strip())
    isrc = entry.get("isrc")
    links = {
        "beatport": f"https://www.beatport.com/search?q={query}",
        "bandcamp": f"https://bandcamp.com/search?q={query}",
    }
    if entry.get("spotify_id"):
        links["spotify"] = (
            f"https://open.spotify.com/track/{entry['spotify_id']}"
        )
    if isrc:
        # An ISRC search disambiguates radio edit vs extended mix vs remix,
        # which a title search cannot.
        links["beatport_isrc"] = (
            f"https://www.beatport.com/search?q={urllib.parse.quote(isrc)}"
        )
    return links


def build(
    ids: list[str], mirror_root: Path, resolver: Any | None = None
) -> dict[str, Any]:
    by_id, on_lists = index_mirrors(mirror_root)
    rows, unknown = [], []

    for sid in ids:
        entry = by_id.get(sid)
        if entry is None:
            unknown.append(sid)
            continue
        owned = resolver.resolve(entry) if resolver else None
        rows.append(
            {
                "spotify_id": sid,
                "isrc": entry.get("isrc"),
                "title": entry.get("title"),
                "artists": entry.get("artists") or [],
                "album": entry.get("album"),
                "duration_ms": entry.get("duration_ms"),
                "on_playlists": sorted(on_lists.get(sid, [])),
                "owned": bool(owned),
                "path": (owned or {}).get("path"),
                "links": store_links(entry),
            }
        )

    # Most-referenced first: a track on six of your playlists matters more
    # than one you saved once.
    rows.sort(key=lambda r: (-len(r["on_playlists"]), r["title"] or ""))
    return {
        "schema": SCHEMA,
        "requested": len(ids),
        "resolved": len(rows),
        "owned": sum(1 for r in rows if r["owned"]),
        "unresolved": unknown,
        "tracks": rows,
    }


def to_tsv(sheet: dict[str, Any]) -> str:
    head = [
        "isrc",
        "artist",
        "title",
        "album",
        "length",
        "owned",
        "on_playlists",
        "beatport_isrc",
        "beatport",
        "bandcamp",
        "spotify",
    ]
    lines = ["\t".join(head)]
    for r in sheet["tracks"]:
        ms = r.get("duration_ms") or 0
        links = r["links"]
        lines.append(
            "\t".join(
                [
                    r.get("isrc") or "",
                    ", ".join(r["artists"]),
                    r.get("title") or "",
                    r.get("album") or "",
                    f"{ms // 60000}:{(ms // 1000) % 60:02d}",
                    "yes" if r["owned"] else "",
                    "; ".join(r["on_playlists"]),
                    links.get("beatport_isrc", ""),
                    links.get("beatport", ""),
                    links.get("bandcamp", ""),
                    links.get("spotify", ""),
                ]
            )
        )
    return "\n".join(lines) + "\n"
