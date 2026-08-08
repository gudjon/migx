"""Tracks whose analysis looks wrong, queued for a human to judge.

Analysis is good, not infallible. BPM detection **doubles** on sparse or
half-time material — `Lola Young - Like Him` came back at 195 BPM sitting
between a 100 and a 95 in a planned set. The set still sounded plausible
because the planner bridged it as double-time, which is the dangerous part: a
wrong number that produces a *reasonable-looking* result is far worse than one
that produces an obvious mess, because nothing draws your eye to it.

So this does not try to fix anything. It builds a **review queue**: the DJ has
ears, the analyser has arithmetic, and only the DJ can settle which is right.
Human-in-the-loop, on the human's schedule.

Every check answers "is this value implausible *for a DJ track*", never "is
this file unusual". A 195 BPM drum-and-bass record is real; a 195 BPM record
surrounded by 95s is a doubling.
"""

from __future__ import annotations

from typing import Any

# Outside this, a DJ track is almost certainly mis-detected rather than exotic.
BPM_FLOOR, BPM_CEILING = 60.0, 190.0

# Folding must bring the tempo at least this much closer to the norm before we
# call it a mis-detection. Well under 1.0 so a marginal improvement is not
# enough — a genuine 140 in a 121 library must not be "corrected" to 70.
FOLD_MARGIN = 0.4

# A track needs this many analysed neighbours before "unlike its neighbours"
# means anything.
MIN_CONTEXT = 8


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    if not ordered:
        return 0.0
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def inspect(tracks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flag tracks a human should re-check. Returns one row per suspicion."""
    analysed = [t for t in tracks if t.get("bpm")]
    tempos = [float(t["bpm"]) for t in analysed]
    norm = _median(tempos)
    have_context = len(tempos) >= MIN_CONTEXT

    out: list[dict[str, Any]] = []
    for track in tracks:
        bpm = track.get("bpm")
        reasons: list[str] = []

        if not bpm:
            # Not suspicious — just not done. library.analyze already reports
            # these, and duplicating them here would bury the real findings.
            continue

        bpm = float(bpm)
        if bpm < BPM_FLOOR or bpm > BPM_CEILING:
            reasons.append(
                f"{bpm:.0f} BPM is outside {BPM_FLOOR:.0f}-{BPM_CEILING:.0f}"
            )
        elif have_context and norm > 0:
            # The doubling case: plausible alone, wrong in company.
            #
            # Compare against FOLDING THE TRACK, not against 2x the norm. A
            # doubled 97.5 reads as 195, which is 1.6x a 121 norm — nowhere
            # near 2x it, so a "is it 2x the median" test never fires. The
            # question is whether halving (or doubling) moves this track
            # markedly closer to the rest of the library.
            here = abs(bpm - norm)
            for factor, label in ((0.5, "double-time"), (2.0, "half-time")):
                folded = bpm * factor
                if not (BPM_FLOOR <= folded <= BPM_CEILING):
                    continue
                if abs(folded - norm) < here * FOLD_MARGIN:
                    reasons.append(
                        f"{bpm:.0f} sits far from the library norm "
                        f"({norm:.0f}) but {folded:.0f} does not — likely "
                        f"detected {label}; true tempo may be {folded:.0f}"
                    )
                    break

        if not track.get("camelot"):
            reasons.append("no key detected — cannot be harmonically mixed")

        duration = track.get("duration_s") or 0
        if 0 < duration < 60:
            reasons.append(f"only {duration:.0f}s long — a clip or a bad file?")

        if reasons:
            out.append(
                {
                    "name": track.get("name"),
                    "path": track.get("path"),
                    "bpm": bpm,
                    "camelot": track.get("camelot"),
                    "reasons": reasons,
                }
            )
    out.sort(key=lambda r: r["name"] or "")
    return out
