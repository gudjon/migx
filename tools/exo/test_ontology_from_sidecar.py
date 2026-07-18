#!/usr/bin/env python3
"""Regression tests for ontology_from_sidecar.py.

Run: python3 tools/exo/test_ontology_from_sidecar.py   (exit 0 = pass)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ontology_from_sidecar import (  # noqa: E402
    sidecar_cues_to_session_prep,
    sidecar_energy_curve,
    sidecar_to_ontology,
    to_camelot,
)


def check(condition: bool, message: str) -> int:
    print(f"[{'ok' if condition else 'FAIL'}] {message}")
    return 0 if condition else 1


def main() -> int:
    failed = 0

    cases = [
        ("8A", "8A", "Camelot passes through"),
        ("8a", "8A", "Camelot normalizes case"),
        ("1m", "8A", "OpenKey minor maps to Camelot A ring"),
        ("2d", "9B", "OpenKey major maps to Camelot B ring"),
        ("A minor", "8A", "traditional minor maps to Camelot"),
        ("E minor", "9A", "traditional adjacent minor maps to Camelot"),
        ("G# major", "4B", "enharmonic major maps to Camelot"),
        ("not-a-key", None, "unknown key is left unresolved"),
    ]
    for text, expected, message in cases:
        failed += check(to_camelot(text) == expected, message)

    ont = sidecar_to_ontology({"bpm": 126, "key": "E minor"}, "song-real")
    failed += check(ont["id"] == "song-real", "ontology preserves song id")
    failed += check(ont["source"] == "local", "sidecar ontology is local source")
    failed += check(ont["playback"]["multi_deck_allowed"] is True, "local playback allows multi-deck")
    failed += check(ont["key"]["camelot"] == "9A", "sidecar key is converted to Camelot")
    failed += check(ont["bpm"] == 126.0, "sidecar bpm becomes numeric bpm")
    failed += check("energy_curve" not in ont, "energy curve is not invented")
    failed += check("sections" not in ont, "sections are not invented")

    enriched_sidecar = {
        "bpm": 128,
        "key": "9A",
        "energy_curve": {
            "unit": "track_fraction",
            "method": "waveform-filtered-downsample-v1",
            "samples": [0.1, 0.55, 1.2, -0.2, "skip"],
            "bands": {"low": [0.2], "mid": [0.3], "high": [0.4], "all": [0.5]},
        },
        "cues": [
            {
                "type": "hotcue",
                "hotcue": 0,
                "label": "mix in",
                "position_beats": 16.5,
                "position_ms": 15384.6,
            },
            {"type": "loop", "hotcue": 2, "position_ms": 45000},
            {"type": "hotcue", "hotcue": 4},
        ],
    }
    energy = sidecar_energy_curve(enriched_sidecar)
    failed += check(energy is not None, "real sidecar energy is accepted")
    failed += check(
        energy["samples"] == [0.1, 0.55, 1.0, 0.0],
        "energy samples are bounded and non-numeric values are skipped",
    )
    enriched = sidecar_to_ontology(enriched_sidecar, "song-enriched")
    failed += check(
        enriched["energy_curve"]["method"] == "waveform-filtered-downsample-v1",
        "sidecar energy method is preserved",
    )
    prep = sidecar_cues_to_session_prep(enriched_sidecar)
    failed += check(prep is not None, "real sidecar cues become session prep")
    cue_points = prep["cue_points"] if prep else []
    failed += check(len(cue_points) == 2, "cues without position are skipped")
    failed += check(cue_points[0]["id"] == "cue-hotcue-1", "hotcue id is 1-based for prep")
    failed += check(cue_points[0]["label"] == "mix in", "cue label is preserved")
    failed += check(cue_points[0]["beat"] == 16.5, "cue beat is mapped")
    failed += check(cue_points[0]["ms"] == 15384.6, "cue millis is mapped")
    failed += check(cue_points[1]["label"] == "Hotcue 3", "missing cue label has useful default")

    unresolved = sidecar_to_ontology({"bpm": 0, "key": ""}, "song-gap")
    failed += check("camelot" not in unresolved["key"], "empty key stays unresolved")
    failed += check("bpm" not in unresolved, "zero bpm is omitted")

    print("PASS" if not failed else f"FAILED ({failed})")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
