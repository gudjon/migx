"""Render a planned set into one continuous, beatmatched mix.

`setplan` decides the ORDER. This performs it: each track is pitched onto the
running deck tempo and crossfaded into the next, producing a single audio file
you can actually listen to.

This is the first thing in the CLI that makes a *sound*, so be clear about what
it is and is not:

- It is **not** the engine. There is no deck, no RT thread, no live mixing.
  This is an offline render (`arch-analyzer`-class batch work), so none of the
  `P-02` real-time rules apply — and equally, nothing here may ever be reused
  on the audio callback path.
- It is **not** a second beatmatcher. The pitch numbers come from
  `mixing.beatmatch()`, the same source the Deck view shows a DJ. A render that
  disagreed with the on-screen plan would be worse than no render (`P-11`).

## The one musical decision: tempo drift

Beatmatching chains. Track 2 is pitched onto track 1's tempo, track 3 onto
*that* tempo, and so on. The running tempo is therefore each track's **played**
BPM (`bpm × ratio`), not its native one — so a beatmatched run holds a constant
tempo rather than drifting a little further with every transition, and the
tempo only moves when a track is cut in at its native speed.

A track that cannot reach the running tempo within `MAX_PITCH` is **not**
pitched. It plays native and gets a short crossfade instead — the honest
equivalent of a DJ cutting rather than forcing a mix no fader can perform.
Silently applying a 30% tempo change would produce a mix that technically
beatmatches and musically falls apart.

Requires `ffmpeg` on PATH (override with `MIGX_FFMPEG_BIN`).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from . import mixing

# The pitch fader most gear actually has. Past this we cut instead of beatmatch.
MAX_PITCH = 0.08

# ffmpeg's atempo is only well-behaved in this band; outside it we would be
# stacking filters to fake a ratio no DJ would use anyway.
ATEMPO_MIN, ATEMPO_MAX = 0.5, 2.0

DEFAULT_SECONDS = 90.0
DEFAULT_CROSSFADE = 12.0
CUT_CROSSFADE = 3.0

# Where to enter a track when it has no usable cue. A quarter in clears most
# intros without landing mid-drop.
DEFAULT_ENTRY = 0.25

# Cue labels that mean "the mix starts here", in the DJ's own words.
ENTRY_WORDS = ("intro is over", "mix in", "start mixing", "mix start", "drop")


def ffmpeg_bin() -> str | None:
    return os.environ.get("MIGX_FFMPEG_BIN") or shutil.which("ffmpeg")


def entry_point(track: dict[str, Any]) -> float:
    """Where to start playing this track."""
    for cue in track.get("cues") or []:
        label = (cue.get("label") or "").lower()
        if any(word in label for word in ENTRY_WORDS):
            position = cue.get("position_s")
            if isinstance(position, (int, float)) and position >= 0:
                return float(position)
    duration = track.get("duration_s") or 0.0
    return round(duration * DEFAULT_ENTRY, 2)


def build_segments(
    rows: list[dict[str, Any]],
    seconds: float = DEFAULT_SECONDS,
    crossfade: float = DEFAULT_CROSSFADE,
) -> list[dict[str, Any]]:
    """Decide, per track, how fast to play it and where to come in.

    `rows` are `setplan` rows (they carry bpm/camelot/path/duration_s).
    """
    segments: list[dict[str, Any]] = []
    running_bpm: float | None = None

    for index, row in enumerate(rows):
        bpm = row.get("bpm")
        ratio = 1.0
        beatmatched = False

        if index > 0 and running_bpm and bpm:
            plan = mixing.beatmatch(running_bpm, bpm)
            # beatmatch() reports what B needs to sit on A's grid. Ignore the
            # double/half-time relation here: halving a track's speed for a
            # render is a musical choice, not a rescue.
            if not plan.get("relation"):
                wanted = running_bpm / float(bpm)
                if abs(wanted - 1.0) <= MAX_PITCH and (
                    ATEMPO_MIN <= wanted <= ATEMPO_MAX
                ):
                    ratio = wanted
                    beatmatched = True

        segments.append(
            {
                "position": index + 1,
                "path": row.get("path"),
                "name": row.get("name"),
                "bpm": bpm,
                "camelot": row.get("camelot"),
                "start_s": entry_point(row),
                # Play long enough that a crossfade is a blend, not a stumble.
                "play_s": round(seconds, 2),
                "tempo_ratio": round(ratio, 6),
                "beatmatched": beatmatched,
                "played_bpm": round(float(bpm) * ratio, 2) if bpm else None,
                # A cut gets a short fade; a real beatmatch gets a full blend.
                "crossfade_s": (
                    round(crossfade, 2) if beatmatched or index == 0
                    else CUT_CROSSFADE
                ),
            }
        )
        # Re-anchor: once this track is alone it defines the tempo, so drift
        # never compounds across the whole set.
        running_bpm = float(bpm) * ratio if bpm else running_bpm

    return segments


def build_command(segments: list[dict[str, Any]], out: Path) -> list[str]:
    """The ffmpeg invocation that renders these segments into one mix."""
    binary = ffmpeg_bin() or "ffmpeg"
    argv: list[str] = [binary, "-y", "-v", "error"]
    for seg in segments:
        argv += [
            "-ss", f"{seg['start_s']:.3f}",
            "-t", f"{seg['play_s']:.3f}",
            "-i", str(seg["path"]),
        ]

    parts: list[str] = []
    for index, seg in enumerate(segments):
        chain = f"[{index}:a]"
        if abs(seg["tempo_ratio"] - 1.0) > 1e-9:
            chain += f"atempo={seg['tempo_ratio']:.6f},"
        else:
            chain += ""
        chain += "aformat=sample_rates=44100:channel_layouts=stereo"
        parts.append(f"{chain}[a{index}]")

    if len(segments) == 1:
        parts.append("[a0]anull[out]")
    else:
        current = "[a0]"
        for index in range(1, len(segments)):
            label = "[out]" if index == len(segments) - 1 else f"[x{index}]"
            fade = segments[index]["crossfade_s"]
            parts.append(
                f"{current}[a{index}]acrossfade=d={fade:.2f}:c1=tri:c2=tri{label}"
            )
            current = label

    argv += ["-filter_complex", ";".join(parts), "-map", "[out]", str(out)]
    return argv


def render(
    segments: list[dict[str, Any]], out: Path, timeout_s: float = 1800.0
) -> dict[str, Any]:
    """Run the render. Reports ffmpeg's own error rather than a bare failure."""
    if ffmpeg_bin() is None:
        return {
            "ok": False,
            "error": "ffmpeg not found — install it (brew install ffmpeg) "
            "or set MIGX_FFMPEG_BIN",
        }
    out.parent.mkdir(parents=True, exist_ok=True)
    argv = build_command(segments, out)
    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, timeout=timeout_s
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"ffmpeg timed out after {timeout_s:g}s"}
    if proc.returncode != 0:
        return {
            "ok": False,
            "error": (proc.stderr or "").strip()[:600] or "ffmpeg failed",
        }
    return {"ok": True, "path": str(out)}


def expected_duration(segments: list[dict[str, Any]]) -> float:
    """How long the rendered mix should be, given tempo and overlaps.

    `play_s` is trimmed from the SOURCE, before atempo. Speeding a track up
    shortens it: 60 s taken at ratio 1.05 emerges as 60/1.05 = 57.1 s. Summing
    `play_s` directly overstates the mix — it read 309 s for a render that
    measured 302.8 s, and would drift further the more the set is pitched.
    """
    if not segments:
        return 0.0
    total = sum(
        s["play_s"] / (s["tempo_ratio"] or 1.0) for s in segments
    )
    total -= sum(s["crossfade_s"] for s in segments[1:])
    return round(total, 2)
