"""Phase alignment — start the incoming track ON the outgoing track's downbeat.

Tempo matching and phase matching are different problems, and only the first
was solved. `mixing.beatmatch` makes both records run at the same speed; that
is necessary and not sufficient. Two tracks at identical BPM whose bars do not
coincide sound like a flam, not a mix — the kick lands twice, slightly apart.

## What alignment needs

Three quantities, all already available:

    bar length      60 / bpm * 4          (mixing.beatmatch reports bar_s)
    where we are    Deck.position_s()
    where to enter  the incoming track's own bar grid

The move is: wait until the OUTGOING track crosses a bar line, and at that
instant start the INCOMING track from one of ITS bar lines. Both grids then
advance together.

## The honest limitation

Migx has no first-beat offset yet — `library.analyze` gives bpm and key, not a
beatgrid origin. So the grid is assumed to start at t=0 of the file. That is
correct for a track topped-and-tailed on the beat and wrong by a fixed offset
for one with a ragged start.

This is stated rather than hidden because the failure is *systematic, not
random*: a track whose grid is offset by 0.2s will be consistently 0.2s out,
every time, in the same direction. That is fixable later by one number per
track in the sidecar — and until that number exists, alignment is an
improvement on nothing, not a guarantee.

Everything here is pure arithmetic on seconds. No audio, no I/O, no clock —
the caller supplies the position, so it is testable without playing anything.
"""

from __future__ import annotations

BEATS_PER_BAR = 4


def bar_seconds(bpm: float, beats_per_bar: int = BEATS_PER_BAR) -> float:
    """How long one bar lasts at this tempo."""
    if not bpm or bpm <= 0:
        raise ValueError(f"bpm must be positive, got {bpm}")
    return (60.0 / float(bpm)) * beats_per_bar


def next_bar_line(position_s: float, bpm: float, origin_s: float = 0.0) -> float:
    """The next bar boundary at or after `position_s`.

    `origin_s` is where the grid starts — a first-beat offset when we have one.
    Exactly on a line counts as that line, not the next: a caller asking at the
    downbeat wants to fire now, not wait a whole bar.
    """
    bar = bar_seconds(bpm)
    elapsed = position_s - origin_s
    if elapsed <= 0:
        return origin_s
    bars_done = elapsed / bar
    whole = int(bars_done)
    if abs(bars_done - whole) < 1e-9:      # already on the line
        return origin_s + whole * bar
    return origin_s + (whole + 1) * bar


def snap_to_bar(position_s: float, bpm: float, origin_s: float = 0.0) -> float:
    """The bar line at or BEFORE a position — where to enter a track.

    Rounds down, never up: entering later than intended can clip the phrase the
    DJ chose, while a bar earlier is musically safe.
    """
    bar = bar_seconds(bpm)
    elapsed = position_s - origin_s
    if elapsed <= 0:
        return max(0.0, origin_s)
    return origin_s + int(elapsed / bar) * bar


def align(
    outgoing_position_s: float,
    outgoing_bpm: float,
    incoming_entry_s: float,
    incoming_bpm: float,
    tempo_ratio: float = 1.0,
    outgoing_origin_s: float = 0.0,
    incoming_origin_s: float = 0.0,
) -> dict[str, float]:
    """When to fire the incoming deck, and where in the track to start it.

    Returns `wait_s` (how long to hold before launching) and `start_s` (the
    incoming offset, snapped to its own bar grid).

    `tempo_ratio` matters: a track played at 1.02x has bars 2% shorter than its
    own tag implies, so its grid must be measured at the PLAYED tempo or the
    two drift apart within a phrase — the exact bug this function exists to
    prevent, reintroduced one layer down.
    """
    fire_at = next_bar_line(outgoing_position_s, outgoing_bpm, outgoing_origin_s)
    played_bpm = float(incoming_bpm) * (tempo_ratio or 1.0)
    start_s = snap_to_bar(incoming_entry_s, played_bpm, incoming_origin_s)
    return {
        "wait_s": round(max(0.0, fire_at - outgoing_position_s), 4),
        "start_s": round(start_s, 4),
        "fire_at_s": round(fire_at, 4),
        "out_bar_s": round(bar_seconds(outgoing_bpm), 4),
        "in_bar_s": round(bar_seconds(played_bpm), 4),
    }
