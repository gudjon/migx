"""Audio quality gate — the DJ bar as a contract on the *file*.

Not on the pipeline that produced it.

A resolver is trusted or not based on what it produced, never on where
to get it. That is deliberate: the file contract and the licensing line end up
being the same line, because the paths that cut legal corners are the
that hand you a lossy->lossy transcode.

    lossless        FLAC / WAV / AIFF / ALAC          -> eligible
    mp3-320-cbr     true 320 kbps constant bitrate    -> eligible
    mp3-vbr-high    VBR averaging >= 220 kbps         -> needs --allow-tier
    below-bar       everything else                   -> refused

A YouTube-sourced file lands in `below-bar` or `mp3-vbr-high` nearly
it is Opus re-encoded to MP3, so it cannot present as true 320 CBR.

Header parsing is stdlib only — no mutagen, no ffprobe dependency.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

# MPEG-1 Layer III bitrates, kbps, indexed by the 4-bit header field.
_MPEG1_L3 = (
    None,
    32,
    40,
    48,
    56,
    64,
    80,
    96,
    112,
    128,
    160,
    192,
    224,
    256,
    320,
    None,
)
_MPEG2_L3 = (
    None,
    8,
    16,
    24,
    32,
    40,
    48,
    56,
    64,
    80,
    96,
    112,
    128,
    144,
    160,
    None,
)
_SAMPLE_RATES = {
    3: (44100, 48000, 32000),  # MPEG-1
    2: (22050, 24000, 16000),  # MPEG-2
    0: (11025, 12000, 8000),  # MPEG-2.5
}

TIER_LOSSLESS = "lossless"
TIER_MP3_320 = "mp3-320-cbr"
TIER_MP3_VBR = "mp3-vbr-high"
TIER_BELOW = "below-bar"
TIER_UNKNOWN = "unknown"

DEFAULT_ELIGIBLE = (TIER_LOSSLESS, TIER_MP3_320)
VBR_HIGH_FLOOR_KBPS = 220


def _skip_id3(data: bytes) -> int:
    """Return the offset past an ID3v2 tag, if present."""
    if len(data) >= 10 and data[:3] == b"ID3":
        # Syncsafe integer: 7 bits per byte.
        size = 0
        for byte in data[6:10]:
            size = (size << 7) | (byte & 0x7F)
        return 10 + size
    return 0


def _parse_frame(header: bytes) -> dict[str, Any] | None:
    """Decode one MPEG audio frame header.

    Returns None if it is not a valid Layer III frame.
    """
    if len(header) < 4 or header[0] != 0xFF or (header[1] & 0xE0) != 0xE0:
        return None
    version = (header[1] >> 3) & 0x03  # 3=MPEG1, 2=MPEG2, 0=MPEG2.5
    layer = (header[1] >> 1) & 0x03  # 1 = Layer III
    if layer != 1 or version == 1:
        return None

    table = _MPEG1_L3 if version == 3 else _MPEG2_L3
    bitrate = table[(header[2] >> 4) & 0x0F]
    rate_idx = (header[2] >> 2) & 0x03
    if bitrate is None or rate_idx == 3:
        return None
    sample_rate = _SAMPLE_RATES[version][rate_idx]
    padding = (header[2] >> 1) & 0x01
    channel_mode = (header[3] >> 6) & 0x03

    samples = 1152 if version == 3 else 576
    frame_len = int((samples // 8) * bitrate * 1000 / sample_rate) + padding
    return {
        "bitrate": bitrate,
        "sample_rate": sample_rate,
        "version": version,
        "channel_mode": channel_mode,
        "frame_len": frame_len,
    }


def _inspect_mp3(data: bytes) -> dict[str, Any]:
    offset = _skip_id3(data)
    # Find the first frame sync.
    first = None
    while offset < len(data) - 4:
        frame = _parse_frame(data[offset : offset + 4])
        if frame:
            first = frame
            break
        offset += 1
    if not first:
        return {
            "codec": "mp3",
            "tier": TIER_UNKNOWN,
            "reason": "no MPEG frame found",
        }

    # Xing => VBR, Info => CBR. The tag sits after the side-info block.
    side = {3: (32, 17), 2: (17, 9), 0: (17, 9)}[first["version"]]
    side_len = side[1] if first["channel_mode"] == 3 else side[0]
    tag_at = offset + 4 + side_len
    marker = data[tag_at : tag_at + 4]
    declared_vbr = marker == b"Xing"
    declared_cbr = marker == b"Info"

    # Sample real frame bitrates to catch files with no Xing/Info tag at all.
    rates: list[int] = []
    cursor = offset
    for _ in range(200):
        frame = _parse_frame(data[cursor : cursor + 4])
        if not frame:
            break
        rates.append(frame["bitrate"])
        cursor += frame["frame_len"]
        if cursor >= len(data) - 4:
            break

    observed = sorted(set(rates))
    avg = sum(rates) / len(rates) if rates else first["bitrate"]
    is_cbr = declared_cbr or (not declared_vbr and len(observed) == 1)

    info = {
        "codec": "mp3",
        "bitrate_kbps": round(avg),
        "sample_rate": first["sample_rate"],
        "mode": "cbr" if is_cbr else "vbr",
        "lossless": False,
        "observed_bitrates": observed,
    }

    if is_cbr and first["bitrate"] == 320:
        info["tier"] = TIER_MP3_320
        info["reason"] = "true 320 kbps CBR"
    elif not is_cbr and avg >= VBR_HIGH_FLOOR_KBPS:
        info["tier"] = TIER_MP3_VBR
        info["reason"] = (
            f"VBR averaging {round(avg)} kbps — high, but not true 320 CBR"
        )
    else:
        info["tier"] = TIER_BELOW
        info["reason"] = (
            f"{round(avg)} kbps {'CBR' if is_cbr else 'VBR'} "
            "— below the 320 CBR / lossless bar"
        )
    return info


def _inspect_flac(data: bytes) -> dict[str, Any]:
    # STREAMINFO is the first metadata block: 34 bytes after the 4-byte header.
    if len(data) < 42:
        return {
            "codec": "flac",
            "tier": TIER_UNKNOWN,
            "reason": "truncated STREAMINFO",
        }
    block = data[8:26]
    packed = int.from_bytes(block[10:18], "big")
    sample_rate = (packed >> 44) & 0xFFFFF
    bit_depth = ((packed >> 36) & 0x1F) + 1
    return {
        "codec": "flac",
        "lossless": True,
        "sample_rate": sample_rate,
        "bit_depth": bit_depth,
        "mode": "lossless",
        "tier": TIER_LOSSLESS,
        "reason": f"FLAC {bit_depth}-bit / {sample_rate} Hz",
    }


def _inspect_riff(data: bytes) -> dict[str, Any]:
    sample_rate = struct.unpack("<I", data[24:28])[0] if len(data) >= 28 else 0
    bit_depth = struct.unpack("<H", data[34:36])[0] if len(data) >= 36 else 0
    return {
        "codec": "wav",
        "lossless": True,
        "sample_rate": sample_rate,
        "bit_depth": bit_depth,
        "mode": "lossless",
        "tier": TIER_LOSSLESS,
        "reason": f"WAV {bit_depth}-bit / {sample_rate} Hz",
    }


def _inspect_mp4(data: bytes, path: Path) -> dict[str, Any]:
    """ALAC and AAC both live in MP4; the codec box name is the discriminator.

    The `moov` atom holding that box may sit at either end of the file — ffmpeg
    writes it last unless `+faststart` moved it — so check the tail too.
    """
    probe = data
    size = path.stat().st_size
    if b"alac" not in probe and size > len(data):
        with path.open("rb") as handle:
            handle.seek(max(0, size - 256 * 1024))
            probe = data + handle.read()

    if b"alac" in probe:
        return {
            "codec": "alac",
            "lossless": True,
            "mode": "lossless",
            "tier": TIER_LOSSLESS,
            "reason": "Apple Lossless",
        }
    return {
        "codec": "aac",
        "lossless": False,
        "mode": "lossy",
        "tier": TIER_BELOW,
        "reason": "AAC is lossy — not 320 CBR or lossless",
    }


def inspect(
    path: Path | str, *, read_bytes: int = 256 * 1024
) -> dict[str, Any]:
    """Inspect one audio file and classify it into a quality tier."""
    path = Path(path)
    if not path.is_file():
        return {
            "path": str(path),
            "tier": TIER_UNKNOWN,
            "reason": "file not found",
        }

    with path.open("rb") as handle:
        data = handle.read(read_bytes)

    if data[:4] == b"fLaC":
        info = _inspect_flac(data)
    elif data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        info = _inspect_riff(data)
    elif data[:4] == b"FORM" and data[8:12] in (b"AIFF", b"AIFC"):
        info = {
            "codec": "aiff",
            "lossless": True,
            "mode": "lossless",
            "tier": TIER_LOSSLESS,
            "reason": "AIFF",
        }
    elif data[4:8] == b"ftyp":
        info = _inspect_mp4(data, path)
    elif data[:3] == b"ID3" or (len(data) > 1 and data[0] == 0xFF):
        info = _inspect_mp3(data)
    else:
        info = {
            "codec": "unknown",
            "tier": TIER_UNKNOWN,
            "reason": "unrecognised container",
        }

    info["path"] = str(path)
    info["size_bytes"] = path.stat().st_size
    return info


def verdict(
    info: dict[str, Any], *, allow_tiers: tuple[str, ...] = DEFAULT_ELIGIBLE
) -> dict[str, Any]:
    """Apply the gate. `eligible` decides whether a file may be
    indexed."""
    tier = info.get("tier", TIER_UNKNOWN)
    eligible = tier in allow_tiers
    return {
        **info,
        "eligible": eligible,
        "gate": "pass" if eligible else "refused",
        "allowed_tiers": list(allow_tiers),
    }
