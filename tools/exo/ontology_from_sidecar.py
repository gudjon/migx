#!/usr/bin/env python3
"""Bridge: real Migx FSL track sidecars -> co-pilot song ontologies + a session.

Turns the per-track `<track>.migx/track.json` sidecars that TrackDAO::saveTrack()
writes (bpm / key / replaygain / peak) into the `migx.song-ontology` JSON that
copilot_why_next.py reasons over -- so the co-pilot runs on a REAL library's
key/bpm, not fixtures. This is the smallest end-to-end learning vehicle
(DC-PDCL-5.3): prove harmonic + tempo reasoning works on real track metadata,
and expose exactly what data is still missing.

Honest gaps (DC-PDCL-4.6 / 1.11): the FSL sidecar has no cue points and no real
energy curve, so this bridge omits `energy_curve` (the co-pilot falls back to a
neutral 0.5) and emits no sections/phrases. Those need the on-device analyzer
(see spike-musicunderstanding-local-to-exo). bpm + key are real.

Usage:
  python3 tools/exo/ontology_from_sidecar.py \\
      --sidecars a.json b.json c.json --out-dir /tmp/exo-real
  python3 tools/exo/copilot_why_next.py --session /tmp/exo-real/session.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

# Chromatic key name -> Camelot code (the wheel). Minor = A ring, major = B ring.
# Enharmonic spellings are aliased. Names are normalized (lowercased, no spaces,
# 'minor'/'min' -> 'm', 'major'/'maj' -> '').
_CAMELOT = {
    # minor (A)
    "abm": "1A", "g#m": "1A", "ebm": "2A", "d#m": "2A", "bbm": "3A", "a#m": "3A",
    "fm": "4A", "cm": "5A", "gm": "6A", "dm": "7A", "am": "8A", "em": "9A",
    "bm": "10A", "f#m": "11A", "gbm": "11A", "c#m": "12A", "dbm": "12A",
    # major (B) -- bare name
    "b": "1B", "f#": "2B", "gb": "2B", "db": "3B", "c#": "3B", "ab": "4B",
    "g#": "4B", "eb": "5B", "d#": "5B", "bb": "6B", "a#": "6B", "f": "7B",
    "c": "8B", "g": "9B", "d": "10B", "a": "11B", "e": "12B",
}
_CAMELOT_RE = re.compile(r"^\s*(\d{1,2})\s*([ABab])\s*$")
_OPENKEY_RE = re.compile(r"^\s*(\d{1,2})\s*([dmDM])\s*$")


def to_camelot(text: str | None) -> str | None:
    """Convert a key string in Camelot, OpenKey, or Traditional notation to a
    Camelot code. Returns None if unrecognized (co-pilot skips harmonic scoring
    rather than guessing)."""
    if not text:
        return None
    s = text.strip()
    m = _CAMELOT_RE.match(s)
    if m:
        return f"{int(m.group(1))}{m.group(2).upper()}"
    m = _OPENKEY_RE.match(s)
    if m:  # OpenKey N (m=minor->A, d=major->B); camelot = ((N+6) % 12) + 1
        n = ((int(m.group(1)) + 6) % 12) + 1
        return f"{n}{'A' if m.group(2).lower() == 'm' else 'B'}"
    # Traditional / chromatic: normalize.
    norm = (
        s.lower()
        .replace(" ", "")
        .replace("minor", "m")
        .replace("min", "m")
        .replace("major", "")
        .replace("maj", "")
    )
    return _CAMELOT.get(norm)


def sidecar_to_ontology(sidecar: dict[str, Any], song_id: str) -> dict[str, Any]:
    camelot = to_camelot(sidecar.get("key"))
    key_obj: dict[str, Any] = {"chromatic": sidecar.get("key")}
    if camelot:
        key_obj["camelot"] = camelot
    ont: dict[str, Any] = {
        "schema": "migx.song-ontology/1",
        "id": song_id,
        "source": "local",
        "playback": {"mode": "engine_multi_deck", "multi_deck_allowed": True},
        "key": key_obj,
    }
    bpm = sidecar.get("bpm")
    if bpm:
        ont["bpm"] = float(bpm)
    # NOTE: no energy_curve / sections / cues — the FSL sidecar has none yet.
    # The co-pilot defaults energy to neutral; analyzer work fills this later.
    return ont


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sidecars", nargs="+", required=True,
                    help="FSL track.json sidecar paths, in intended play order")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tracks, order, unresolved = [], [], []
    for i, sc_path in enumerate(args.sidecars):
        p = Path(sc_path)
        sidecar = json.loads(p.read_text(encoding="utf-8"))
        # id from the parent dir (<track>.migx) or the file stem.
        stem = p.parent.stem if p.parent.suffix == ".migx" else p.stem
        song_id = re.sub(r"[^a-z0-9]+", "-", f"song-{i + 1:02d}-{stem}".lower()).strip("-")
        ont = sidecar_to_ontology(sidecar, song_id)
        (out / f"{song_id}.ontology.json").write_text(
            json.dumps(ont, indent=2) + "\n", encoding="utf-8")
        tracks.append({"song_id": song_id, "ontology_ref": f"{song_id}.ontology.json"})
        order.append(song_id)
        if "camelot" not in ont["key"]:
            unresolved.append((song_id, sidecar.get("key")))

    session = {
        "schema": "migx.session/1",
        "id": "session-from-sidecars",
        "order": order,
        "tracks": tracks,
        "edges": [],  # no declared edges: force the co-pilot to reason from key/bpm
    }
    (out / "session.json").write_text(json.dumps(session, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(tracks)} ontologies + session.json to {out}")
    if unresolved:
        print("WARN unresolved keys (harmonic scoring skipped):")
        for sid, k in unresolved:
            print(f"  {sid}: key={k!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
