"""Drive migx-analyze and fold BPM/key into the sidecar.

`migx-analyze` is a C++ tool linking mixxx-lib, so the numbers come from the
same AnalyzerBeats/AnalyzerKey the app uses. There is no second detector
here (`P-11`); this module only runs it and stores what it says.

Results land in `<track>.migx/track.json` — the sidecar is the SSoT — which
is exactly where `naming.render` and the TUI already look. Analysing a track
is therefore what makes `{bpm} {camelot}` in a filename become real.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Callable, Iterable

from . import keys, sidecar

REPO = Path(__file__).resolve().parents[3]
DEFAULT_BIN = REPO / "build" / "migx-analyze"


def binary(explicit: str | None = None) -> Path:
    import os

    chosen = explicit or os.environ.get("MIGX_ANALYZE_BIN") or ""
    return Path(chosen).expanduser() if chosen else DEFAULT_BIN


def run(
    paths: Iterable[Path],
    bin_path: Path,
    on_result: Callable[[dict[str, Any]], None] | None = None,
) -> list[dict[str, Any]]:
    """Analyze files in one process, yielding each result as it lands.

    The analyzer plugins print progress chatter to stdout, so anything that
    is not a JSON object is not ours to interpret.

    Streams rather than buffering. `subprocess.run(capture_output=True)` only
    returns when the process EXITS, so a 307-track run wrote nothing for its
    entire duration: no progress to show, no way to tell healthy-slow from
    hung, and a crash on the last track would have thrown away every result
    before it. Reading line by line means each track is durable the moment the
    analyzer emits it, and `on_result` lets the caller persist as it goes.

    One process for the whole batch is still deliberate — the analyzer pays a
    real startup cost registering sound sources, and paying it per track would
    dominate the run.
    """
    args = [str(bin_path)] + [str(p) for p in paths]
    out: list[dict[str, Any]] = []
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,  # line buffered, or results arrive in 4 KB clumps
    )
    try:
        for line in proc.stdout or ():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                result = json.loads(line)
            except json.JSONDecodeError:
                continue
            out.append(result)
            if on_result is not None:
                on_result(result)
    finally:
        if proc.stdout is not None:
            proc.stdout.close()
        proc.wait(timeout=7200)
    return out


def store(result: dict[str, Any]) -> dict[str, Any]:
    """Write bpm/key into the sidecar, preserving everything already there."""
    path = Path(result["path"])
    data = sidecar.read(path)
    bpm = keys.parse_bpm(result.get("bpm"))
    if bpm is not None:
        data["bpm"] = bpm
    curve = result.get("energy_curve")
    if isinstance(curve, dict) and curve.get("all"):
        data["energy_curve"] = curve
    if result.get("duration_s"):
        data["duration_s"] = round(float(result["duration_s"]), 2)
    key_text = result.get("key")
    if key_text:
        data["key"] = key_text
        camelot = keys.to_camelot(key_text)
        if camelot:
            data["camelot"] = camelot
    sidecar.write(path, data)
    return data
