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
from typing import Any, Iterable

from . import keys, sidecar

REPO = Path(__file__).resolve().parents[3]
DEFAULT_BIN = REPO / "build" / "migx-analyze"


def binary(explicit: str | None = None) -> Path:
    import os

    chosen = explicit or os.environ.get("MIGX_ANALYZE_BIN") or ""
    return Path(chosen).expanduser() if chosen else DEFAULT_BIN


def run(paths: Iterable[Path], bin_path: Path) -> list[dict[str, Any]]:
    """Analyze files in one process; parse only the JSON lines.

    The analyzer plugins print progress chatter to stdout, so anything that
    is not a JSON object is not ours to interpret.
    """
    args = [str(bin_path)] + [str(p) for p in paths]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=7200)
    out = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def store(result: dict[str, Any]) -> dict[str, Any]:
    """Write bpm/key into the sidecar, preserving everything already there."""
    path = Path(result["path"])
    data = sidecar.read(path)
    bpm = keys.parse_bpm(result.get("bpm"))
    if bpm is not None:
        data["bpm"] = bpm
    key_text = result.get("key")
    if key_text:
        data["key"] = key_text
        camelot = keys.to_camelot(key_text)
        if camelot:
            data["camelot"] = camelot
    sidecar.write(path, data)
    return data
