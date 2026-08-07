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


# Heat levels, low to high. A DJ scans for shape, so the ramp has to read at a
# glance: cool for quiet, hot for loud, with the top level reserved for peaks
# so a track's climaxes stand out rather than blending into the body.
HEAT_LEVELS = 5


def heat(level: float) -> int:
    """Map a 0..1 energy value to a heat band (0 = coolest)."""
    if level <= 0:
        return 0
    return max(0, min(HEAT_LEVELS - 1, int(level * HEAT_LEVELS)))


def waveform(
    values: Sequence[float], width: int = 72, height: int = 8
) -> list[tuple[str, list[int]]]:
    """A block waveform as (row_text, per-column heat) pairs.

    Returned rather than printed so the caller paints it — curses needs the
    heat band per column to pick a colour pair, and a plain terminal can drop
    the colour and still read the shape.

    Drawn top-down so the loudest columns reach the top row, which is how a
    waveform is read everywhere else.
    """
    if not values or width <= 0 or height <= 0:
        return []

    count = len(values)
    columns: list[float] = []
    for column in range(width):
        start = column * count // width
        end = max(start + 1, (column + 1) * count // width)
        window = [v for v in values[start:end] if isinstance(v, (int, float))]
        columns.append(sum(window) / len(window) if window else 0.0)

    rows: list[tuple[str, list[int]]] = []
    for row in range(height):
        # Row 0 is the top, so it lights up only for the loudest columns.
        floor = (height - 1 - row) / height
        ceiling = (height - row) / height
        chars, heats = [], []
        for value in columns:
            if value >= ceiling:
                chars.append("█")
            elif value <= floor:
                chars.append(" ")
            else:
                fraction = (value - floor) / max(1e-9, ceiling - floor)
                index = max(
                    1,
                    min(
                        len(BLOCKS) - 1,
                        int(fraction * (len(BLOCKS) - 1) + 0.5),
                    ),
                )
                chars.append(BLOCKS[index])
            heats.append(heat(value))
        rows.append(("".join(chars), heats))
    return rows


def time_axis(duration_s: float, width: int = 72, ticks: int = 5) -> str:
    """A minute ruler under a waveform, so a cue position is locatable."""
    if duration_s <= 0 or width <= 0:
        return ""
    line = [" "] * width
    for tick in range(ticks):
        column = int(tick * (width - 1) / max(1, ticks - 1))
        seconds = duration_s * column / max(1, width - 1)
        label = f"{int(seconds) // 60}:{int(seconds) % 60:02d}"
        start = min(
            max(0, column - (0 if tick == 0 else len(label) // 2)),
            width - len(label),
        )
        for offset, char in enumerate(label):
            if start + offset < width:
                line[start + offset] = char
    return "".join(line)
