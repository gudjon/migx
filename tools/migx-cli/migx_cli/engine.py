"""Talk to a running Migx engine over a local socket.

This is the **client half** of the engine command bridge
(`kanban/tasks/replace-set-play-render-with-live-transport.md`). The C++ half
does not exist yet; this defines and tests the wire contract it must implement,
so that side becomes an implementation of a settled protocol rather than a
negotiation.

## Why a client with no server is worth having

The protocol is the risky part, not the socket code. Getting the intent/receipt
shapes wrong is expensive to change once both halves exist, and every decision
here is testable offline against a fake server. So the contract lands first.

## The contract

One JSON object per line, request and response, over a **Unix domain socket**
(`QLocalServer` on the C++ side). No TCP: this must not be reachable from the
network, and a socket file inherits filesystem permissions for free.

    ->  {"cmd": "load", "deck": 1, "path": "/Volumes/.../track.mp3", "play": true}
    <-  {"ok": true, "deck": 1, "play": 1.0, "bpm": 125.0, ...}

**A receipt reports what the engine DID, not what was asked.** The bridge is a
peer input surface, exactly like a MIDI controller — the DJ can hit play on the
hardware in the same instant, so the reply carries the engine's actual control
values read back, never an echo of the request (`P-34`, and the `P-06` note in
the task card).

## Engine absent is a normal condition

Most of the time nothing is running. That is reported as a clean, typed
`not-running` result — never an exception, and never a fabricated "ok". A CLI
that pretends a deck loaded when no engine exists is the worst possible answer.
"""

from __future__ import annotations

import json
import os
import socket
from pathlib import Path
from typing import Any

# Default socket path. Under the user's runtime dir, not /tmp: /tmp is
# world-writable, and this socket accepts commands that move audio.
DEFAULT_SOCKET = Path(
    os.environ.get("MIGX_ENGINE_SOCKET")
    or (Path.home() / "Library" / "Application Support" / "Migx" / "engine.sock")
)

# A live engine answers immediately; anything slower means it is wedged, and a
# DJ waiting on a hung socket mid-set is worse than a fast honest failure.
TIMEOUT_S = 2.0

DECK_GROUP = "[Channel{}]"

# Read back after every intent, so a receipt describes the deck's real state.
RECEIPT_KEYS = ("play", "bpm", "rate", "duration", "playposition", "track_loaded")


def socket_path(explicit: str | None = None) -> Path:
    return Path(explicit).expanduser() if explicit else DEFAULT_SOCKET


def group_for(deck: int) -> str:
    """`1` -> `[Channel1]`. Decks are 1-based for a DJ, as on the hardware."""
    if deck < 1:
        raise ValueError(f"deck must be 1 or greater, got {deck}")
    return DECK_GROUP.format(int(deck))


def is_running(path: Path | None = None) -> bool:
    """Whether an engine is listening. A stale socket file is not 'running'."""
    target = path or DEFAULT_SOCKET
    if not target.exists():
        return False
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT_S)
            sock.connect(str(target))
        return True
    except (OSError, socket.timeout):
        # The file can outlive the process that made it; connecting is the only
        # honest test, and a refused connection means nothing is listening.
        return False


def request(payload: dict[str, Any], path: Path | None = None) -> dict[str, Any]:
    """Send one intent, return the engine's receipt.

    Never raises for the ordinary cases — a missing engine, a timeout, or a
    malformed reply all come back as a typed result the caller can report.
    """
    target = path or DEFAULT_SOCKET
    line = json.dumps(payload, ensure_ascii=False) + "\n"
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT_S)
            sock.connect(str(target))
            sock.sendall(line.encode("utf-8"))
            chunks: list[bytes] = []
            while b"\n" not in b"".join(chunks):
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
    except FileNotFoundError:
        return {
            "ok": False,
            "status": "not-running",
            "error": f"no engine listening at {target} — start Migx first",
        }
    except (ConnectionRefusedError, OSError, socket.timeout) as exc:
        return {
            "ok": False,
            "status": "unreachable",
            "error": f"engine at {target} did not answer: {exc}",
        }

    raw = b"".join(chunks).split(b"\n", 1)[0].decode("utf-8", "replace").strip()
    if not raw:
        return {"ok": False, "status": "no-reply", "error": "engine closed the connection"}
    try:
        reply = json.loads(raw)
    except json.JSONDecodeError as exc:
        # Do NOT treat unparseable output as failure-shaped-but-fine; the engine
        # may well have acted, and pretending otherwise would be a lie.
        return {
            "ok": False,
            "status": "bad-reply",
            "error": f"engine sent something that is not JSON ({exc}): {raw[:120]}",
        }
    if not isinstance(reply, dict):
        return {"ok": False, "status": "bad-reply", "error": "reply was not an object"}
    return reply


def load(
    deck: int, path_to_audio: Path | str, play: bool = True, sock: Path | None = None
) -> dict[str, Any]:
    """Load a track onto a deck, optionally starting it.

    `play` rides along with the load rather than being a second call: the C++
    side maps this to `PlayerManager::slotLoadLocationToPlayer(location, group,
    play)`, which starts the deck as part of loading. Issuing a separate `play`
    afterwards would race the load.
    """
    audio = Path(path_to_audio).expanduser()
    if not audio.is_file():
        return {
            "ok": False,
            "status": "no-such-track",
            "error": f"not a file: {audio}",
        }
    return request(
        {
            "cmd": "load",
            "deck": int(deck),
            "group": group_for(deck),
            "path": str(audio.resolve()),
            "play": bool(play),
        },
        sock,
    )


def status(deck: int | None = None, sock: Path | None = None) -> dict[str, Any]:
    """What the engine is actually doing — the TUI's source of deck truth."""
    payload: dict[str, Any] = {"cmd": "status", "keys": list(RECEIPT_KEYS)}
    if deck is not None:
        payload["deck"] = int(deck)
        payload["group"] = group_for(deck)
    return request(payload, sock)
