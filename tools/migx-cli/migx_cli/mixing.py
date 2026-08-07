"""Transition planning: can these two tracks be mixed, and how?

Reuses the co-pilot's scoring rather than writing a third copy —
`tools/exo/copilot_why_next.py` already owns `tempo_compat` (beatmatch across
direct/double/half time) and `camelot_neighbors` (the harmonic wheel). A
second implementation would drift from the co-pilot's answers, which is
exactly the failure `P-11` names.

What is new here is **technique suitability**. A DJ does not ask "are these
compatible" so much as "which move do I make". Each technique has different
requirements, and the data already in the sidecar answers most of them:

    Long Blend        harmonic + tight BPM + room to breathe at the edges
    Bass Swap         tight BPM; key matters less, the bass is swapped out
    Drop Mix          a known drop on both sides; timing is everything
    Echo Out          rescues an exit when there is no clean outro
    Crossfade Cut     works on anything; energy carries it, not beatmatch

This plans transitions. It does not perform them: there is no deck, no
engine, and no audio here.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_EXO = Path(__file__).resolve().parents[3] / "tools" / "exo"
if str(_EXO) not in sys.path:
    sys.path.insert(0, str(_EXO))

try:  # pragma: no cover - import shape depends on repo layout
    from copilot_why_next import camelot_neighbors, tempo_compat
except ImportError:  # pragma: no cover
    camelot_neighbors = None
    tempo_compat = None


def tempo(from_bpm: float | None, to_bpm: float | None) -> dict[str, Any]:
    """Beatmatch verdict, delegated to the co-pilot's scorer."""
    if not from_bpm or not to_bpm or tempo_compat is None:
        return {"score": None, "note": "tempo: unknown bpm"}
    score, note = tempo_compat(float(from_bpm), float(to_bpm))
    pct = min(
        abs((float(to_bpm) * f) / float(from_bpm) - 1.0) * 100.0
        for f in (1.0, 2.0, 0.5)
    )
    return {"score": score, "note": note, "drift_pct": round(pct, 2)}


def harmonic(from_key: str | None, to_key: str | None) -> dict[str, Any]:
    """Camelot verdict: same, neighbouring, relative, or a clash."""
    if not from_key or not to_key or camelot_neighbors is None:
        return {"compatible": None, "note": "key: unknown"}
    neighbours = camelot_neighbors(from_key)
    if not neighbours:
        return {"compatible": None, "note": f"key: cannot read {from_key!r}"}
    if to_key == from_key:
        return {
            "compatible": True,
            "relation": "same",
            "note": f"key: {from_key} → {to_key}, same key",
        }
    if to_key in neighbours:
        relation = "relative" if to_key[:-1] == from_key[:-1] else "neighbour"
        return {
            "compatible": True,
            "relation": relation,
            "note": f"key: {from_key} → {to_key}, {relation} on the wheel",
        }
    return {
        "compatible": False,
        "relation": "clash",
        "note": f"key: {from_key} → {to_key}, not adjacent — expect a clash",
    }


def _has_cue(track: dict[str, Any], *words: str) -> bool:
    for cue in track.get("cues") or []:
        label = (cue.get("label") or "").lower()
        if any(word in label for word in words):
            return True
    return False


TECHNIQUES = (
    "Long Blend",
    "Bass Swap",
    "Drop Mix",
    "Echo Out",
    "Crossfade Cut",
)


def techniques(
    outgoing: dict[str, Any], incoming: dict[str, Any]
) -> list[dict[str, Any]]:
    """Rank transition techniques for this pair, with the reason for each."""
    beat = tempo(outgoing.get("bpm"), incoming.get("bpm"))
    key = harmonic(outgoing.get("camelot"), incoming.get("camelot"))
    drift = beat.get("drift_pct")
    tight = drift is not None and drift <= 3.0
    mixable = drift is not None and drift <= 6.0

    out = []

    # Long blend: the most exposed move — a clash or a tempo drift is audible
    # for the whole overlap, so it demands the most and forgives the least.
    score = 0
    why = []
    if key.get("compatible"):
        score += 50
        why.append(key["note"])
    elif key.get("compatible") is False:
        why.append("keys clash — a long overlap will expose it")
    if tight:
        score += 40
        why.append(f"tempo within {drift:.1f}%")
    elif mixable:
        score += 15
        why.append(f"tempo {drift:.1f}% — needs a pitch nudge")
    if _has_cue(outgoing, "outro", "mix out", "exit"):
        score += 10
        why.append("outgoing has an exit cue")
    out.append({"name": "Long Blend", "score": score, "why": why})

    # Bass swap: bass is swapped rather than layered, so a key clash matters
    # much less than the beatgrid lining up.
    score = 60 if tight else (25 if mixable else 0)
    why = [f"tempo {drift:.1f}%" if drift is not None else "tempo unknown"]
    if key.get("compatible") is False:
        why.append("key clash tolerable — bass is swapped, not layered")
    out.append({"name": "Bass Swap", "score": score, "why": why})

    # Drop mix: needs to know where the drops are. Without cues it is a guess.
    has_drops = _has_cue(incoming, "drop") and _has_cue(
        outgoing, "drop", "break", "mix out"
    )
    score = (70 if has_drops else 10) + (20 if tight else 0)
    why = (
        ["drop cues marked on both"]
        if has_drops
        else ["no drop cue — mark one with `track.cue` first"]
    )
    out.append({"name": "Drop Mix", "score": score, "why": why})

    # Echo out: the rescue. Best exactly when the others are weak.
    score = 40
    why = ["works without a clean outro"]
    if key.get("compatible") is False:
        score += 20
        why.append("covers the key clash")
    if not mixable:
        score += 20
        why.append("covers the tempo gap")
    out.append({"name": "Echo Out", "score": score, "why": why})

    # Crossfade cut: always available; the question is whether it fits.
    score = 30
    why = ["always available — energy carries it, not beatmatch"]
    energy_out = (outgoing.get("energy") or [])[-8:]
    energy_in = (incoming.get("energy") or [])[:8]
    if energy_out and energy_in:
        if sum(energy_in) / len(energy_in) >= sum(energy_out) / len(
            energy_out
        ):
            score += 25
            why.append("incoming opens hotter than the outgoing ends")
    out.append({"name": "Crossfade Cut", "score": score, "why": why})

    out.sort(key=lambda t: -t["score"])
    return out


def plan(outgoing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "migx.transition-plan/1",
        "from": outgoing.get("name"),
        "to": incoming.get("name"),
        "tempo": tempo(outgoing.get("bpm"), incoming.get("bpm")),
        "harmonic": harmonic(outgoing.get("camelot"), incoming.get("camelot")),
        "techniques": techniques(outgoing, incoming),
    }
