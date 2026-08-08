"""What the DJ said about a track, and how it changes the next set.

The loop this closes: a set is playing, the DJ reacts out loud — *"that one
feels dated, don't play it again"*, *"the blend was too long"*, *"this is a
peak-time record, stop opening with it"* — and the coding agent they are
already talking to records the verdict here. The next `set.plan` is different
because of it. Trigger → Capture → Intelligence → Adjustment (`P-01`).

## The split that keeps this honest

**The agent interprets. This module persists and applies.** The CLI takes
*structured verdicts*, never free speech, so there is no natural-language
guessing anywhere near the library. Turning "yeah that felt tired, bin it" into
`--fit retire` is the agent's job, where it is cheap, reviewable, and needs
no runtime.

The consequence is that every stored verdict is a small closed vocabulary a
lint could check, and a human reading `track.json` a year from now can still
tell exactly what was meant.

## Where it lives

In the track's own sidecar, beside the audio (`filesystem-driven-architecture`).
Feedback about a *recording* travels with that recording — copy the file to
another machine and its history comes along. Nothing here needs a database.

Verdicts are **append-only with a timestamp**. A DJ who retires a track in
December and revives it in June has a history, not a silently overwritten
field, and `set.plan` reads only the latest — so reviving is just saying so
again.

## What each verdict does to the next set

| flag / value          | effect on `set.plan` / Arrange |
| --------------------- | ------------------------------ |
| `--fit retire`        | excluded entirely — the strongest thing a DJ can say |
| `--fit weak`          | soft demotion as next-track candidate (`candidate_bias`) |
| `--fit worked`        | mild promotion — it earned another look |
| `--placement opener`  | strongly preferred as the set's first track |
| `--placement peak`    | biased away from the opening; it wants a built room |
| `--transition 1..5`   | how well blends *into* this track landed; nudges rank |

Segment notes ride along for `set.play`: `shorter`/`longer` change how much of
the track is used. Transition rating is stored on the *incoming* track (the one
just mixed into) until pair memory exists — still enough to prefer tracks that
usually take a blend well.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Any

from . import sidecar

# Two DIFFERENT judgments, kept apart on purpose. "Did it work?" and "where
# does it belong?" are independent: a record can work brilliantly and still be
# wrong to open with. Folding them into one flag would force a DJ to overwrite
# one answer to give the other.
# `fit` vocabulary is the SSoT's (kanban/knowledge/session-coaching-multimodal-agent.md).
FITS = ("worked", "weak", "retire")
PLACEMENTS = ("opener", "peak")
SEGMENTS = ("shorter", "longer")

# How much a verdict moves a candidate's score in set.plan. `retire` is not
# here because it is an exclusion, not a penalty — a retired track is gone.
PEAK_OPENING_PENALTY = -60
OPENER_BONUS = 80

# Floor-judgment nudges on *next-track* rank. Sized below harmonic (+30) and
# in-range (+25) so physics still win; large enough that two equal-mixable
# candidates order by what the DJ said. Applied in setplan.transition_score
# so Arrange / set.plan / Deck never disagree (P-11).
WEAK_PENALTY = -28
WORKED_BONUS = 12
# transition 1..5 → bias for choosing this track as the *incoming* side.
TRANSITION_BIAS = {1: -22, 2: -12, 3: 0, 4: 8, 5: 14}


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record(
    audio: Path | str,
    fit: str | None = None,
    placement: str | None = None,
    note: str | None = None,
    segment: str | None = None,
    transition: int | None = None,
    when: str | None = None,
) -> dict[str, Any]:
    """Append one verdict to a track's sidecar. Returns the updated document."""
    if fit is not None and fit not in FITS:
        raise ValueError(f"fit must be one of {', '.join(FITS)}, got {fit!r}")
    if placement is not None and placement not in PLACEMENTS:
        raise ValueError(
            f"placement must be one of {', '.join(PLACEMENTS)}, got {placement!r}"
        )
    if segment is not None and segment not in SEGMENTS:
        raise ValueError(
            f"segment must be one of {', '.join(SEGMENTS)}, got {segment!r}"
        )
    if transition is not None and not 1 <= transition <= 5:
        raise ValueError("transition rating must be 1..5")

    doc = sidecar.read(audio)
    entries = list(doc.get("feedback") or [])
    entry: dict[str, Any] = {"at": when or _now()}
    for key, value in (
        ("fit", fit),
        ("placement", placement),
        ("note", note),
        ("segment", segment),
        ("transition", transition),
    ):
        if value is not None:
            entry[key] = value
    # A bare call would append an entry that says nothing.
    if len(entry) == 1:
        raise ValueError(
            "nothing to record — pass a fit, placement, note, segment or rating"
        )
    entries.append(entry)
    doc["feedback"] = entries
    sidecar.write(audio, doc)
    return doc


def latest(track: dict[str, Any]) -> dict[str, Any]:
    """The verdict currently in force, folded from the entry history.

    Each field takes its most recent non-null value, so a DJ can revise the
    segment length without also having to restate the verdict.
    """
    out: dict[str, Any] = {}
    for entry in track.get("feedback") or []:
        for key in ("fit", "placement", "segment", "transition", "note"):
            if entry.get(key) is not None:
                out[key] = entry[key]
    return out


def is_retired(track: dict[str, Any]) -> bool:
    return latest(track).get("fit") == "retire"


def placement_bias(track: dict[str, Any], position: int) -> int:
    """Score adjustment for putting this track at this position (1-based).

    Only the *opening* is judged. Beyond it, the harmonic and tempo scoring
    already decides placement far better than a coarse "peak-time" label could,
    and stacking a second opinion on top would just fight it.
    """
    placement = latest(track).get("placement")
    if position == 1:
        if placement == "opener":
            return OPENER_BONUS
        if placement == "peak":
            return PEAK_OPENING_PENALTY
    return 0


def candidate_bias(track: dict[str, Any]) -> int:
    """Nudge for picking this track as the *next* in a set / Arrange list.

    Fit and transition-into ratings only. Placement belongs to the opener
    picker; retire is exclusion, not a number. Never invents a verdict — missing
    fields contribute zero.
    """
    v = latest(track)
    score = 0
    fit = v.get("fit")
    if fit == "weak":
        score += WEAK_PENALTY
    elif fit == "worked":
        score += WORKED_BONUS
    rating = v.get("transition")
    if isinstance(rating, int) and rating in TRANSITION_BIAS:
        score += TRANSITION_BIAS[rating]
    return score


def seconds_for(track: dict[str, Any], default_s: float) -> float:
    """How long to play this track, honouring a `shorter`/`longer` note."""
    segment = latest(track).get("segment")
    if segment == "shorter":
        return round(default_s * 0.6, 2)
    if segment == "longer":
        return round(default_s * 1.5, 2)
    return default_s
