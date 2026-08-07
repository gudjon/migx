"""Output naming convention — one template, one sanitiser, one truth.

Template tokens (spotDL-compatible so existing muscle memory transfers):
    {artist}  {album-artist}  {album}  {title}  {track-number}  {disc-number}
    {year}    {isrc}          {ext}

Defaults:
    library   {album-artist}/{album}/{track-number} - {title}.{ext}
    flat      {artist} - {title}.{ext}

`P-07`: one writer per artifact family. Every path Migx produces for a synced
track comes from `render()` — no ad-hoc f-strings at call sites, or the library
grows two naming schemes and neither is authoritative.
"""

from __future__ import annotations

import re
import unicodedata

TEMPLATE_LIBRARY = "{album-artist}/{album}/{track-number} - {title}.{ext}"
TEMPLATE_FLAT = "{artist} - {title}.{ext}"

# Reserved on macOS/HFS+ and Windows alike; `/` and `:` matter most on macOS.
_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_COLLAPSE = re.compile(r"\s+")
_MAX_COMPONENT = (
    120  # bytes of headroom under the 255-byte per-component limit
)


def sanitize(value: str, *, fallback: str = "Unknown") -> str:
    """Make one path component safe without mangling non-ASCII artist names."""
    if not value:
        return fallback
    # NFC keeps accented names stable across macOS (which prefers NFD on disk).
    value = unicodedata.normalize("NFC", value)
    value = _ILLEGAL.sub("-", value)
    value = _COLLAPSE.sub(" ", value).strip(" .")
    if len(value) > _MAX_COMPONENT:
        value = value[:_MAX_COMPONENT].rstrip(" .-")
    return value or fallback


def render(
    entry: dict, *, template: str = TEMPLATE_LIBRARY, ext: str = "mp3"
) -> str:
    """Render a relative path for one mirror entry.

    Never returns an absolute path.
    """
    artists = entry.get("artists") or []
    primary = artists[0] if artists else ""
    track_no = entry.get("track_number")
    disc_no = entry.get("disc_number")
    date = entry.get("release_date") or ""

    values = {
        "artist": sanitize(primary, fallback="Unknown Artist"),
        "album-artist": sanitize(
            entry.get("album_artist") or primary, fallback="Unknown Artist"
        ),
        "album": sanitize(entry.get("album") or "", fallback="Unknown Album"),
        "title": sanitize(entry.get("title") or "", fallback="Untitled"),
        "track-number": (
            f"{track_no:02d}" if isinstance(track_no, int) else "00"
        ),
        "disc-number": f"{disc_no:d}" if isinstance(disc_no, int) else "1",
        "year": date[:4] if len(date) >= 4 else "0000",
        "isrc": sanitize(entry.get("isrc") or "", fallback="NOISRC"),
        "ext": ext.lstrip("."),
    }

    out = template
    for key, value in values.items():
        out = out.replace("{" + key + "}", value)
    # A leading separator would make this absolute; strip defensively.
    return out.lstrip("/")
