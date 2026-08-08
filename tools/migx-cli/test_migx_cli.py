#!/usr/bin/env python3
"""Regression tests for the migx CLI. Offline — no network, no encoder.

Pins what a later change could silently break:
  - the output naming convention (P-07, one writer per artifact family)
  - the `migx.playlist-mirror/1` and `migx.gap-list/1` shapes agents parse
  - the quality bar, which is a contract on the file not the pipeline
  - ISRC reading from both TSRC and TXXX, the strongest match key

PKCE/auth needs a live account and is not covered here.

Run: python3 tools/migx-cli/test_migx_cli.py   (exit 0 = pass)
"""

import os
import shutil
import struct
import sys
import tempfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from migx_cli import (  # noqa: E402
    analyze,
    api,
    auth,
    feedback,
    ingest,
    keys,
    layout,
    mirror,
    mixing,
    naming,
    quality,
    ratelimit,
    resolve,
    session,
    sidecar,
    spark,
    tags,
    termart,
    tui,
    watch,
)  # noqa: E402 — path insert above


def _gradient_png(width: int = 64, height: int = 64) -> bytes:
    """Truecolour gradient PNG (no deps). Solid colours can paint as blanks
    in chafa mono mode; a gradient always yields glyphs."""
    rows = []
    for y in range(height):
        row = b"\x00"
        for x in range(width):
            row += bytes([(x * 4) % 256, (y * 4) % 256, 128])
        rows.append(row)
    compressed = zlib.compress(b"".join(rows), 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )


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

        # ---- resolver: ISRC wins; below-bar is upgrade, not missing
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
            report["below_bar"][0]["method"] == "scored",
            "scored match used when ISRC differs",
        )

        gaps = resolve.gap_list(report)
        statuses = {i["title"]: i["status"] for i in gaps["items"]}
        check(
            statuses.get("Not Owned") == "missing", "absent track -> missing"
        )
        check(
            statuses.get("Blue Monday") == "upgrade",
            "owned-but-low track -> upgrade, not a second missing entry",
        )
        check(gaps["schema"] == "migx.gap-list/1", "gap-list schema pinned")

    # ---- mixing: can these two be mixed, and how
    same = mixing.tempo(125.0, 125.0)
    check(same["drift_pct"] == 0.0, "identical tempo has no drift")
    half = mixing.tempo(128.0, 64.0)
    check(
        half["drift_pct"] == 0.0,
        "half-time is beatmixable, not a 50% clash",
    )
    check(
        mixing.tempo(None, 125.0)["score"] is None,
        "unknown bpm scores nothing rather than guessing",
    )
    check(mixing.harmonic("8A", "8A")["relation"] == "same", "same key")
    check(mixing.harmonic("8A", "9A")["compatible"], "wheel neighbour")
    check(mixing.harmonic("8A", "8B")["compatible"], "relative major")
    check(
        mixing.harmonic("8A", "3B")["compatible"] is False,
        "distant keys are reported as a clash",
    )
    check(
        mixing.harmonic("8A", None)["compatible"] is None,
        "unknown key is unknown, not a clash",
    )

    tight = {"bpm": 125, "camelot": "8A", "cues": [], "energy": []}
    far = {"bpm": 70, "camelot": "3B", "cues": [], "energy": []}
    ranked = mixing.techniques(tight, dict(tight))
    check(
        [t["name"] for t in ranked][0] in ("Bass Swap", "Long Blend"),
        f"a perfect pair favours a blend: got {ranked[0]['name']}",
    )
    rescue = mixing.techniques(tight, far)
    check(
        rescue[0]["name"] == "Echo Out",
        f"an incompatible pair favours the rescue: got {rescue[0]['name']}",
    )
    check(
        all(t["why"] for t in rescue),
        "every technique explains itself — a bare score is not advice",
    )
    check(
        {t["name"] for t in ranked} == set(mixing.TECHNIQUES),
        "every technique is ranked, not just the winner",
    )

    # ---- beatmatch: the number a DJ actually needs before a blend
    bm = mixing.beatmatch(125, 128)
    check(bm["direction"] == "down", "faster incoming means pitching down")
    check(abs(bm["pitch_pct"] + 2.34) < 0.1, f"pitch %: {bm['pitch_pct']}")
    check(bm["fits_range"] == "±8%", "a small move fits a standard fader")
    check(
        mixing.beatmatch(128, 64)["pitch_pct"] == 0.0,
        "half-time needs no pitch at all, not a 50% move",
    )
    check(
        mixing.beatmatch(128, 64)["relation"] == "double-time",
        "and the relation is named so it is not a mystery zero",
    )
    check(
        mixing.beatmatch(100, 100)["bar_s"] == 2.4,
        "a bar at 100 BPM is 2.4s",
    )
    check(
        mixing.beatmatch(120, 120)["phrase_s"] == 64.0,
        "32 bars at 120 BPM is 64s — blends are planned in bars",
    )
    check(
        mixing.beatmatch(None, 128)["possible"] is None,
        "unknown bpm is unknown, not impossible",
    )

    # ---- ARRANGE: find and sort, which is the core job
    lib = [
        {
            "name": "A",
            "bpm": 128,
            "camelot": "8A",
            "tags": ["peak"],
            "notes": "",
            "artist": "X",
            "duration_s": 300,
            "tier": "lossless",
        },
        {
            "name": "B",
            "bpm": None,
            "camelot": None,
            "tags": [],
            "notes": "",
            "artist": "Y",
            "duration_s": None,
            "tier": "mp3-320-cbr",
        },
        {
            "name": "C",
            "bpm": 122,
            "camelot": "3A",
            "tags": ["girly"],
            "notes": "warm",
            "artist": "Z",
            "duration_s": 200,
            "tier": "lossless",
        },
    ]
    by_bpm = tui.sort_collection(lib, "bpm")
    check(
        [c["bpm"] for c in by_bpm] == [122, 128, None],
        f"unknown bpm sorts LAST, not as zero: {[c['bpm'] for c in by_bpm]}",
    )
    by_key = tui.sort_collection(lib, "key")
    check(
        [c["camelot"] for c in by_key][:2] == ["3A", "8A"],
        "key sorts round the wheel so neighbours sit together",
    )
    check(len(tui.filter_collection(lib, "girly")) == 1, "tags are searchable")
    check(len(tui.filter_collection(lib, "warm")) == 1, "notes are searchable")
    check(len(tui.filter_collection(lib, "8a")) == 1, "key is searchable")
    check(
        [c["name"] for c in tui.filter_collection(lib, "120-125")] == ["C"],
        "a BPM range filters on tempo",
    )
    check(
        len(tui.filter_collection(lib, "")) == 3,
        "an empty query filters out nothing",
    )

    # ---- waveform + heat: the single-track view
    check(spark.waveform([], 10, 4) == [], "no curve, no waveform")
    wf = spark.waveform([0.1, 1.0], 8, 4)
    check(len(wf) == 4, "one entry per row")
    check(all(len(text) == 8 for text, _ in wf), "rows are `width` wide")
    check(all(len(heats) == 8 for _, heats in wf), "one heat band per column")
    # Loud columns must reach the top row; that is what makes it a waveform.
    # Curves are normalised so the peak is 1.0; that column fills the top row.
    check("█" in wf[0][0], "a full-scale column reaches the top row")
    check(
        "█" not in spark.waveform([0.1, 0.9], 8, 4)[0][0],
        "a 0.9 column stops short of the top — partial blocks, not rounding up",
    )
    check(wf[-1][0].strip() != "", "the bottom row is filled for any signal")
    check(
        spark.heat(0.0) == 0 and spark.heat(1.0) == spark.HEAT_LEVELS - 1,
        "heat spans the full band range",
    )
    check(spark.heat(-5) == 0, "negative energy clamps to the coolest band")
    axis = spark.time_axis(120, 40)
    check("0:00" in axis and "2:00" in axis, f"time axis ends: {axis!r}")
    check(len(axis) == 40, "axis matches the width")
    check(spark.time_axis(0, 40) == "", "no duration, no axis")

    # ---- sparkline: shape of a track in one line, with cue markers
    check(spark.sparkline([], 10) == "", "empty curve renders empty")
    check(len(spark.sparkline([0.5] * 64, 24)) == 24, "resamples to width")
    check(
        spark.sparkline([0.0, 1.0], 2)[0] == spark.BLOCKS[0]
        and spark.sparkline([0.0, 1.0], 2)[1] == spark.BLOCKS[-1],
        "0 and 1 map to the lowest and highest block",
    )
    # Downsampling must average, not sample — dropping peaks between samples
    # would hide exactly the drops a DJ is looking for.
    check(
        spark.sparkline([0.0, 1.0, 0.0, 1.0], 2)
        == spark.sparkline([0.5, 0.5], 2),
        "downsampling averages rather than dropping values",
    )

    ruler = spark.cue_ruler(
        [{"position": 0, "label": "start"}, {"position": 100, "label": "end"}],
        100,
        10,
    )
    check(ruler and ruler[0][0] == "▲", "first cue marks column 0")
    check(ruler[0][-1] == "▲", "a cue at the end lands in the last column")
    check(
        spark.cue_ruler([{"position": 5}], 0, 10) == [],
        "unknown duration draws no ruler rather than a wrong one",
    )
    check(spark.cue_ruler([], 100, 10) == [], "no cues, no ruler")

    # ---- watch: a file still downloading must never be filed
    with tempfile.TemporaryDirectory() as tmp:
        inbox = Path(tmp)
        exts = {".mp3"}
        seen: dict = {}
        growing = inbox / "downloading.mp3"
        growing.write_bytes(b"x" * 1000)
        clock = 1000.0

        for step in range(4):
            clock += 10
            growing.write_bytes(b"x" * (1000 + step * 500))
            ready = watch.stable_files(inbox, exts, seen, 20.0, now=clock)
            check(not ready, "a growing file is never ready")

        clock += 30  # it stops changing
        ready = watch.stable_files(inbox, exts, seen, 20.0, now=clock)
        check(
            [p.name for p in ready] == ["downloading.mp3"],
            "a quiet file becomes ready once settled",
        )

        # Downloader debris shares the inbox and is never audio.
        (inbox / "subs.srt").write_bytes(b"x")
        (inbox / "half.crdownload").write_bytes(b"x")
        (inbox / ".thumb").mkdir()
        (inbox / ".thumb" / "art.mp3").write_bytes(b"x")
        (inbox / watch.FILED_DIR).mkdir()
        (inbox / watch.FILED_DIR / "done.mp3").write_bytes(b"x")
        clock += 60
        names = {
            p.name
            for p in watch.stable_files(inbox, exts, seen, 20.0, now=clock)
        }
        check(names == {"downloading.mp3"}, f"debris ignored: got {names}")

        # Parking must move, never delete.
        parked = watch.park(inbox / "downloading.mp3", inbox)
        check(parked is not None and parked.is_file(), "parked file exists")
        check(
            not (inbox / "downloading.mp3").exists(),
            "parking removes it from the inbox root",
        )
        check(
            parked.parent.name == watch.FILED_DIR,
            "parked into _filed/, not deleted",
        )

    # ---- analyze: results land in the sidecar without losing notes
    with tempfile.TemporaryDirectory() as tmp:
        audio = Path(tmp) / "A - B.mp3"
        audio.write_bytes(_mp3(14))
        sidecar.set_note(audio, note="keep me", tags=["keep"])
        sidecar.add_cue(audio, 30.0, "cue stays")
        analyze.store({"path": str(audio), "bpm": 128.0, "key": "Am"})
        side = sidecar.read(audio)
        check(side.get("bpm") == 128.0, "analysis stores bpm")
        check(side.get("key") == "Am", "analysis stores key text")
        check(side.get("camelot") == "8A", "key is folded to Camelot")
        check(side.get("notes") == "keep me", "analysis preserves notes")
        check(len(side.get("cues") or []) == 1, "analysis preserves cues")
        # An implausible tempo must not be written into a filename.
        analyze.store({"path": str(audio), "bpm": 0})
        check(
            sidecar.read(audio)["bpm"] == 128.0, "junk bpm does not overwrite"
        )

    # ---- sidecar: notes + cues, and never clobber the analyzer's work
    check(sidecar.parse_position("90") == 90.0, "bare seconds")
    check(sidecar.parse_position("1:30") == 90.0, "mm:ss")
    check(sidecar.parse_position("1m30s") == 90.0, "1m30s")
    check(sidecar.parse_position("1:01:00") == 3660.0, "hh:mm:ss")
    check(sidecar.fmt_position(275) == "4:35", "position formats back")
    check(sidecar.fmt_position(None) == "--:--", "unknown position is safe")

    with tempfile.TemporaryDirectory() as tmp:
        audio = Path(tmp) / "Artist - Title.mp3"
        audio.write_bytes(_mp3(14))
        check(
            sidecar.read(audio) == {}, "no sidecar reads as empty, not error"
        )

        # Pretend the analyzer got there first.
        sidecar.write(
            audio,
            {
                "bpm": 124.0,
                "key": "Am",
                "energy_curve": {"points": [0.1, 0.9]},
            },
        )
        sidecar.set_note(audio, note="girly song", tags=["girly"])
        sidecar.add_cue(audio, 275.0, "mix out here")
        sidecar.add_cue(audio, 62.0, "intro over")
        data = sidecar.read(audio)

        check(data.get("bpm") == 124.0, "note write preserves analyzer bpm")
        check(data.get("key") == "Am", "note write preserves key")
        check("energy_curve" in data, "note write preserves energy curve")
        check(data.get("notes") == "girly song", "note stored")
        check(data.get("tags") == ["girly"], "tag stored")
        check(len(data.get("cues") or []) == 2, "both cues stored")
        check(
            [c["position"] for c in data["cues"]] == [62.0, 275.0],
            "cues are kept sorted by position",
        )
        check(
            data["cues"][0]["label"] == "intro over",
            "cue label survives the sort",
        )

        sidecar.set_note(audio, tags=["peak"], append=True)
        check(
            sidecar.read(audio)["tags"] == ["girly", "peak"],
            "append extends tags instead of replacing",
        )
        check(
            sidecar.read(audio).get("notes") == "girly song",
            "appending a tag leaves the note alone",
        )
        # The sidecar lives inside Collection; nothing may treat it as audio.
        check(
            sidecar.track_file(audio).suffix == ".json",
            "sidecar is track.json inside <audio>.migx/",
        )

    # ---- TUI: the snapshot is pure data, so it is testable without a screen
    snap = tui.snapshot()
    for field in (
        "library_root",
        "mirror_count",
        "collection_count",
        "missing_count",
        "template",
    ):
        check(field in snap, f"snapshot carries {field}")
    check(isinstance(snap["mirrors"], list), "mirrors is a list")
    check("Track" in tui.PANES, "single-track mode exists")
    check("Deck" in tui.PANES, "dual-deck mode exists")
    check(
        tui.deck_view(None, None)[0][1] is None,
        "deck with no selection renders guidance",
    )
    check(
        {"Library", "Arrange", "Prep"} <= set(tui.PANES),
        "modes use the house vocabulary (ADR-007)",
    )
    check(
        tui.track_view(None) and tui.track_view(None)[0][1] is None,
        "no selection renders guidance, not a crash",
    )
    for pane in tui.PANES:
        rows = tui._rows(pane, snap)
        check(isinstance(rows, list), f"{pane} renders a list of lines")
        check(all(isinstance(r, str) for r in rows), f"{pane} rows are str")
    # An empty library must render guidance, never a traceback.
    blank = {
        **snap,
        "collection": [],
        "mirrors": [],
        "gaps": [],
        "crates": [],
        "collection_count": 0,
        "mirror_count": 0,
        "mirror_tracks": 0,
        "analysed_count": 0,
        "missing_count": 0,
        "upgrade_count": 0,
    }
    for pane in tui.PANES:
        rows = tui._rows(pane, blank)
        check(len(rows) > 0, f"{pane} renders something when empty")

    # ---- key notation: every tagger's spelling folds to one Camelot value
    for raw, want in [
        ("Am", "8A"),
        ("A", "11B"),
        ("AM", "11B"),
        ("F#m", "11A"),
        ("Gbm", "11A"),  # enharmonic
        ("8A", "8A"),
        ("8a", "8A"),  # already Camelot
        ("10m", "5A"),
        ("10d", "5B"),  # Open Key
        ("Bbm", "3A"),
        ("Ebm", "2A"),
        ("Dbm", "12A"),
        ("F minor", "4A"),
        ("C Major", "8B"),
        ("A min", "8A"),
    ]:
        got = keys.to_camelot(raw)
        check(got == want, f"key {raw!r} -> {got} (want {want})")

    for junk in ["", None, "junk", "H", "Amazing", "  "]:
        check(
            keys.to_camelot(junk) is None,
            f"unparsable key {junk!r} yields None, never a wrong key",
        )
    check(
        keys.to_camelot("F#m") == keys.to_camelot("Gbm"),
        "enharmonic spellings agree",
    )

    check(keys.parse_bpm("128") == 128.0, "bpm string parses")
    check(keys.parse_bpm("126,5") == 126.5, "comma decimal (EU taggers)")
    for junk in ["0", "999", "abc", None, ""]:
        check(
            keys.parse_bpm(junk) is None,
            f"implausible bpm {junk!r} rejected rather than written to a name",
        )

    # ---- smart_split: boundary-aware truncation (spotDL-adapted)
    long_name = (
        "Blue Monday - Halo Varga Vocal Extended Club Remix "
        "Special Edition Version"
    )
    check(
        naming.smart_split("Short", 40) == "Short",
        "short strings pass through untouched",
    )
    check(
        naming.smart_split(long_name, 40)
        == "Blue Monday - Halo Varga Vocal Extended",
        f"cuts on a boundary: got {naming.smart_split(long_name, 40)!r}",
    )
    check(
        len(naming.smart_split(long_name, 25)) <= 25,
        "never exceeds the budget",
    )
    check(
        not naming.smart_split(long_name, 40).endswith((" ", "-", ",")),
        "no dangling separator",
    )
    check(
        naming.smart_split("A" * 50, 20) == "A" * 20,
        "falls back to a hard slice when there is no separator",
    )
    # The whole point: keep more than the first fragment.
    check(
        len(naming.smart_split(long_name, 40)) > len("Blue Monday"),
        "keeps the longest fitting result, not the first separator's",
    )

    # ---- curated template tokens (only what the mirror carries)
    set_entry = {
        "artists": ["Amelie Lens"],
        "title": "Feel It",
        "position": 4,
        "list_name": "Peak Time",
        "spotify_id": "abc123",
        "duration_ms": 321000,
    }
    check(
        naming.render(set_entry, template=naming.TEMPLATE_SET)
        == "005 - Amelie Lens - Feel It.mp3",
        "list-position is 1-based and zero-padded for sort order",
    )
    check(
        naming.render(set_entry, template="{duration}.{ext}") == "5-21.mp3",
        "duration renders mm-ss (colon shows as / in Finder)",
    )
    check(
        naming.render(set_entry, template="{spotify-id}.{ext}")
        == "abc123.mp3",
        "spotify-id token",
    )
    check(
        naming.render(
            {},
            template="{list-position}|{list-name}" "|{spotify-id}|{duration}",
        )
        == "000|Playlist|nospotifyid|0-00",
        "every new token degrades instead of raising",
    )

    # ---- resolver registry: discoverable by name, unknown names fail loudly
    check(
        resolve.available() == ["local-files"],
        f"core ships one resolver: got {resolve.available()}",
    )
    check(
        isinstance(
            resolve.get_resolver("local-files", []),
            resolve.LocalFilesResolver,
        ),
        "registry builds the local resolver",
    )
    try:
        resolve.get_resolver("youtube", [])
        check(False, "unknown resolver must raise")
    except ValueError as exc:
        check("known:" in str(exc), "unknown resolver lists the known names")

    # ---- scoring: the DJ inversion of spotDL's variant handling
    check(
        resolve.variants("Song (Extended Mix)")
        == frozenset({"extended", "mix"}),
        "variant tokens extracted",
    )
    check(
        resolve.variants("Song (Original Mix)") == frozenset(),
        "'original mix' is noise, stripped before variant extraction",
    )
    check(
        resolve.score_candidate(
            {"title": "Feel It", "artists": ["Amelie Lens"]},
            {"title": "Feel It", "artist": "Amelie Lens"},
        )
        is not None,
        "identical track scores a match",
    )
    check(
        resolve.score_candidate(
            {"title": "Feel It", "artists": ["Amelie Lens"]},
            {"title": "Feel It (Extended Mix)", "artist": "Amelie Lens"},
        )
        is None,
        "an extended mix is NOT the original — the DJ inversion",
    )
    check(
        resolve.score_candidate(
            {"title": "Feel It (Remix)", "artists": ["Amelie Lens"]},
            {"title": "Feel It (Remix)", "artist": "Amelie Lens"},
        )
        is not None,
        "matching variants still match — remix is not penalised per se",
    )
    check(
        resolve.score_candidate(
            {"title": "Feel It", "artists": ["Amelie Lens"]},
            {"title": "Feel It", "artist": "Someone Else"},
        )
        is None,
        "same title, wrong artist is rejected",
    )
    # A store may credit the featured artist as `artist` and the headliner as
    # `album_artist`. Beatport did exactly that for Jon Hopkins / Imogen Heap,
    # and scoring only `artist` rejected a track bought off the want-list.
    check(
        resolve.score_candidate(
            {"title": "Reckoning", "artists": ["Jon Hopkins"]},
            {
                "title": "Reckoning",
                "artist": "Imogen Heap",
                "album_artist": "Jon Hopkins",
            },
        )
        is not None,
        "matches when the headliner is only in album_artist",
    )
    check(
        resolve.score_candidate(
            {"title": "Reckoning", "artists": ["Jon Hopkins"]},
            {
                "title": "Reckoning",
                "artist": "Someone Else",
                "album_artist": "Nobody At All",
            },
        )
        is None,
        "both artist fields wrong is still rejected",
    )
    check(
        resolve.score_candidate(
            {
                "title": "Feel It",
                "artists": ["Amelie Lens"],
                "duration_ms": 300000,
            },
            {"title": "Feel It", "artist": "Amelie Lens", "duration_s": 30.0},
        )
        is None,
        "a 4.5-minute gap in duration rejects the match",
    )
    check(
        resolve.score_candidate(
            {
                "title": "Feel It",
                "artists": ["Amelie Lens"],
                "duration_ms": 300000,
            },
            {"title": "Feel It", "artist": "Amelie Lens", "duration_s": 300.5},
        )
        is not None,
        "a matching duration confirms",
    )
    check(
        resolve.time_score(None, 300.0) is None
        and resolve.time_score(300000, None) is None,
        "unknown duration scores None rather than penalising",
    )

    # ---- DJ naming: the prefix appears only once the track is analysed
    analysed = {
        "artists": ["Amelie Lens"],
        "title": "Feel It",
        "bpm": 128,
        "camelot": "8A",
    }
    check(
        naming.render(analysed, template=naming.TEMPLATE_DJ)
        == "128 8A - Amelie Lens - Feel It.mp3",
        "dj template renders BPM and key",
    )
    check(
        naming.render(
            {"artists": ["X"], "title": "Y"}, template=naming.TEMPLATE_DJ
        )
        == "X - Y.mp3",
        "unanalysed track drops the BPM/key prefix instead of writing 000 --",
    )
    check(
        naming.render(
            {"artists": ["X"], "title": "Y", "bpm": 99, "camelot": "1A"},
            template=naming.TEMPLATE_DJ,
        )
        == "099 1A - X - Y.mp3",
        "BPM zero-pads to 3 so 099 sorts before 128",
    )

    # ---- layout: shelves, symlinks, and the SSoT invariant
    check(layout.alpha_bucket("Burial") == "B", "letter shelf")
    check(layout.alpha_bucket("2 Bad Mice") == "0-9", "digit shelf")
    check(layout.alpha_bucket("") == "#", "unknown shelf")
    check(layout.alpha_bucket("Ólafur Arnalds") == "#", "non-ASCII initial")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        track = layout.collection_dir(root) / "R" / "Rick - Never.mp3"
        track.parent.mkdir(parents=True)
        track.write_bytes(_id3({"TIT2": "Never"}) + _mp3(14))

        crate = layout.crate_dir(root, "Night - Club X")
        link = layout.link_into_crate(track, crate)

        # Hardlink by default: a symlink is 49 bytes on disk, and DJ software
        # that does not dereference it reads those 49 bytes as a broken track.
        check(not link.is_symlink(), "crate entry is not a symlink by default")
        check(link.samefile(track), "crate entry is the same inode")
        check(
            link.stat().st_size == track.stat().st_size,
            "crate entry reports the real size, not a link's 49 bytes",
        )
        check(link.stat().st_nlink >= 2, "two names, one inode")

        # Re-linking must be a no-op so crate.sync is safe to re-run.
        again = layout.link_into_crate(track, crate)
        check(again == link, "re-linking is idempotent")
        check(link.samefile(track), "re-link did not break the identity")

        # Deleting a crate must never cost audio — the whole invariant.
        shutil.rmtree(crate)
        check(track.is_file(), "deleting a crate leaves the audio intact")

        # Symlink mode stays available and stays relative (portable tree).
        crate2 = layout.crate_dir(root, "Sym Night")
        slink = layout.link_into_crate(track, crate2, mode=layout.SYMLINK)
        check(slink.is_symlink(), "symlink mode still produces a symlink")
        check(
            not str(os.readlink(slink)).startswith("/"),
            "symlink is relative so the tree stays movable",
        )
        check(slink.resolve() == track.resolve(), "symlink points at the file")
        shutil.rmtree(crate2)
        check(track.is_file(), "removing a symlink crate is also safe")

        m3u = layout.write_m3u8(
            layout.playlist_path(root, "Peak"),
            [
                {
                    "path": str(track),
                    "title": "Never",
                    "artists": ["Rick"],
                    "duration_ms": 213000,
                }
            ],
            root=root,
        )
        body = m3u.read_text()
        check(body.startswith("#EXTM3U"), "m3u8 header")
        check("#EXTINF:213,Rick - Never" in body, "EXTINF line")

    # ---- ingest: gate first, never overwrite, dry-run touches nothing
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        incoming = root / "incoming"
        incoming.mkdir()
        good = incoming / "good.mp3"
        good.write_bytes(
            _id3(
                {"TIT2": "Feel It", "TPE1": "Amelie Lens"},
                txxx={"ISRC": "GBAAA1111111"},
            )
            + _mp3(14)
        )
        low = incoming / "low.mp3"
        low.write_bytes(_id3({"TIT2": "Weak", "TPE1": "Someone"}) + _mp3(9))

        lib = root / "Library"
        dry = ingest.ingest([good, low], lib, dry_run=True)
        check(dry["filed_count"] == 1, "dry run counts the eligible file")
        check(dry["refused_count"] == 1, "dry run refuses the low file")
        check(
            not layout.collection_dir(lib).exists(),
            "dry run writes nothing to disk",
        )

        real = ingest.ingest([good, low], lib)
        check(real["filed_count"] == 1, "one file filed")
        filed = Path(real["filed"][0]["destination"])
        check(filed.is_file(), "the file actually landed")
        check(
            tags.read(filed).get("isrc") == "GBAAA1111111",
            "ISRC is written through so resolve matches exactly later",
        )

        rerun = ingest.ingest([good, low], lib)
        check(rerun["filed_count"] == 0, "re-ingest files nothing")
        check(
            rerun["duplicate_count"] == 1,
            "an existing Collection path is reported, never overwritten",
        )

    # ---- ingest copies cover art for library.art / Track TUI
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        inbox = root / "_Inbox"
        thumbs = inbox / ".thumb"
        thumbs.mkdir(parents=True)
        song = inbox / "Feel It.mp3"
        song.write_bytes(
            _id3(
                {"TIT2": "Feel It", "TPE1": "Amelie Lens"},
                txxx={"ISRC": "GBAAA2222222"},
            )
            + _mp3(14)
        )
        # Downloader-style thumb (fuzzy stem match).
        (thumbs / "Amelie Lens - Feel It (Official).png").write_bytes(
            _gradient_png(48, 48)
        )
        lib = root / "Library"
        report = ingest.ingest([song], lib, move=True)
        check(report["filed_count"] == 1, "filed with cover source available")
        dest = Path(report["filed"][0]["destination"])
        cover = dest.parent / "cover.png"
        check(cover.is_file(), f"cover.png placed beside audio, got {cover}")
        check(
            report["filed"][0].get("cover") == str(cover),
            "ingest report records cover path",
        )
        # termart must find it without the inbox anymore
        check(
            termart.find_cover(dest) == cover,
            "find_cover resolves filed cover.png",
        )
        check(not song.exists(), "move drained the inbox audio")

    # ---- Spotify Web API client rails (offline)
    try:
        api.assert_allowed_url("https://evil.example/v1/me")
        check(False, "non-API host must be refused")
    except api.ApiError as exc:
        check("refusing request" in str(exc), "host allowlist message")
    try:
        api.assert_allowed_url("https://api.spotify.com/v1/me")
        check(True, "official API host is allowed")
    except api.ApiError:
        check(False, "official API host must pass allowlist")

    check(
        api.API_HOST == "api.spotify.com"
        and "api.spotify.com" in api.ALLOWED_HOSTS,
        "only the official Web API host is allowlisted",
    )
    check(
        set(auth.SCOPES)
        == {
            "user-library-read",
            "playlist-read-private",
            "playlist-read-collaborative",
        },
        "scopes stay read-only — no modify/streaming",
    )
    check(
        "playlist-modify" not in " ".join(auth.SCOPES)
        and "streaming" not in " ".join(auth.SCOPES),
        "never request write or streaming scopes",
    )
    check(
        auth.ACCOUNTS_HOST == "accounts.spotify.com",
        "OAuth only talks to accounts.spotify.com",
    )
    check(
        ratelimit.DEFAULT_MIN_INTERVAL_S >= 0.25,
        "default pacing is conservative (≥0.25s)",
    )
    check(api.MAX_CONSECUTIVE_429 >= 2, "circuit breaker is armed")

    # Pagination next links drop fields= — sticky re-apply must restore them.
    nxt = "https://api.spotify.com/v1/me/playlists?offset=50&limit=50"
    fixed = api.reapply_query_params(
        nxt, {"fields": "next,items(id,name,owner(display_name,id))"}
    )
    check(
        "fields=" in fixed and "offset=50" in fixed and "limit=50" in fixed,
        "sticky fields re-applied on pagination next without dropping offset",
    )
    check(
        "owner(display_name,id)" in api._PLAYLIST_LIST_FIELDS
        and "tracks(total)" not in api._PLAYLIST_LIST_FIELDS,
        "playlist list fields keep owner.id; drop dead tracks(total)",
    )

    # ---- termart / chafa cover preview (optional binary; always degrade)
    check(
        "\x1b[31m" not in termart.strip_ansi("\x1b[31mred\x1b[0m"),
        "strip_ansi removes CSI colour",
    )
    ph = termart._placeholder(20, 5, "no cover")
    check(len(ph) >= 3 and ph[0].startswith("┌"), "placeholder is a box")
    missing = termart.render("/no/such/cover.png", cols=20, rows=6)
    check(
        not missing["ok"] and missing["engine"] == "placeholder",
        "missing file degrades to placeholder",
    )
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        audio = td / "Song Title.mp3"
        audio.write_bytes(b"ID3")
        cover = td / "cover.png"
        cover.write_bytes(_gradient_png())
        found = termart.find_cover(audio)
        check(found == cover, f"find_cover sibling cover.png, got {found}")
        # Fuzzy thumb match under .thumb/
        thumb_dir = td / ".thumb"
        thumb_dir.mkdir()
        long = thumb_dir / "Artist - Song Title (Official Video).png"
        long.write_bytes(cover.read_bytes())
        near = td / "Song Title.mp3"
        near.write_bytes(b"ID3")
        (td / "cover.png").unlink()  # force thumb path
        fuzzy = termart.find_cover(near)
        check(
            fuzzy is not None and "Song Title" in fuzzy.name,
            f"find_cover .thumb fuzzy, got {fuzzy}",
        )
        if termart.available():
            painted = termart.render(
                long, cols=24, rows=8, color=False
            )
            check(
                painted["ok"] and painted["engine"] == "chafa",
                f"chafa symbols render succeeds when installed ({painted.get('reason')})",
            )
            check(
                all("\x1b" not in ln for ln in painted["lines"]),
                "curses-safe mono output has no ANSI escapes",
            )
            check(len(painted["lines"]) >= 2, "chafa produced multiple rows")
        else:
            check(True, "chafa not installed — skip live render (ok)")

    # ---- session.now / bind / room (coaching live status)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        audio = root / "Live.mp3"
        audio.write_bytes(
            _id3({"TIT2": "Live Track", "TPE1": "Tester"}) + _mp3(14)
        )
        empty = session.read(root)
        check(empty.get("path") is None, "unbound session has no path")
        bound = session.bind(root, audio, deck="A", source="test")
        check(
            bound.get("title") == "Live Track" and bound.get("deck") == "A",
            "session.bind captures identity",
        )
        check(
            session.resolve_now_track(root) == audio.resolve(),
            "resolve_now_track finds bound file",
        )
        roomed = session.set_room(
            root, theme="melodic", energy="mid", note="floor is warm"
        )
        check(
            roomed["room"].get("theme") == "melodic"
            and roomed["room"].get("energy") == "mid",
            "session.room is session-local",
        )
        # feedback against bound path
        doc = feedback.record(
            audio, fit="retire", note="felt outdated on floor"
        )
        check(
            feedback.latest(doc).get("fit") == "retire",
            "track.feedback fit=retire sticks",
        )
        session.clear(root)
        check(
            session.resolve_now_track(root) is None,
            "session.clear removes binding",
        )

    # ---- embedded APIC extract + library.covers backfill
    png = _gradient_png(32, 32)
    apic_body = (
        b"\x00"  # latin-1
        + b"image/png\x00"
        + b"\x03"  # front cover
        + b"\x00"  # empty description
        + png
    )
    frame = (
        b"APIC"
        + len(apic_body).to_bytes(4, "big")
        + b"\x00\x00"
        + apic_body
    )
    # pad tag size to fit
    tag_body = frame + b"\x00" * 16
    size = len(tag_body)
    # v2.3 uses syncsafe size in header
    ss = bytes(
        [
            (size >> 21) & 0x7F,
            (size >> 14) & 0x7F,
            (size >> 7) & 0x7F,
            size & 0x7F,
        ]
    )
    id3 = b"ID3\x03\x00\x00" + ss + tag_body
    with tempfile.TemporaryDirectory() as tmp:
        td = Path(tmp)
        track = td / "Embedded.mp3"
        track.write_bytes(id3 + _mp3(14))
        extracted = tags.extract_cover(track)
        check(extracted is not None, "extract_cover finds APIC")
        if extracted:
            data, ext = extracted
            check(ext == ".png" and data[:8] == b"\x89PNG\r\n\x1a\n", "APIC is PNG")
        # backfill
        rep = termart.attach_covers([track], extract_embedded=True)
        check(rep["attached_count"] == 1, "attach_covers from embedded")
        check((td / "cover.png").is_file(), "cover.png written beside track")
        # second run skips
        rep2 = termart.attach_covers([track])
        check(rep2["skipped_count"] == 1, "existing cover is skipped")
        # thumb backfill
        track2 = td / "sub" / "Rare Title.mp3"
        track2.parent.mkdir()
        track2.write_bytes(_id3({"TIT2": "Rare"}) + _mp3(14))
        thumbs = td / "thumbs"
        thumbs.mkdir()
        (thumbs / "Artist - Rare Title (video).png").write_bytes(png)
        rep3 = termart.attach_covers(
            [track2],
            thumb_dirs=[thumbs],
            extract_embedded=False,
        )
        check(
            rep3["attached_count"] == 1 and (track2.parent / "cover.png").is_file(),
            "thumb_dirs backfill for Collection tracks",
        )

    # ---- set.plan --------------------------------------------------------
    from migx_cli import setplan

    def _t(name, bpm, camelot, energy_head, dur=300.0, path=None):
        return {
            "name": name,
            "path": path or f"/x/{name}",
            "bpm": bpm,
            "camelot": camelot,
            # 64 buckets; only the head is read for opener selection.
            "energy": [energy_head] * 8 + [0.9] * 56,
            "duration_s": dur,
            "cues": [],
        }

    # The coldest opening leads, even when it is listed last.
    pool = [
        _t("hot.mp3", 128, "8A", 0.9),
        _t("mid.mp3", 126, "8A", 0.5),
        _t("cold.mp3", 127, "8A", 0.1),
    ]
    plan = setplan.plan_set(pool)
    check(plan["schema"] == "migx.set-plan/1", "set-plan schema")
    check(plan["tracks"][0]["name"] == "cold.mp3", "coldest opening leads")
    check(len(plan["tracks"]) == 3, "every mixable track is placed")
    check(plan["tracks"][0]["transition"] is None, "opener has no transition")
    check(
        all(r["transition"] for r in plan["tracks"][1:]),
        "every later track carries its transition",
    )

    # An explicit opener overrides the energy rule.
    forced = setplan.plan_set(pool, opener="hot.mp3")
    check(forced["tracks"][0]["name"] == "hot.mp3", "--opener wins")

    # A track with no bpm/key cannot be sequenced; it must be reported,
    # not silently dropped — a set missing a track with no explanation is
    # the vacuous-success shape (P-34).
    with_unknown = pool + [
        {"name": "raw.mp3", "path": "/x/raw.mp3", "bpm": None, "camelot": None}
    ]
    rep = setplan.plan_set(with_unknown)
    check(len(rep["tracks"]) == 3, "unanalysed track is not sequenced")
    check(rep["unplannable"] == ["raw.mp3"], "unanalysed track is reported")

    # Nothing analysable at all is a reported condition, not a crash.
    empty = setplan.plan_set(
        [{"name": "a.mp3", "path": "/x/a.mp3", "bpm": None, "camelot": None}]
    )
    check(empty["tracks"] == [] and "library.analyze" in empty["note"],
          "no analysable track explains itself")

    # Reachability is scored above raw beatmatchability: a same-key pair
    # inside ±8% must beat one that needs a half-time trick.
    near = _t("near.mp3", 126, "8A", 0.5)
    far = _t("far.mp3", 64, "8A", 0.5)
    from_t = _t("from.mp3", 128, "8A", 0.5)
    check(
        setplan.transition_score(from_t, near)[0]
        > setplan.transition_score(from_t, far)[0],
        "an in-range transition outscores a half-time trick",
    )

    # Duplicate recordings must not both land in a set.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        coll = root / "Collection" / "D"
        coll.mkdir(parents=True)
        same = _mp3(14, frames=60)
        for nm in ("125 4B - Diplo - Don't Be Afraid.mp3",
                   "125 4B - Soulwax - Don't Be Afraid.mp3"):
            (coll / nm).write_bytes(_id3({"TIT2": "Don't Be Afraid"}) + same)
        rows = [
            _t("125 4B - Diplo - Don't Be Afraid.mp3", 125, "4B", 0.4,
               path=str(coll / "125 4B - Diplo - Don't Be Afraid.mp3")),
            _t("125 4B - Soulwax - Don't Be Afraid.mp3", 125, "4B", 0.4,
               path=str(coll / "125 4B - Soulwax - Don't Be Afraid.mp3")),
            _t("other.mp3", 126, "4B", 0.2),
        ]
        deduped = setplan.plan_set(rows, library_root=root)
        names = [r["name"] for r in deduped["tracks"]]
        check(
            len(names) == 2 and "other.mp3" in names,
            f"duplicate recording dropped from the set, got {names}",
        )

    # ---- set.play --------------------------------------------------------
    from migx_cli import setplay

    run = [
        {"name": "a.mp3", "path": "/x/a.mp3", "bpm": 125, "camelot": "7A",
         "duration_s": 300.0, "cues": []},
        {"name": "b.mp3", "path": "/x/b.mp3", "bpm": 123, "camelot": "8A",
         "duration_s": 300.0, "cues": []},
        # 115 needs +8.7% onto 125 — past the fader, so it must be cut.
        {"name": "c.mp3", "path": "/x/c.mp3", "bpm": 115, "camelot": "7A",
         "duration_s": 300.0, "cues": []},
    ]
    segs = setplay.build_segments(run, seconds=60, crossfade=12)
    check(segs[0]["tempo_ratio"] == 1.0, "opener plays native")
    check(segs[1]["beatmatched"], "reachable track is beatmatched")
    check(
        abs(segs[1]["played_bpm"] - 125) < 0.5,
        f"beatmatched onto the running tempo, got {segs[1]['played_bpm']}",
    )
    check(
        not segs[2]["beatmatched"] and segs[2]["tempo_ratio"] == 1.0,
        "a track past ±8% is cut, never force-pitched",
    )
    check(
        segs[2]["crossfade_s"] < segs[1]["crossfade_s"],
        "a cut gets a shorter fade than a blend",
    )

    # Duration must account for atempo: 60s of source at 1.05x is 57.1s out.
    # Pinned to a measured render (6 tracks/60s read 302.79s, not 309s).
    d = setplay.expected_duration(segs)
    by_hand = sum(s["play_s"] / s["tempo_ratio"] for s in segs) - (
        segs[1]["crossfade_s"] + segs[2]["crossfade_s"]
    )
    check(abs(d - by_hand) < 0.05, f"duration accounts for tempo, got {d}")
    # Fades alone would give sum(play_s) - fades; the speed-up must take more.
    fades_only = sum(s["play_s"] for s in segs) - (
        segs[1]["crossfade_s"] + segs[2]["crossfade_s"]
    )
    check(d < fades_only, "speeding a track up shortens the mix beyond fades")

    # A DJ's own mix-in cue wins over the default entry point.
    cued = setplay.entry_point(
        {"duration_s": 400.0,
         "cues": [{"label": "intro is over — start here", "position_s": 62.0}]}
    )
    check(cued == 62.0, f"entry uses the mix-in cue, got {cued}")
    check(
        setplay.entry_point({"duration_s": 400.0, "cues": []}) == 100.0,
        "entry falls back to a quarter in",
    )

    # The filter graph must chain N-1 crossfades and end on [out].
    argv = setplay.build_command(segs, Path("/tmp/x.mp3"))
    graph = argv[argv.index("-filter_complex") + 1]
    check(graph.count("acrossfade") == 2, "N-1 crossfades for N tracks")
    check(graph.rstrip().endswith("[out]"), "graph terminates at [out]")
    check("atempo" in graph, "a pitched track carries atempo")
    check(argv.count("-ss") == 3 and argv.count("-t") == 3,
          "each input is trimmed to its segment")

    # Missing ffmpeg is a reported condition, not a crash or a silent no-op.
    _saved = os.environ.get("MIGX_FFMPEG_BIN")
    os.environ["MIGX_FFMPEG_BIN"] = ""
    try:
        import shutil as _sh
        _real = _sh.which
        _sh.which = lambda *_a, **_k: None
        res = setplay.render(segs, Path("/tmp/never-written.mp3"))
        check(
            not res["ok"] and "ffmpeg" in res["error"],
            "missing ffmpeg is reported, not silently skipped",
        )
    finally:
        _sh.which = _real
        if _saved is None:
            os.environ.pop("MIGX_FFMPEG_BIN", None)
        else:
            os.environ["MIGX_FFMPEG_BIN"] = _saved

    # ---- track.feedback → set.plan (the learning loop) -------------------
    with tempfile.TemporaryDirectory() as td:
        shelf = Path(td) / "Collection" / "A"
        shelf.mkdir(parents=True)
        audio = shelf / "a.mp3"
        audio.write_bytes(_mp3(14, frames=40))

        feedback.record(audio, fit="worked", note="worked at 1am")
        feedback.record(audio, segment="shorter")
        doc = sidecar.read(audio)
        check(len(doc["feedback"]) == 2, "feedback appends, never overwrites")
        check(all("at" in e for e in doc["feedback"]), "every entry timestamped")

        cur = feedback.latest(doc)
        check(
            cur["fit"] == "worked" and cur["segment"] == "shorter",
            f"latest folds fields across entries, got {cur}",
        )
        # Revising one field must not clear the others.
        feedback.record(audio, fit="retire")
        cur2 = feedback.latest(sidecar.read(audio))
        check(
            cur2["fit"] == "retire" and cur2["segment"] == "shorter",
            "revising a fit keeps the segment note",
        )
        check(feedback.is_retired(sidecar.read(audio)), "retire is in force")

        # A bad verdict is refused, not silently stored.
        for bad in (("nonsense", None, None), (None, "sideways", None),
                    (None, None, 9)):
            try:
                feedback.record(audio, fit=bad[0], segment=bad[1],
                                transition=bad[2])
                check(False, f"invalid feedback accepted: {bad}")
            except ValueError:
                check(True, f"invalid feedback refused: {bad}")
        try:
            feedback.record(audio)
            check(False, "empty feedback accepted")
        except ValueError:
            check(True, "empty feedback refused")

    # retire actually removes the track from the next set, and says so.
    base = {"bpm": 125, "camelot": "8A", "duration_s": 300.0,
            "energy": [0.5] * 64, "cues": []}
    keep_t = {**base, "name": "keep.mp3", "path": "/x/keep.mp3"}
    gone_t = {**base, "name": "gone.mp3", "path": "/x/gone.mp3",
              "feedback": [{"at": "now", "fit": "retire"}]}
    planned = setplan.plan_set([keep_t, gone_t])
    names = [r["name"] for r in planned["tracks"]]
    check(names == ["keep.mp3"], f"retired track excluded, got {names}")
    check(planned["retired"] == ["gone.mp3"], "retired tracks are reported")

    # A DJ's `opener` outranks the opening-energy guess, and `peak` is pushed
    # off the opening slot even when it starts quietly.
    quiet_peak = {**base, "name": "peak.mp3", "path": "/x/peak.mp3",
                  "energy": [0.05] * 64,
                  "feedback": [{"at": "now", "placement": "peak"}]}
    loud_opener = {**base, "name": "open.mp3", "path": "/x/open.mp3",
                   "energy": [0.95] * 64,
                   "feedback": [{"at": "now", "placement": "opener"}]}
    led = setplan.plan_set([quiet_peak, loud_opener])
    check(
        led["tracks"][0]["name"] == "open.mp3",
        f"DJ placement outranks energy for the opener, got {led['tracks'][0]['name']}",
    )

    # segment notes change how much of a track set.play uses.
    check(feedback.seconds_for({"feedback": [{"at": "n", "segment": "shorter"}]}, 100) == 60.0,
          "shorter segment shortens play time")
    check(feedback.seconds_for({"feedback": [{"at": "n", "segment": "longer"}]}, 100) == 150.0,
          "longer segment extends play time")
    check(feedback.seconds_for({}, 100) == 100, "no note leaves play time alone")

    # Regression: the loop must survive the REAL loader, not just injected
    # dicts. tui._collection() originally dropped the `feedback` key, so
    # verdicts were written to the sidecar and silently never read — every
    # check above passed while retire did nothing on the live library.
    with tempfile.TemporaryDirectory() as td:
        shelf = Path(td) / "Collection" / "R"
        shelf.mkdir(parents=True)
        real = shelf / "r.mp3"
        real.write_bytes(_mp3(14, frames=40))
        feedback.record(real, fit="retire")
        loaded = tui._collection(Path(td))
        row = next((r for r in loaded if r["name"] == "r.mp3"), None)
        check(row is not None, "loader sees the track")
        check(
            row is not None and feedback.is_retired(row),
            "the real loader carries feedback through to set.plan",
        )

    for f in failures:
        print(f"FAIL: {f}", file=sys.stderr)
    print(
        f"{'FAILED' if failures else 'ok'} — migx-cli naming + mirror"
        f" + quality + tags + resolver + layout + ingest + safety "
        f"({len(failures)} failure(s))"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
