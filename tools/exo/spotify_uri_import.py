#!/usr/bin/env python3
"""Paste-import Spotify track URIs into EXO song ontology stubs (no network, no playback).

Step 1.5 of the Octave-style Spotify path:
  - Identity only (spotify:track:… / open.spotify.com/track/…)
  - Writes migx.song-ontology/1 JSON with source=spotify, multi_deck_allowed=false
  - Optional: append tracks into a hybrid prep session JSON

Does NOT call Spotify APIs, decode audio, or enable dual-deck Spotify.

Input line formats (one track per line; blank/# ignored):
  spotify:track:<id>
  https://open.spotify.com/track/<id>
  https://open.spotify.com/track/<id>?si=…
  <uri_or_url> | <title> | <artist> | <bpm> | <camelot>

Examples:
  python3 tools/exo/spotify_uri_import.py \\
    --paste kanban/.../fixtures/import/sample-paste.txt \\
    --out-dir kanban/.../fixtures/songs

  python3 tools/exo/spotify_uri_import.py --stdin --out-dir /tmp/exo-songs \\
    --session-out /tmp/session-hybrid.json --session-id session-paste-demo
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]

URI_RE = re.compile(
    r"(?:spotify:track:|https?://open\.spotify\.com/track/)([A-Za-z0-9]+)",
    re.IGNORECASE,
)
CAMELOT_RE = re.compile(r"^([0-9]{1,2})([ABab])$")


def parse_line(line: str) -> dict[str, Any] | None:
    raw = line.strip()
    if not raw or raw.startswith("#"):
        return None
    parts = [p.strip() for p in raw.split("|")]
    head = parts[0]
    m = URI_RE.search(head)
    if not m:
        raise ValueError(f"no Spotify track id in line: {raw!r}")
    sid = m.group(1)
    title = parts[1] if len(parts) > 1 and parts[1] else None
    artist = parts[2] if len(parts) > 2 and parts[2] else None
    bpm = float(parts[3]) if len(parts) > 3 and parts[3] else 124.0
    camelot = parts[4].upper() if len(parts) > 4 and parts[4] else "8A"
    if not CAMELOT_RE.match(camelot):
        raise ValueError(f"invalid camelot {camelot!r} on line: {raw!r}")
    return {
        "spotify_id": sid,
        "spotify_uri": f"spotify:track:{sid}",
        "title": title,
        "artist": artist,
        "bpm": bpm,
        "camelot": camelot,
    }


def song_id_for(spotify_id: str) -> str:
    # stable, filesystem-safe; short prefix for readability
    return f"song-sp-{spotify_id[:12].lower()}"


def stub_ontology(meta: dict[str, Any]) -> dict[str, Any]:
    """Hand-authorable stub: identity is real; structure/energy are placeholders."""
    sid = meta["spotify_id"]
    song_id = song_id_for(sid)
    guidance = "paste-import stub — no local file; prep/sequence only; multi_deck forbidden"
    if meta.get("title") or meta.get("artist"):
        label = " — ".join(x for x in (meta.get("artist"), meta.get("title")) if x)
        guidance = f"{label}; {guidance}"

    # default section grid: 8-bar phrases at given bpm; unknown real duration
    duration_beats = 512
    return {
        "schema": "migx.song-ontology/1",
        "id": song_id,
        "ref": "",
        "source": "spotify",
        "external_ids": {
            "spotify_uri": meta["spotify_uri"],
            "spotify_id": sid,
        },
        "playback": {
            "mode": "prep_only",
            "multi_deck_allowed": False,
        },
        "duration_beats": duration_beats,
        "bpm": meta["bpm"],
        "key": {
            "chromatic": "?",
            "camelot": meta["camelot"],
            "open_key": "",
        },
        "phrases": {"beats_per_bar": 4, "bars_per_phrase": 8},
        "sections": [
            {
                "id": "sec-intro",
                "type": "intro",
                "start_beat": 0,
                "end_beat": 64,
                "energy": 0.35,
                "mixable": True,
                "_llm_guidance": guidance,
            },
            {
                "id": "sec-build",
                "type": "build",
                "start_beat": 64,
                "end_beat": 128,
                "energy": 0.5,
            },
            {
                "id": "sec-drop",
                "type": "drop",
                "start_beat": 128,
                "end_beat": 320,
                "energy": 0.75,
                "_llm_guidance": "stub energy — replace when analyzed or user-edited",
            },
            {
                "id": "sec-outro",
                "type": "outro",
                "start_beat": 400,
                "end_beat": duration_beats,
                "energy": 0.3,
                "mixable": True,
            },
        ],
        "energy_curve": {
            "unit": "phrase",
            "method": "paste-import-stub",
            "samples": [0.3, 0.4, 0.5, 0.65, 0.75, 0.7, 0.5, 0.35, 0.28],
        },
        "_import": {
            "tool": "tools/exo/spotify_uri_import.py",
            "title": meta.get("title"),
            "artist": meta.get("artist"),
            "note": "metadata optional; Spotify URI is SSoT identity for this row",
        },
    }


def session_track_entry(
    meta: dict[str, Any], ontology_rel: str, role: str = "other"
) -> dict[str, Any]:
    song_id = song_id_for(meta["spotify_id"])
    note_bits = ["Spotify paste-import — prep/sequence only"]
    if meta.get("title"):
        note_bits.append(meta["title"])
    return {
        "song_id": song_id,
        "ontology_ref": ontology_rel,
        "source": "spotify",
        "prep": {
            "role": role,
            "notes": "; ".join(note_bits),
            "cue_points": [
                {"id": "cue-mix-in", "label": "mix-in", "beat": 0},
            ],
        },
    }


def sequence_edges(order: list[str]) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for a, b in zip(order, order[1:]):
        edges.append(
            {
                "from": a,
                "to": b,
                "relation": "sequence-only",
                "notes": "paste-import order; dual Spotify multi-deck forbidden",
            }
        )
    return edges


def load_lines(args: argparse.Namespace) -> list[str]:
    if args.stdin:
        return sys.stdin.read().splitlines()
    if args.paste:
        return Path(args.paste).read_text(encoding="utf-8").splitlines()
    raise SystemExit("provide --paste PATH or --stdin")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--paste", type=Path, help="text file of URIs (one per line)")
    ap.add_argument("--stdin", action="store_true", help="read paste from stdin")
    ap.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="directory for song-*.ontology.json files",
    )
    ap.add_argument(
        "--session-out",
        type=Path,
        help="optional path to write hybrid prep session JSON",
    )
    ap.add_argument("--session-id", default="session-paste-import")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="print paths and JSON summaries without writing",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="validate that out-dir songs for this paste already exist and match URI",
    )
    args = ap.parse_args()

    lines = load_lines(args)
    metas: list[dict[str, Any]] = []
    for i, line in enumerate(lines, 1):
        try:
            m = parse_line(line)
        except ValueError as e:
            print(f"line {i}: {e}", file=sys.stderr)
            return 2
        if m:
            metas.append(m)

    if not metas:
        print("no tracks parsed", file=sys.stderr)
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    order: list[str] = []
    session_tracks: list[dict[str, Any]] = []

    for meta in metas:
        song_id = song_id_for(meta["spotify_id"])
        order.append(song_id)
        path = args.out_dir / f"{song_id}.ontology.json"
        ont = stub_ontology(meta)

        if args.check:
            if not path.is_file():
                print(f"MISSING {path}", file=sys.stderr)
                return 1
            existing = json.loads(path.read_text(encoding="utf-8"))
            got = (existing.get("external_ids") or {}).get("spotify_uri")
            if got != meta["spotify_uri"]:
                print(f"URI mismatch {path}: {got} != {meta['spotify_uri']}", file=sys.stderr)
                return 1
            if existing.get("playback", {}).get("multi_deck_allowed") is not False:
                print(f"multi_deck must be false: {path}", file=sys.stderr)
                return 1
            print(f"OK {path.name}")
            continue

        text = json.dumps(ont, indent=2) + "\n"
        if args.dry_run:
            print(f"WOULD WRITE {path}")
            print(f"  uri={meta['spotify_uri']} bpm={meta['bpm']} camelot={meta['camelot']}")
        else:
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path}")
        written.append(path)
        # ontology_ref filled when writing session (relative to session dir)
        session_tracks.append(session_track_entry(meta, path.name, role="wildcard"))

    if args.check:
        print(f"CHECK PASS ({len(metas)} tracks)")
        return 0

    if args.session_out:
        sess_parent = args.session_out.parent.resolve()
        for i, meta in enumerate(metas):
            song_path = (
                args.out_dir / f"{song_id_for(meta['spotify_id'])}.ontology.json"
            ).resolve()
            rel = Path(os.path.relpath(song_path, sess_parent))
            session_tracks[i]["ontology_ref"] = str(rel).replace("\\", "/")

        session = {
            "schema": "migx.session-ontology/1",
            "id": args.session_id,
            "kind": "hybrid_prep",
            "policy": {
                "spotify_multi_deck": False,
                "spotify_playback": "none",
            },
            "tracks": session_tracks,
            "order": order,
            "edges": sequence_edges(order),
        }
        if args.dry_run:
            print(f"WOULD WRITE session {args.session_out}")
            print(json.dumps(session, indent=2)[:500], "…")
        else:
            args.session_out.parent.mkdir(parents=True, exist_ok=True)
            args.session_out.write_text(
                json.dumps(session, indent=2) + "\n", encoding="utf-8"
            )
            print(f"wrote {args.session_out}")

    print(
        f"done: {len(metas)} Spotify URI row(s); multi_deck_allowed=false; no network"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
