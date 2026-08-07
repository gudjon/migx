"""API pacing, backoff, and a refresh lock.

1. **Skip when possible** — unchanged `snapshot_id` means no track pages
   (`playlist.pull` short-circuit).
2. **Pace** — minimum gap between calls so bursts do not trip rolling windows.
3. **Back off** — honour `Retry-After` with jitter so parallel clients do not
   stampede.
4. **Refresh lock** — serialise token refresh across processes.
"""

from __future__ import annotations

import os
import random
import threading
import time
from pathlib import Path
from typing import Any

# Conservative default: ~3–4 requests/second sustained. Spotify's limit is a
# rolling ~30s window; bursts trip it, not totals. A 2000-track pull at 50
# items/page is ~40 pages — still under a minute at this pace, with headroom
# for concurrent agent + human use of the same app.
DEFAULT_MIN_INTERVAL_S = 0.3

# Never sleep longer than this for a single backoff step.
MAX_BACKOFF_S = 60.0


class Pacer:
    """Enforce a minimum gap between requests, plus jittered backoff."""

    def __init__(self, min_interval_s: float = DEFAULT_MIN_INTERVAL_S) -> None:
        self.min_interval_s = max(0.0, min_interval_s)
        self._lock = threading.Lock()
        self._last = 0.0
        self.waited_s = 0.0
        self.throttled = 0

    def wait(self) -> None:
        """Block long enough to keep pace. Call before each request."""
        with self._lock:
            now = time.monotonic()
            gap = now - self._last
            if self._last and gap < self.min_interval_s:
                delay = self.min_interval_s - gap
                time.sleep(delay)
                self.waited_s += delay
            self._last = time.monotonic()

    def backoff(self, attempt: int, retry_after: float | None = None) -> float:
        """Sleep for a 429/5xx and return how long we slept.

        `Retry-After` is Spotify telling us exactly what it wants; we honour it
        and add a small jitter rather than second-guessing it.
        """
        self.throttled += 1
        if retry_after is not None:
            delay = float(retry_after) + random.uniform(0.1, 1.0)
        else:
            # Exponential with full jitter — avoids retry stampedes.
            ceiling = min(MAX_BACKOFF_S, 2.0**attempt)
            delay = random.uniform(0.0, ceiling)
        delay = min(delay, MAX_BACKOFF_S)
        time.sleep(delay)
        self.waited_s += delay
        return delay


class RefreshLock:
    """Cross-process lock around the OAuth token refresh.

    This guards a genuine race, not a hypothetical one: Spotify rotates refresh
    tokens, and the old one dies the moment a new one is issued. Two migx
    commands refreshing concurrently would each get a token, and whichever
    wrote to the Keychain second would leave the other holding a dead token —
    the user is silently logged out and cannot tell why.

    An O_EXCL lockfile is enough; this is one user on one machine.
    """

    def __init__(
        self, path: Path | str | None = None, timeout_s: float = 30.0
    ) -> None:
        self.path = Path(path or (Path.home() / ".migx-spotify-refresh.lock"))
        self.timeout_s = timeout_s
        self._fd: int | None = None

    def __enter__(self) -> "RefreshLock":
        deadline = time.monotonic() + self.timeout_s
        while True:
            try:
                self._fd = os.open(
                    self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600
                )
                os.write(self._fd, str(os.getpid()).encode("ascii"))
                return self
            except FileExistsError:
                if self._stale():
                    self._release_path()
                    continue
                if time.monotonic() >= deadline:
                    # Better to proceed than to hard-fail a user command; the
                    # worst case is the race we were avoiding.
                    return self
                time.sleep(0.1)

    def __exit__(self, *exc: Any) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        self._release_path()

    def _stale(self, max_age_s: float = 120.0) -> bool:
        """A crashed process must not lock everyone out forever."""
        try:
            return (time.time() - self.path.stat().st_mtime) > max_age_s
        except OSError:
            return False

    def _release_path(self) -> None:
        try:
            self.path.unlink()
        except OSError:
            pass
