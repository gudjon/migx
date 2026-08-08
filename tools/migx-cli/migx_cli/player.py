"""Live playback for the TUI — one deck at a time, decided as it plays.

The difference from `setplay` is not sound quality, it is *when the decisions
happen*. `setplay` renders a file: every transition is fixed before you hear a
note, and nothing you say during the set can change it. This starts one track,
reports where it is, and lets the NEXT choice be made while the current one is
still playing — so `track.feedback` changes what comes next tonight, not
tomorrow.

## What this is not

Not a mixer. macOS gives us `afplay` (no volume control) and `ffplay` (filters
fixed at launch), and migx-cli carries zero third-party dependencies — so there
is no live crossfader here. A blend is *scheduled* when the incoming deck
starts, not ridden by hand.

Saying that plainly matters: a TUI that drew a crossfader it could not move
would be the same lie as a Prep header promising an apply key that does not
exist. When real fader control is wanted, it comes from the engine
(`replace-set-play-render-with-live-transport`), not from a second audio path
grown here.

## Why subprocess and not a library

The audio never enters this process. We spawn a player, hold its pid, and read
the clock. That keeps Python entirely off the audio path — there is no buffer
here to underrun, and a slow TUI redraw cannot glitch playback.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

# How long to wait before believing a player actually started. Long enough for
# a broken binary to die, short enough not to be felt as latency.
START_CONFIRM_S = 0.35


def player_bin() -> tuple[str, str] | None:
    """(binary, kind) — ffplay preferred because it can pitch and fade."""
    explicit = os.environ.get("MIGX_PLAYER_BIN")
    if explicit:
        return explicit, "ffplay" if "ffplay" in explicit else "afplay"
    found = shutil.which("ffplay")
    if found:
        return found, "ffplay"
    found = shutil.which("afplay")
    if found:
        return found, "afplay"
    return None


class Deck:
    """One playing track. Holds a pid and a start time — nothing else.

    Position is *derived* from the wall clock rather than tracked, because a
    counter we increment ourselves would drift from what you actually hear, and
    a position that disagrees with the speakers is worse than no position.
    """

    def __init__(self) -> None:
        self.proc: subprocess.Popen | None = None
        self.track: dict[str, Any] | None = None
        self.started_at: float | None = None
        self.start_offset: float = 0.0
        self.tempo_ratio: float = 1.0

    def is_playing(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def position_s(self) -> float | None:
        """Where we are in the track, in ITS timeline (tempo accounted for)."""
        if not self.is_playing() or self.started_at is None:
            return None
        elapsed = time.time() - self.started_at
        return self.start_offset + elapsed * self.tempo_ratio

    def play(
        self,
        track: dict[str, Any],
        start_s: float = 0.0,
        tempo_ratio: float = 1.0,
        fade_in_s: float = 0.0,
    ) -> dict[str, Any]:
        """Start a track. Stops whatever this deck was playing first."""
        chosen = player_bin()
        if chosen is None:
            return {
                "ok": False,
                "error": "no player found — install ffmpeg (ffplay) or use afplay",
            }
        binary, kind = chosen
        path = Path(track.get("path") or "")
        if not path.is_file():
            return {"ok": False, "error": f"not a file: {path}"}

        self.stop()
        if kind == "ffplay":
            argv = [binary, "-nodisp", "-autoexit", "-loglevel", "quiet",
                    "-ss", f"{start_s:.3f}", str(path)]
            filters = []
            if abs(tempo_ratio - 1.0) > 1e-9:
                filters.append(f"atempo={tempo_ratio:.6f}")
            if fade_in_s > 0:
                filters.append(f"afade=t=in:st=0:d={fade_in_s:.2f}")
            if filters:
                argv[1:1] = ["-af", ",".join(filters)]
        else:
            # afplay cannot seek, pitch or fade. Report that rather than
            # pretending the request was honoured.
            argv = [binary, str(path)]

        self.proc = subprocess.Popen(
            argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
        )
        # A pid is NOT evidence of playback. A broken player (missing dylib,
        # unsupported codec) exits in milliseconds while Popen still hands back
        # a healthy-looking process object — reporting ok:True there is exactly
        # the "green while knowing nothing" defect this codebase keeps
        # producing. So confirm it is still alive before claiming it plays.
        time.sleep(START_CONFIRM_S)
        if self.proc.poll() is not None:
            err = b""
            try:
                err = (self.proc.stderr.read() or b"") if self.proc.stderr else b""
            except OSError:
                pass
            code = self.proc.returncode
            self.proc = None
            return {
                "ok": False,
                "error": (
                    f"{kind} exited immediately (code {code}) — it is installed "
                    "but not working. "
                    + err.decode("utf-8", "replace").strip()[:300]
                ),
            }
        self.track = track
        self.started_at = time.time()
        self.start_offset = start_s if kind == "ffplay" else 0.0
        self.tempo_ratio = tempo_ratio if kind == "ffplay" else 1.0
        return {
            "ok": True,
            "player": kind,
            "pid": self.proc.pid,
            "honoured": kind == "ffplay",
            "note": None if kind == "ffplay" else
            "afplay cannot seek, pitch or fade — playing from 0 at native tempo",
        }

    def stop(self) -> bool:
        if not self.is_playing():
            self.proc = None
            return False
        assert self.proc is not None
        try:
            self.proc.send_signal(signal.SIGTERM)
            self.proc.wait(timeout=2)
        except (OSError, subprocess.TimeoutExpired):
            try:
                self.proc.kill()
            except OSError:
                pass
        self.proc = None
        self.started_at = None
        return True

    def state(self) -> dict[str, Any]:
        """What is true right now — read from the process, never assumed."""
        position = self.position_s()
        duration = (self.track or {}).get("duration_s")
        return {
            "playing": self.is_playing(),
            "name": (self.track or {}).get("name"),
            "path": (self.track or {}).get("path"),
            "position_s": round(position, 1) if position is not None else None,
            "duration_s": duration,
            "remaining_s": (
                round(duration - position, 1)
                if position is not None and duration else None
            ),
            "tempo_ratio": self.tempo_ratio,
        }
