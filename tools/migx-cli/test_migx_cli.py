#!/usr/bin/env python3
"""Regression tests for the migx CLI. Offline — no network, no encoder.

Pins what a later change could silently break:
  - the output naming convention (P-07, one writer per artifact family)
  - the `migx.playlist-mirror/1` and `migx.want-list/1` shapes agents parse
  - the quality bar, which is a contract on the file not the pipeline
  - ISRC reading from both TSRC and TXXX, the strongest match key

PKCE/auth needs a live account and is not covered here.

Run: python3 tools/migx-cli/test_migx_cli.py   (exit 0 = pass)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from migx_cli import mirror, naming, quality, resolve, tags  # noqa: E402


def _id3(frames: dict[str, str], txxx: dict[str, str] | None = None) -> bytes:
    """Build a minimal ID3v2.4 tag (UTF-8 text frames + TXXX pairs)."""
    body = b""
    for fid, value in frames.items():
        payload = b"\x03" + value.encode("utf-8") + b"\x00"
        body += fid.encode("ascii") + _syncsafe_bytes(len(payload))
        body += b"\x00\x00" + payload
    for desc, value in (txxx or {}).items():
        payload = (
            b"\x03"
            + desc.encode("utf-8")
            + b"\x00"
            + value.encode("utf-8")
            + b"\x00"
        )
        body += b"TXXX" + _syncsafe_bytes(len(payload)) + b"\x00\x00" + payload
    return b"ID3\x04\x00\x00" + _syncsafe_bytes(len(body)) + body


def _syncsafe_bytes(n: int) -> bytes:
    return bytes(
        [(n >> 21) & 0x7F, (n >> 14) & 0x7F, (n >> 7) & 0x7F, n & 0x7F]
    )


def _mp3(bitrate_idx: int, frames: int = 40) -> bytes:
    """Synthesise a CBR MPEG-1 Layer III stream (no Xing tag) at one bitrate.

    Header: FF FB <bitrate_idx><rate=44100> <stereo>. Verified against ffmpeg-
    encoded files during development; kept synthetic so tests need no encoder.
    """
    table = {14: 320, 9: 128, 11: 192}
    kbps = table[bitrate_idx]
    frame_len = int(144 * kbps * 1000 / 44100)
    header = bytes([0xFF, 0xFB, (bitrate_idx << 4) | 0x00, 0x00])
    return (header + b"\x00" * (frame_len - 4)) * frames


def _wav(sample_rate: int = 44100, bits: int = 16) -> bytes:
    return (
        b"RIFF"
        + (36).to_bytes(4, "little")
        + b"WAVEfmt "
        + (16).to_bytes(4, "little")
        + (1).to_bytes(2, "little")
        + (2).to_bytes(2, "little")
        + sample_rate.to_bytes(4, "little")
        + (0).to_bytes(4, "little")
        + (4).to_bytes(2, "little")
        + bits.to_bytes(2, "little")
        + b"data"
        + (0).to_bytes(4, "little")
    )


def _flac(sample_rate: int = 44100, bits: int = 16) -> bytes:
    packed = (sample_rate << 44) | ((bits - 1) << 36)
    return (
        b"fLaC"
        + b"\x00"
        + (34).to_bytes(3, "big")
        + b"\x00" * 10
        + packed.to_bytes(8, "big")
        + b"\x00" * 16
    )


def _track(**over):
    track = {
        "type": "track",
        "id": "4cOdK2wGLETKBW3PvgPWqT",
        "uri": "spotify:track:4cOdK2wGLETKBW3PvgPWqT",
        "name": "Never Gonna Give You Up",
        "artists": [{"name": "Rick Astley"}],
        "album": {
            "name": "Whenever You Need Somebody",
            "artists": [{"name": "Rick Astley"}],
            "release_date": "1987-11-16",
        },
        "track_number": 1,
        "disc_number": 1,
        "duration_ms": 213573,
        "external_ids": {"isrc": "GBARL9300135"},
        "explicit": False,
    }
    track.update(over)
    return track


def main() -> int:
    failures = []

    def check(cond, desc):
        if not cond:
            failures.append(desc)

    # ---- naming: sanitisation and template rendering
    check(
        naming.sanitize("AC/DC") == "AC-DC", "slash is replaced, not dropped"
    )
    check(naming.sanitize("") == "Unknown", "empty falls back")
    check(
        naming.sanitize("  spaced   out  ") == "spaced out",
        "whitespace collapses",
    )
    check(
        not naming.sanitize("a" * 400).__len__() > 120,
        "long names are truncated",
    )
    check(naming.sanitize("Björk") == "Björk", "non-ASCII survives")
    check(naming.sanitize("trailing.") == "trailing", "trailing dot stripped")

    doc = mirror.build(
        source_id="p1",
        source_name="Test List",
        owner="me",
        items=[{"track": _track(), "added_at": "2026-08-01T10:00:00Z"}],
        captured_at="2026-08-07T12:00:00Z",
    )
    entry = doc["tracks"][0]

    rendered = naming.render(entry)
    check(
        rendered == "Rick Astley/Whenever You Need Somebody/01 - "
        "Never Gonna Give You Up.mp3",
        f"library template: got {rendered}",
    )
    check(
        naming.render(entry, template=naming.TEMPLATE_FLAT)
        == "Rick Astley - Never Gonna Give You Up.mp3",
        "flat template",
    )
    check(not naming.render(entry).startswith("/"), "never absolute")

    # ---- mirror document shape (the agent-facing contract)
    check(doc["schema"] == "migx.playlist-mirror/1", "schema string pinned")
    check(doc["track_count"] == 1, "counts tracks")
    check(
        doc["captured_week"] == "2026-W32",
        f"iso week: got {doc['captured_week']}",
    )
    check(
        entry["isrc"] == "GBARL9300135",
        "isrc is carried (the resolve join key)",
    )
    check(entry["position"] == 0, "position recorded for order fidelity")
    check(entry["added_at"] == "2026-08-01T10:00:00Z", "added_at preserved")
    check(
        "preview_url" not in entry and "audio" not in entry,
        "mirror carries identity only, never audio",
    )

    # ---- non-track items are skipped, not crashed on
    mixed = mirror.build(
        source_id="p2",
        source_name="Mixed",
        owner="me",
        items=[
            {"track": _track(), "added_at": None},
            {"track": {"type": "episode", "id": "e1"}, "added_at": None},
            {"track": None, "added_at": None},
        ],
        captured_at="2026-08-07T12:00:00Z",
    )
    check(mixed["track_count"] == 1, "only tracks counted")
    check(
        mixed["skipped_count"] == 2,
        f"skips reported: got {mixed['skipped_count']}",
    )
    check(
        mixed["tracks"][0]["position"] == 0,
        "positions stay contiguous after skips",
    )

    # ---- missing fields degrade instead of raising
    bare = mirror.build(
        source_id="p3",
        source_name="Bare",
        owner=None,
        items=[
            {
                "track": {"type": "track", "id": "x", "name": "No Album"},
                "added_at": None,
            },
        ],
        captured_at="2026-08-07T12:00:00Z",
    )
    bare_path = naming.render(bare["tracks"][0])
    check(
        bare_path == "Unknown Artist/Unknown Album/00 - No Album.mp3",
        f"missing metadata degrades: got {bare_path}",
    )

    check(
        mirror.slug("Discover Weekly!!") == "discover-weekly", "slug is stable"
    )
    check(
        mirror.default_path(Path("/tmp"), doc).name
        == "test-list-2026-W32.json",
        "weekly snapshot path",
    )

    # ---- quality gate: the bar is a contract on the file, not the pipeline
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        cases = [
            ("cbr320.mp3", _mp3(14), quality.TIER_MP3_320, True),
            ("cbr128.mp3", _mp3(9), quality.TIER_BELOW, False),
            ("cbr192.mp3", _mp3(11), quality.TIER_BELOW, False),
            ("track.wav", _wav(), quality.TIER_LOSSLESS, True),
            ("track.flac", _flac(), quality.TIER_LOSSLESS, True),
        ]
        for name, blob, want_tier, want_ok in cases:
            path = root / name
            path.write_bytes(blob)
            got = quality.verdict(quality.inspect(path))
            check(
                got["tier"] == want_tier,
                f"{name}: tier {got['tier']} != {want_tier}",
            )
            check(
                got["eligible"] is want_ok,
                f"{name}: eligible {got['eligible']} != {want_ok}",
            )

        # 320 CBR is the only MP3 that passes by default — that is
        # the whole point.
        mp3_320 = quality.inspect(root / "cbr320.mp3")
        check(
            mp3_320["bitrate_kbps"] == 320,
            f"320 read as {mp3_320['bitrate_kbps']}",
        )
        check(mp3_320["mode"] == "cbr", "constant bitrate detected")

        # A refused tier can be opted into explicitly, never silently.
        low = quality.inspect(root / "cbr128.mp3")
        check(
            quality.verdict(low)["eligible"] is False, "128 refused by default"
        )
        check(
            quality.verdict(low, allow_tiers=(quality.TIER_BELOW,))["eligible"]
            is True,
            "explicit override is possible",
        )

        missing = quality.verdict(quality.inspect(root / "nope.mp3"))
        check(
            missing["tier"] == quality.TIER_UNKNOWN, "missing file is unknown"
        )
        check(missing["eligible"] is False, "unknown never passes the gate")

    # ---- match normalisation: store metadata never matches Spotify exactly
    check(
        resolve.normalise("Windowlicker (Original Mix)")
        == resolve.normalise("Windowlicker"),
        "(Original Mix) is stripped for matching",
    )
    check(
        resolve.normalise("Song (feat. Someone)") == resolve.normalise("Song"),
        "featured-artist suffix stripped",
    )
    check(
        resolve.normalise("Track - Remastered 2011")
        == resolve.normalise("Track"),
        "remaster suffix stripped",
    )
    check(
        resolve.normalise("Björk") == resolve.normalise("Bjork"),
        "accents fold for matching",
    )
    check(
        resolve.normalise("Song") != resolve.normalise("Other Song"),
        "normalisation does not collapse distinct titles",
    )

    # ---- tags: ISRC lives in TSRC *or* TXXX depending on the tagger
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        lib = root / "music"
        lib.mkdir()

        (lib / "a.mp3").write_bytes(
            _id3(
                {"TIT2": "Never Gonna Give You Up", "TPE1": "Rick Astley"},
                txxx={"ISRC": "GBARL9300135"},
            )
            + _mp3(14)
        )
        (lib / "b.mp3").write_bytes(
            _id3(
                {
                    "TIT2": "Blue Monday",
                    "TPE1": "New Order",
                    "TSRC": "GBZZZ1111111",
                }
            )
            + _mp3(9)
        )

        meta_a = tags.read(lib / "a.mp3")
        check(meta_a.get("isrc") == "GBARL9300135", "TXXX:ISRC is read")
        check(meta_a.get("title") == "Never Gonna Give You Up", "TIT2 read")
        meta_b = tags.read(lib / "b.mp3")
        check(meta_b.get("isrc") == "GBZZZ1111111", "TSRC is read")

        # ---- resolver: ISRC wins, and below-bar is an upgrade not a re-buy
        resolver = resolve.LocalFilesResolver([lib])
        resolver.scan()
        check(resolver.scanned == 2, f"scanned {resolver.scanned} != 2")

        doc = {
            "schema": "migx.playlist-mirror/1",
            "source_name": "T",
            "captured_week": "2026-W32",
            "tracks": [
                {
                    "position": 0,
                    "title": "Never Gonna Give You Up (Remaster)",
                    "artists": ["Rick Astley"],
                    "isrc": "GBARL9300135",
                },
                {
                    "position": 1,
                    "title": "Blue Monday",
                    "artists": ["New Order"],
                    "isrc": "GBAAA8300001",
                },
                {
                    "position": 2,
                    "title": "Not Owned",
                    "artists": ["Nobody"],
                    "isrc": "GBZZZ0000001",
                },
            ],
        }
        report = resolve.resolve_mirror(doc, resolver)
        check(report["resolved_count"] == 1, "one track meets the bar")
        check(report["below_bar_count"] == 1, "one owned but below bar")
        check(report["missing_count"] == 1, "one genuinely absent")
        check(
            report["resolved"][0]["method"] == "isrc",
            "ISRC matched despite the differing title",
        )
        check(
            report["below_bar"][0]["method"] == "artist+title",
            "fuzzy match used when ISRC differs",
        )

        want = resolve.want_list(report)
        wants = {i["title"]: i["want"] for i in want["items"]}
        check(wants.get("Not Owned") == "acquire", "absent track -> acquire")
        check(
            wants.get("Blue Monday") == "upgrade",
            "owned-but-low track -> upgrade, never a re-buy",
        )
        check(want["schema"] == "migx.want-list/1", "want-list schema pinned")

    for f in failures:
        print(f"FAIL: {f}", file=sys.stderr)
    print(
        f"{'FAILED' if failures else 'ok'} — migx-cli naming + mirror"
        f" + quality gate + tags + resolver "
        f"({len(failures)} failure(s))"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
