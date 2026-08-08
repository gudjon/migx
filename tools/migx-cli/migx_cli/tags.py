"""Read embedded audio tags — ID3v2 and FLAC Vorbis comments, stdlib only.

Enough to resolve a mirror entry against a local file: title, artist, album,
track number and — the one that matters most — ISRC. ISRC is a globally unique
recording id, so an ISRC hit is an exact match and needs no fuzzy scoring.

No mutagen dependency: `tools/` stays dependency-free.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import keys

# ID3v2 text frames we care about -> normalised key.
_ID3_FRAMES = {
    b"TIT2": "title",
    b"TPE1": "artist",
    b"TPE2": "album_artist",
    b"TALB": "album",
    b"TRCK": "track_number",
    b"TSRC": "isrc",
    b"TBPM": "bpm",
    b"TKEY": "key",
    b"TDRC": "date",
    b"TYER": "date",
}

# TXXX descriptions that carry a field we care about, upper-cased.
_TXXX_KEYS = {
    "ISRC": "isrc",
    # Mixed In Key / Traktor / rekordbox all park these in TXXX.
    "INITIALKEY": "key",
    "INITIAL KEY": "key",
    "KEY": "key",
    "BPM": "bpm",
    "ENERGY": "energy",
    "ENERGYLEVEL": "energy",
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
    "bpm": "bpm",
    "initialkey": "key",
    "key": "key",
    "energy": "energy",
    "energylevel": "energy",
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


def _mime_to_ext(mime: str) -> str:
    mime = (mime or "").lower().split(";")[0].strip()
    return {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }.get(mime, ".jpg")


def _parse_apic(payload: bytes) -> tuple[bytes, str] | None:
    """Decode an ID3 APIC frame body → (image_bytes, .ext)."""
    if len(payload) < 4:
        return None
    encoding = payload[0]
    rest = payload[1:]
    # MIME is always ISO-8859-1, terminated by 0x00.
    nul = rest.find(b"\x00")
    if nul < 0:
        return None
    mime = rest[:nul].decode("latin-1", "replace")
    rest = rest[nul + 1 :]
    if not rest:
        return None
    # picture type (1 byte) + description + image
    rest = rest[1:]
    if encoding in (1, 2):  # UTF-16 with BOM / UTF-16BE — description ends \0\0
        end = 0
        while end + 1 < len(rest):
            if rest[end : end + 2] == b"\x00\x00":
                rest = rest[end + 2 :]
                break
            end += 2
        else:
            return None
    else:  # latin-1 or utf-8 — single NUL
        nul = rest.find(b"\x00")
        if nul < 0:
            return None
        rest = rest[nul + 1 :]
    if not rest:
        return None
    return rest, _mime_to_ext(mime)


def extract_cover(path: Path | str) -> tuple[bytes, str] | None:
    """Pull the first front-cover (or any) APIC image from an MP3.

    Stdlib only. Returns (bytes, extension) or None. FLAC picture blocks are
    not handled here yet — folder art + chafa cover the common path.
    """
    path = Path(path)
    if not path.is_file():
        return None
    try:
        with path.open("rb") as handle:
            header = handle.read(10)
            if len(header) < 10 or header[:3] != b"ID3":
                return None
            major = header[3]
            tag_size = _syncsafe(header[6:10])
            body = handle.read(tag_size)
    except OSError:
        return None

    pos = 0
    fallback: tuple[bytes, str] | None = None
    while pos + 10 <= len(body):
        frame_id = body[pos : pos + 4]
        if not frame_id.strip(b"\x00"):
            break
        raw_size = body[pos + 4 : pos + 8]
        size = (
            _syncsafe(raw_size)
            if major >= 4
            else int.from_bytes(raw_size, "big")
        )
        pos += 10
        if size <= 0 or pos + size > len(body):
            break
        if frame_id == b"APIC":
            parsed = _parse_apic(body[pos : pos + size])
            if parsed:
                # Prefer picture type 3 (front cover) when we can read it.
                # Type is the byte after MIME; re-check from frame body.
                payload = body[pos : pos + size]
                # encoding + mime + nul + type
                mime_end = payload.find(b"\x00", 1)
                ptype = (
                    payload[mime_end + 1]
                    if mime_end >= 0 and mime_end + 1 < len(payload)
                    else 0
                )
                if ptype == 3:
                    return parsed
                fallback = fallback or parsed
        pos += size
    return fallback


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

    # Normalise what a tagger wrote into the two fields naming.render wants.
    # Detection stays in src/analyzer/ (arch-analyzer) — this only reads.
    bpm = keys.parse_bpm(tags.pop("bpm", None))
    if bpm is not None:
        tags["bpm"] = bpm
    camelot = keys.to_camelot(tags.get("key"))
    if camelot:
        tags["camelot"] = camelot
    return {k: v for k, v in tags.items() if v not in ("", None)}
