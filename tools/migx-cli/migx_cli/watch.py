"""Watch _Inbox and file what lands there.

The hazard this is built around: **a file still downloading looks exactly
like a finished one.** Ingesting a half-written MP3 files a truncated track,
writes a wrong ISRC into it, and the quality gate happily passes it because
the first 200 frames of a 320 CBR file are 320 CBR whether or not the rest
arrived.

So nothing is touched until it has been *quiet* — identical size and mtime
across two consecutive polls spanning at least `settle` seconds. A download
in progress fails that on every tick; a finished file passes on the first
one after it lands.

    _Inbox/  ──stable?──▶ ingest ──▶ Collection/ ──▶ analyze ──▶ sidecar

Moves rather than copies by default: an inbox that never drains gets
re-scanned forever, and every scan re-reads the tags of files already filed.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

DEFAULT_INTERVAL_S = 10.0
DEFAULT_SETTLE_S = 20.0

# Ceiling on a single `--once` drain. MUST stay below the launchd StartInterval
# in com.gudjon.migx.watch.plist (300 s), or launchd starts a second pass while
# the first is still draining and two processes ingest one inbox concurrently —
# a double-file race, not merely slow. It was 600 s, i.e. twice the interval,
# and a drain that hit the ceiling blocked a caller for a full ten minutes.
DEFAULT_MAX_WAIT_S = 240.0

# Downloader leftovers that share the inbox. Never audio, never our business.
IGNORED_SUFFIXES = {".srt", ".part", ".crdownload", ".download", ".tmp"}
IGNORED_DIRS = {".thumb", ".temp", ".Trash"}

# Where already-filed files are parked so the inbox drains. Never deleted —
# the watcher must not destroy a purchase because it thinks it has a copy.
FILED_DIR = "_filed"
IGNORED_DIRS.add(FILED_DIR)


def park(path: Path, inbox: Path) -> Path | None:
    """Move an already-filed file aside so it stops being rescanned."""
    target_dir = inbox / FILED_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / path.name
    stem, suffix, index = target.stem, target.suffix, 1
    while target.exists():
        target = target_dir / f"{stem} ({index}){suffix}"
        index += 1
    try:
        path.replace(target)
    except OSError:
        return None
    return target


def candidates(inbox: Path, audio_exts: set[str]) -> list[Path]:
    """Audio files directly in the inbox tree, skipping downloader debris."""
    if not inbox.is_dir():
        return []
    out = []
    for path in sorted(inbox.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if path.name.startswith("."):
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in IGNORED_SUFFIXES:
            continue
        if path.suffix.lower() not in audio_exts:
            continue
        out.append(path)
    return out


def _fingerprint(path: Path) -> tuple[int, float] | None:
    try:
        st = path.stat()
    except OSError:
        return None
    return (st.st_size, st.st_mtime)


def stable_files(
    inbox: Path,
    audio_exts: set[str],
    seen: dict[str, tuple[tuple[int, float], float]],
    settle_s: float,
    now: float | None = None,
) -> list[Path]:
    """Files unchanged for `settle_s`. Mutates `seen` as the poll memory.

    `seen` maps path -> (fingerprint, first time we saw that fingerprint).
    A changed fingerprint resets the clock, so a slow download simply never
    matures until it stops growing.
    """
    now = time.time() if now is None else now
    ready: list[Path] = []
    live: set[str] = set()

    for path in candidates(inbox, audio_exts):
        key = str(path)
        live.add(key)
        fingerprint = _fingerprint(path)
        if fingerprint is None:
            continue
        previous = seen.get(key)
        if previous is None:
            seen[key] = (fingerprint, now)
            # First sighting: poll history cannot vouch for it, but the
            # filesystem can. A file whose mtime is already older than the
            # settle window has demonstrably finished writing — without this,
            # a single pass (--once, launchd) could never file anything,
            # because everything is new on the first tick.
            if now - fingerprint[1] >= settle_s:
                ready.append(path)
            continue
        if previous[0] != fingerprint:
            seen[key] = (fingerprint, now)
            continue
        if now - previous[1] >= settle_s:
            ready.append(path)

    # Forget files that left the inbox, so a re-drop is treated as new.
    for key in set(seen) - live:
        seen.pop(key, None)
    return ready


def run(
    inbox: Path,
    audio_exts: set[str],
    on_ready: Callable[[list[Path]], dict[str, Any]],
    interval_s: float = DEFAULT_INTERVAL_S,
    settle_s: float = DEFAULT_SETTLE_S,
    once: bool = False,
    max_wait_s: float = DEFAULT_MAX_WAIT_S,
    log: Callable[[str], None] = print,
) -> int:
    """Poll until interrupted, or until the inbox is drained when `once`.

    `once` deliberately does NOT mean one instantaneous poll. launchd's
    WatchPaths fires the moment a file *arrives*, when it is zero seconds old
    and cannot possibly have settled — and no second event follows, because
    nothing changes again. A single snapshot would therefore never file
    anything. So `once` drains: it keeps polling while candidates exist that
    have not settled yet, and exits when nothing is left waiting.
    """
    seen: dict[str, tuple[tuple[int, float], float]] = {}
    filed = 0
    deadline = time.time() + max_wait_s
    log(
        f"watching {inbox}  (poll {interval_s:g}s, settle {settle_s:g}s)"
        f"{' — draining' if once else ''}"
    )
    try:
        while True:
            ready = stable_files(inbox, audio_exts, seen, settle_s)
            if ready:
                log(f"{time.strftime('%H:%M:%S')}  {len(ready)} settled")
                result = on_ready(ready)
                filed += result.get("filed_count", 0)
            if once:
                pending = [
                    p
                    for p in candidates(inbox, audio_exts)
                    if p not in set(ready)
                ]
                if not pending or time.time() >= deadline:
                    if pending:
                        log(
                            f"{len(pending)} still unsettled after "
                            f"{max_wait_s:g}s — leaving for the next run"
                        )
                    return filed
            time.sleep(interval_s)
    except KeyboardInterrupt:
        log(f"\nstopped — {filed} track(s) filed this session")
        return filed
