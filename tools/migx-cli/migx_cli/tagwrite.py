"""Write ID3v2.4 tags to an MP3 — stdlib only, no mutagen.

Ingestion needs the *write* half of `tags.py`: a file entering the library
carries the identity it was matched to, so a later `library.resolve`
finds it by
ISRC instead of falling back to fuzzy title matching.

Only MP3/ID3 is written. FLAC and WAV are passed through untouched: their tags
are already reliable in practice, and a half-correct Vorbis writer would be
worse than none. `P-07` — one writer per artifact family; this is it for ID3.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Normalised key -> ID3v2.4 frame id. Mirrors tags._ID3_FRAMES.
_FRAMES = {
    "title": b"TIT2",
    "artist": b"TPE1",
    "album_artist": b"TPE2",
    "album": b"TALB",
    "track_number": b"TRCK",
    "isrc": b"TSRC",
    "date": b"TDRC",
}


def _syncsafe(n: int) -> bytes:
    if n < 0 or n >= (1 << 28):
        raise ValueError(f"size {n} does not fit a syncsafe integer")
    return bytes(
        [(n >> 21) & 0x7F, (n >> 14) & 0x7F, (n >> 7) & 0x7F, n & 0x7F]
    )


def _text_frame(frame_id: bytes, value: str) -> bytes:
    # Encoding 0x03 = UTF-8, the v2.4 default; NUL-terminated.
    payload = b"\x03" + value.encode("utf-8") + b"\x00"
    return frame_id + _syncsafe(len(payload)) + b"\x00\x00" + payload


def _existing_tag_size(data: bytes) -> int:
    """Bytes of leading ID3v2 tag to drop, 0 if none."""
    if len(data) >= 10 and data[:3] == b"ID3":
        size = 0
        for byte in data[6:10]:
            size = (size << 7) | (byte & 0x7F)
        return 10 + size
    return 0


def build_tag(meta: dict[str, Any]) -> bytes:
    """Build a complete ID3v2.4 tag for the given normalised metadata."""
    body = b""
    for key, frame_id in _FRAMES.items():
        value = meta.get(key)
        if value in (None, ""):
            continue
        body += _text_frame(frame_id, str(value))
    if not body:
        return b""
    return b"ID3\x04\x00\x00" + _syncsafe(len(body)) + body


def write_mp3(path: Path | str, meta: dict[str, Any]) -> bool:
    """Replace the ID3 tag on an MP3 in place. Returns True if written.

    Rewrites the whole file, which is fine for ingestion (one pass, already
    copying) and avoids the padding arithmetic an in-place patch would need.
    """
    path = Path(path)
    data = path.read_bytes()
    if data[:3] != b"ID3" and not (data[:1] == b"\xff"):
        return False  # not an MP3 we recognise

    tag = build_tag(meta)
    if not tag:
        return False
    audio = data[_existing_tag_size(data) :]
    path.write_bytes(tag + audio)
    return True


def write(path: Path | str, meta: dict[str, Any]) -> bool:
    """Write tags where we can do it correctly; otherwise leave the file be."""
    path = Path(path)
    if path.suffix.lower() == ".mp3":
        return write_mp3(path, meta)
    return False
