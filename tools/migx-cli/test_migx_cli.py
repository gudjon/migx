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
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from migx_cli import (  # noqa: E402
    api,
    auth,
    ingest,
    keys,
    layout,
    mirror,
    naming,
    quality,
    ratelimit,
    resolve,
    sidecar,
    tags,
    tui,
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
