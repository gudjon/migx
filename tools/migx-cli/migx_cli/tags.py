"""Read embedded audio tags — ID3v2 and FLAC Vorbis comments, stdlib only.

Enough to resolve a mirror entry against a local file: title, artist, album,
track number and — the one that matters most — ISRC. ISRC is a globally unique
recording id, so an ISRC hit is an exact match and needs no fuzzy scoring.

No mutagen dependency: `tools/` stays dependency-free.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# ID3v2 text frames we care about -> normalised key.
_ID3_FRAMES = {
    b"TIT2": "title",
    b"TPE1": "artist",
    b"TPE2": "album_artist",
    b"TALB": "album",
    b"TRCK": "track_number",
    b"TSRC": "isrc",
    b"TDRC": "date",
    b"TYER": "date",
}

# TXXX descriptions that carry a field we care about, upper-cased.
_TXXX_KEYS = {
    "ISRC": "isrc",
    "ALBUMARTIST": "album_artist",
    "ALBUM ARTIST": "album_artist",
}

_VORBIS_FIELDS = {
    "title": "title",
    "artist": "artist",
    "albumartist": "album_artist",
    "album": "album",
    "tracknumber": "track_number",
    "isrc": "isrc",
    "date": "date",
}


def _syncsafe(data: bytes) -> int:
    size = 0
    for byte in data:
        size = (size << 7) | (byte & 0x7F)
    return size


def _decode_fields(payload: bytes) -> list[str]:
    """Decode an ID3 text frame body into its NUL-separated fields.

    The first byte is the encoding marker. Most frames carry one value; TXXX
    carries `description NUL value`, which is why callers need the list.
    """
    if not payload:
        return []
    encoding, body = payload[0], payload[1:]
    try:
        if encoding == 0:
            text = body.decode("latin-1")
        elif encoding == 1:
            text = body.decode("utf-16")
        elif encoding == 2:
            text = body.decode("utf-16-be")
        else:
            text = body.decode("utf-8")
    except (UnicodeDecodeError, LookupError):
        text = body.decode("latin-1", "replace")
    return [part.strip() for part in text.split("\x00")]


def _decode_text(payload: bytes) -> str:
    fields = _decode_fields(payload)
    return fields[0] if fields else ""


def _read_id3(handle: Any) -> dict[str, Any]:
    handle.seek(0)
    header = handle.read(10)
    if len(header) < 10 or header[:3] != b"ID3":
        return {}

    major = header[3]
    tag_size = _syncsafe(header[6:10])
    body = handle.read(tag_size)

    out: dict[str, Any] = {}
    pos = 0
    while pos + 10 <= len(body):
        frame_id = body[pos : pos + 4]
        if not frame_id.strip(b"\x00"):
            break
        raw_size = body[pos + 4 : pos + 8]
        # v2.4 uses syncsafe frame sizes; v2.3 uses plain big-endian.
        size = (
            _syncsafe(raw_size)
            if major >= 4
            else int.from_bytes(raw_size, "big")
        )
        pos += 10
        if size <= 0 or pos + size > len(body):
            break
        if frame_id in _ID3_FRAMES:
            key = _ID3_FRAMES[frame_id]
            out.setdefault(key, _decode_text(body[pos : pos + size]))
        elif frame_id == b"TXXX":
            # User-defined frame: `description NUL value`. ffmpeg and several
            # taggers write ISRC here rather than in the standard TSRC frame,
            # so ignoring TXXX silently loses the strongest match key.
            fields = _decode_fields(body[pos : pos + size])
            if len(fields) >= 2 and fields[0].upper() in _TXXX_KEYS:
                out.setdefault(_TXXX_KEYS[fields[0].upper()], fields[1])
        pos += size
    return out


def _read_flac(handle: Any) -> dict[str, Any]:
    handle.seek(4)  # past "fLaC"
    out: dict[str, Any] = {}
    while True:
        head = handle.read(4)
        if len(head) < 4:
            return out
        last = bool(head[0] & 0x80)
        block_type = head[0] & 0x7F
        length = int.from_bytes(head[1:4], "big")

        if block_type == 4:  # VORBIS_COMMENT
            block = handle.read(length)
            cursor = 0
            vendor_len = int.from_bytes(block[0:4], "little")
            cursor = 4 + vendor_len
            count = int.from_bytes(block[cursor : cursor + 4], "little")
            cursor += 4
            for _ in range(count):
                if cursor + 4 > len(block):
                    break
                item_len = int.from_bytes(block[cursor : cursor + 4], "little")
                cursor += 4
                item = block[cursor : cursor + item_len]
                cursor += item_len
                if b"=" not in item:
                    continue
                raw_key, _, raw_val = item.partition(b"=")
                key = raw_key.decode("utf-8", "replace").lower()
                if key in _VORBIS_FIELDS:
                    out.setdefault(
                        _VORBIS_FIELDS[key],
                        raw_val.decode("utf-8", "replace").strip(),
                    )
            return out

        handle.seek(length, 1)
        if last:
            return out


def read(path: Path | str) -> dict[str, Any]:
    """Return normalised tags for one file. Missing tags are simply absent."""
    path = Path(path)
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as handle:
            magic = handle.read(4)
            if magic == b"fLaC":
                tags = _read_flac(handle)
            elif magic[:3] == b"ID3":
                tags = _read_id3(handle)
            else:
                tags = {}
    except OSError:
        return {}

    if isinstance(tags.get("track_number"), str):
        # "7/12" -> 7
        head = tags["track_number"].split("/")[0].strip()
        tags["track_number"] = int(head) if head.isdigit() else None
    if tags.get("isrc"):
        tags["isrc"] = tags["isrc"].replace("-", "").upper()
    return {k: v for k, v in tags.items() if v not in ("", None)}
