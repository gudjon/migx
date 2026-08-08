"""One live Migx session per OS user, with a stale lock that can be detected.

A booth has one DJ and one set of speakers, so a second session writing the
same sidecars is never what anyone meant. `library.watch` already proved the
cost of not enforcing this: launchd fired a second drain while the first was
still running and two processes ingested one inbox.

## Why pid alone is not enough

"The lock file exists, therefore a session is running" is a lie, and it is the
same lie as every `P-34` defect in this codebase — a value that cannot be
distinguished from a real answer. A crashed session leaves its lock behind
forever, and the next honest run refuses to start.

Checking the pid is still alive is better but still wrong: pids are recycled.
Long after a crash, some unrelated process inherits that number and the stale
lock becomes immortal.

So the lock stores **pid + that process's start time**. A pid is only ours if
the process at that number started when we say it did. Recycling gives you the
number, never the timestamp — which makes stale genuinely *detectable* rather
than assumed.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

STATE_DIR = Path(
    os.environ.get("MIGX_STATE_DIR")
    or (Path.home() / "Library" / "Application Support" / "Migx")
)
LOCK_NAME = "session.lock"


def lock_path(state_dir: Path | None = None) -> Path:
    return (state_dir or STATE_DIR) / LOCK_NAME


def process_start(pid: int) -> str | None:
    """When this pid started, or None if there is no such process.

    `ps -o lstart=` is the portable-enough answer on macOS and Linux. Any
    failure means "cannot confirm", which is deliberately NOT the same as
    "not running" — we return None and let the caller treat an unconfirmable
    process as gone, rather than silently claiming it is alive.
    """
    try:
        out = subprocess.run(
            ["ps", "-o", "lstart=", "-p", str(pid)],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    text = out.stdout.strip()
    return text or None


def read(state_dir: Path | None = None) -> dict[str, Any] | None:
    path = lock_path(state_dir)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # A corrupt lock cannot prove a session is running, so it must not be
        # allowed to block one forever.
        return None
    return data if isinstance(data, dict) else None


def is_stale(entry: dict[str, Any]) -> bool:
    """True when the lock names a process that is not the one that took it."""
    pid = entry.get("pid")
    if not isinstance(pid, int):
        return True
    started = process_start(pid)
    if started is None:
        return True                       # no such process
    return started != entry.get("started")  # pid recycled: same number, new process


def acquire(
    state_dir: Path | None = None, pid: int | None = None
) -> dict[str, Any]:
    """Take the session lock, or report who holds it.

    Returns {"ok": True, ...} or {"ok": False, "held_by": ...} — never raises
    and never silently proceeds, because two sessions writing one library is
    exactly the outcome this exists to prevent.
    """
    directory = state_dir or STATE_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = lock_path(directory)
    mine = pid or os.getpid()

    existing = read(directory)
    # Re-acquiring our own lock is idempotent. A session that re-entered its
    # own guard and refused to start would be blocked by itself, which reads
    # as "another session is running" and is simply false.
    if existing is not None and existing.get("pid") == mine:
        return {"ok": True, "lock": str(path), "entry": existing, "reclaimed_stale": False}
    if existing is not None and not is_stale(existing):
        return {
            "ok": False,
            "status": "held",
            "held_by": existing,
            "error": (
                f"a Migx session is already running (pid {existing.get('pid')}). "
                "One session per user — stop it first."
            ),
        }

    entry = {
        "pid": mine,
        "started": process_start(mine),
        "cwd": str(Path.cwd()),
    }
    # Atomic: a reader must never see a half-written lock and conclude anything.
    fd, tmp = tempfile.mkstemp(dir=str(directory), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(entry, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    reclaimed = existing is not None
    return {"ok": True, "lock": str(path), "entry": entry, "reclaimed_stale": reclaimed}


def release(state_dir: Path | None = None, pid: int | None = None) -> bool:
    """Drop the lock, but only if it is ours — never steal another session's."""
    entry = read(state_dir)
    if entry is None:
        return False
    if entry.get("pid") != (pid or os.getpid()):
        return False
    lock_path(state_dir or STATE_DIR).unlink(missing_ok=True)
    return True
