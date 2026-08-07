"""ASCII energy sparkline with cue markers.

A DJ reads arrangement from shape: where the intro ends, where the breakdown
sits, how long the outro runs. A sparkline puts that in one line of a
terminal, and putting the cue markers *under* it turns a note like "mix out
at 4:35" into something you can see against the music.

    ▁▁▁▁▃▃▂▃▆▇▇▇▇▇▇▇▆▇▇█▇▅▅▇▅▆▄▂▁▇▇▇▇▇▇▇▆▇▆
        ▲intro over        ▲drop      ▲mix out

Pure text: no curses, no colour codes. The caller decides how to paint it,
and the same function serves a plain --json dump or a printed report.
"""

from __future__ import annotations

from typing import Any, Sequence

BLOCKS = " ▁▂▃▄▅▆▇█"


def sparkline(values: Sequence[float], width: int = 64) -> str:
    """Render 0..1 values as block characters, resampled to `width`."""
    if not values or width <= 0:
        return ""
    out = []
    count = len(values)
    for column in range(width):
        # Average the values falling in this column so downsampling does not
        # simply drop peaks between samples.
        start = column * count // width
        end = max(start + 1, (column + 1) * count // width)
        window = [v for v in values[start:end] if isinstance(v, (int, float))]
        level = sum(window) / len(window) if window else 0.0
        index = max(
            0, min(len(BLOCKS) - 1, int(level * (len(BLOCKS) - 1) + 0.5))
        )
        out.append(BLOCKS[index])
    return "".join(out)


def cue_ruler(
    cues: Sequence[dict[str, Any]],
    duration_s: float,
    width: int = 64,
    labels: bool = True,
) -> list[str]:
    """A marker line under a sparkline, plus optional label lines."""
    if not cues or duration_s <= 0 or width <= 0:
        return []
    marks = [" "] * width
    placed: list[tuple[int, str]] = []
    for cue in cues:
        position = cue.get("position")
        if position is None:
            continue
        column = int(float(position) / duration_s * width)
        column = max(0, min(width - 1, column))
        marks[column] = "▲"
        placed.append((column, str(cue.get("label") or "")))

    lines = ["".join(marks)]
    if not labels:
        return lines

    # One label per line, left-aligned to its marker, so long DJ notes never
    # collide with each other.
    for column, label in sorted(placed):
        if label:
            lines.append(" " * column + label[: max(8, width - column)])
    return lines
