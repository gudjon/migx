#!/usr/bin/env python3
"""Bridge: real Migx FSL track sidecars -> co-pilot song ontologies + a session.

Turns the per-track `<track>.migx/track.json` sidecars that TrackDAO::saveTrack()
writes (bpm / key / replaygain / peak, with optional cues / energy) into the
`migx.song-ontology` JSON that
copilot_why_next.py reasons over -- so the co-pilot runs on a REAL library's
key/bpm, not fixtures. This is the smallest end-to-end learning vehicle
(DC-PDCL-5.3): prove harmonic + tempo reasoning works on real track metadata,
and expose exactly what data is still missing.

Honest gaps (DC-PDCL-4.6 / 1.11): this bridge never invents energy, cue points,
sections, or phrases. If the FSL sidecar has a TrackDAO waveform energy curve,
it maps it through. If cues exist, it maps them into session-local prep cue
points. If they are absent, the co-pilot keeps its neutral energy fallback and
empty prep.

Usage:
  python3 tools/exo/ontology_from_sidecar.py \\
      --sidecars a.json b.json c.json --out-dir /tmp/exo-real
  python3 tools/exo/copilot_why_next.py --session /tmp/exo-real/session.json
"""
from __future__ import annotations

import argparse
import json
import math
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


def _bounded_number(value: Any, lower: float = 0.0, upper: float = 1.0) -> float | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return max(lower, min(upper, number))


def sidecar_energy_curve(sidecar: dict[str, Any]) -> dict[str, Any] | None:
    """Return schema-compatible energy data when the sidecar has real samples."""
    raw = sidecar.get("energy_curve")
    if not isinstance(raw, dict):
        return None
    raw_samples = raw.get("samples")
    if not isinstance(raw_samples, list):
        return None
    samples = [_bounded_number(value) for value in raw_samples]
    samples = [value for value in samples if value is not None]
    if not samples:
        return None

    energy_curve: dict[str, Any] = {
        "unit": str(raw.get("unit") or "track_fraction"),
        "method": str(raw.get("method") or "sidecar"),
        "samples": samples,
    }
    bands = raw.get("bands")
    if isinstance(bands, dict):
        clean_bands: dict[str, list[float]] = {}
        for band in ("low", "mid", "high", "all"):
            raw_values = bands.get(band, [])
            if not isinstance(raw_values, list):
                continue
            values = [_bounded_number(value) for value in raw_values]
            clean = [value for value in values if value is not None]
            if clean:
                clean_bands[band] = clean
        if clean_bands:
            energy_curve["bands"] = clean_bands
    return energy_curve


def sidecar_cues_to_session_prep(sidecar: dict[str, Any]) -> dict[str, Any] | None:
    """Map FSL cue facts into session-local prep cues.

    The sidecar remains the richer source of truth. Session prep keeps only the
    fields the EXO session schema already supports: id, label, beat, and ms.
    """
    raw_cues = sidecar.get("cues")
    if not isinstance(raw_cues, list):
        return None

    cue_points: list[dict[str, Any]] = []
    for index, cue in enumerate(raw_cues):
        if not isinstance(cue, dict):
            continue
        beat = cue.get("position_beats")
        ms = cue.get("position_ms")
        beat_value = (
            float(beat)
            if isinstance(beat, (int, float)) and not isinstance(beat, bool)
            else None
        )
        ms_value = (
            float(ms)
            if isinstance(ms, (int, float)) and not isinstance(ms, bool)
            else None
        )
        if beat_value is None and ms_value is None:
            continue

        cue_type = str(cue.get("type") or "cue")
        hotcue = cue.get("hotcue")
        if isinstance(hotcue, int) and not isinstance(hotcue, bool) and hotcue >= 0:
            cue_id = f"cue-hotcue-{hotcue + 1}"
            default_label = f"Hotcue {hotcue + 1}"
        else:
            cue_id = re.sub(
                r"[^a-z0-9]+",
                "-",
                f"cue-{cue_type}-{index + 1}".lower(),
            ).strip("-")
            default_label = cue_type.replace("-", " ").title()

        point: dict[str, Any] = {
            "id": cue_id,
            "label": str(cue.get("label") or default_label),
        }
        if beat_value is not None and math.isfinite(beat_value):
            point["beat"] = beat_value
        if ms_value is not None and math.isfinite(ms_value):
            point["ms"] = ms_value
        cue_points.append(point)

    if not cue_points:
        return None
    return {"cue_points": cue_points}


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
    energy_curve = sidecar_energy_curve(sidecar)
    if energy_curve:
        ont["energy_curve"] = energy_curve
    # NOTE: no invented sections/phrases. Cues are session-local prep data.
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
        track_entry = {
            "song_id": song_id,
            "ontology_ref": f"{song_id}.ontology.json",
            "source": "local",
        }
        prep = sidecar_cues_to_session_prep(sidecar)
        if prep:
            track_entry["prep"] = prep
        tracks.append(track_entry)
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
