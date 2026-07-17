#!/usr/bin/env python3
"""Structural checks for EXO song/session fixtures (no network)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXO = (
    REPO
    / "kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures"
)
PASTE = EXO / "import/sample-paste.txt"
IMPORTED = EXO / "songs/imported"


def main() -> int:
    errors: list[str] = []

    # paste-import --check when sample exists
    if PASTE.is_file() and IMPORTED.is_dir():
        r = subprocess.run(
            [
                sys.executable,
                str(REPO / "tools/exo/spotify_uri_import.py"),
                "--paste",
                str(PASTE),
                "--out-dir",
                str(IMPORTED),
                "--check",
            ],
            cwd=REPO,
        )
        if r.returncode != 0:
            errors.append("spotify_uri_import --check failed")

    songs = list((EXO / "songs").rglob("*.json"))
    sessions = list((EXO / "sessions").glob("*.json"))
    for p in songs + sessions:
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{p}: {e}")

    for p in sessions:
        data = json.loads(p.read_text(encoding="utf-8"))
        order = data.get("order") or []
        ids = {t["song_id"] for t in data.get("tracks") or []}
        for o in order:
            if o not in ids:
                errors.append(f"{p.name}: order id {o} missing from tracks")
        for t in data.get("tracks") or []:
            ref = (p.parent / t["ontology_ref"]).resolve()
            if not ref.is_file():
                errors.append(f"{p.name}: missing ontology_ref {t['ontology_ref']}")
        if data.get("kind") == "hybrid_prep":
            pol = data.get("policy") or {}
            if pol.get("spotify_multi_deck") is not False:
                errors.append(f"{p.name}: hybrid_prep requires spotify_multi_deck=false")

    for p in songs:
        data = json.loads(p.read_text(encoding="utf-8"))
        if data.get("source") == "spotify":
            ext = data.get("external_ids") or {}
            if "spotify_uri" not in ext:
                errors.append(f"{p.name}: spotify without spotify_uri")
            if data.get("playback", {}).get("multi_deck_allowed") is True:
                errors.append(f"{p.name}: multi_deck_allowed must be false for spotify")

    if errors:
        print("FAIL:")
        for e in errors:
            print(" ", e)
        return 1
    print(f"ALL EXO FIXTURES OK ({len(songs)} songs, {len(sessions)} sessions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
