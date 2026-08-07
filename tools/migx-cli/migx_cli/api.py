"""Thin Spotify Web API client — stdlib only, read-only.

Engineering constraints for a reliable client:

1. **Documented hosts only** — `api.spotify.com` (auth lives in `auth.py`).
2. **User OAuth bearer** — PKCE access tokens only.
3. **Metadata endpoints** — playlist/library identity; no audio stream handling here.
4. **Read-only scopes** — enforced in `auth.SCOPES`.
5. **Polite client** — pace, honour `Retry-After`, circuit-break on repeated 429s,
   sticky `fields=` across pagination, skip work via `snapshot_id` when possible.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterator
from urllib.parse import urlparse

from . import ratelimit

API_BASE = "https://api.spotify.com/v1"
API_HOST = "api.spotify.com"
# Only these hosts may ever receive a request from this module.
ALLOWED_HOSTS = frozenset({API_HOST})

MAX_RETRIES = 5
# After this many consecutive 429s, stop cold. Continuing to retry past
# Spotify's patience is how temporary throttles become longer blocks.
MAX_CONSECUTIVE_429 = 3

# Identifies the client honestly. A real User-Agent is the opposite of the
# evasion pattern that gets clients blocked.
USER_AGENT = "migx-cli/1 (+https://github.com/gudjon/migx)"

# Sparse field filters on *stable* endpoints only. We deliberately do not
# field-filter `/items` or `/me/tracks` body rows: the 2026-03 migration
# renamed nested keys (`track` → `item` on some paths), and a wrong filter
# would silently return empty mirrors. Meta + playlist index shapes are
# stable and worth filtering.
#
# owner.id is load-bearing for development-mode ownership checks (display_name
# alone is not unique). tracks(total) was dropped: /me/playlists no longer
# returns a tracks object even without a fields filter (2026 Web API).
_PLAYLIST_META_FIELDS = "id,name,snapshot_id,owner(display_name,id)"
_PLAYLIST_LIST_FIELDS = (
    "next,items(id,name,owner(display_name,id),snapshot_id)"
)


class ApiError(RuntimeError):
    pass


class RateLimitError(ApiError):
    """Raised when we stop to protect access after repeated 429s."""


def assert_allowed_url(url: str) -> None:
    """Reject any request that is not to the official Web API host.

    Pagination `next` links come from Spotify and should always be on
    api.spotify.com. If they ever aren't, we refuse rather than follow.
    """
    host = (urlparse(url).hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise ApiError(
            f"refusing request to non-API host {host!r} "
            f"(allowed: {sorted(ALLOWED_HOSTS)}). "
            "Migx only talks to the official Spotify Web API."
        )


def _parse_429_body(raw: bytes) -> dict[str, Any]:
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


def reapply_query_params(url: str, sticky: dict[str, Any]) -> str:
    """Merge sticky query params onto a pagination `next` URL.

    Spotify's `next` links preserve offset/limit but **drop** `fields=`.
    Following them raw yields page 1 sparse and page 2+ full-shape — silent
    misclassification (e.g. ownership surveys keyed on owner.id). Always
    re-apply filters that must stay stable across the whole walk.
    """
    if not sticky:
        return url
    parts = urllib.parse.urlsplit(url)
    query = dict(urllib.parse.parse_qsl(parts.query, keep_blank_values=True))
    for key, value in sticky.items():
        if value is None:
            continue
        query[key] = str(value)
    return urllib.parse.urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urllib.parse.urlencode(query),
            parts.fragment,
        )
    )


class SpotifyRead:
    """Read-only official Web API client."""

    def __init__(
        self, token: str, pacer: ratelimit.Pacer | None = None
    ) -> None:
        if not token or not isinstance(token, str):
            raise ApiError("missing access token")
        self._token = token
        self.pacer = pacer or ratelimit.Pacer()
        self.requests = 0
        self._consecutive_429 = 0

    def get(self, path: str, **params: Any) -> dict[str, Any]:
        url = path if path.startswith("http") else f"{API_BASE}{path}"
        if params:
            # Drop Nones so optional filters stay clean.
            clean = {k: v for k, v in params.items() if v is not None}
            if clean:
                url = f"{url}?{urllib.parse.urlencode(clean)}"
        assert_allowed_url(url)

        for attempt in range(MAX_RETRIES):
            # Pace *before* every attempt, including retries: a burst is
            # what trips the rolling window, not the total request count.
            self.pacer.wait()
            self.requests += 1
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json",
                },
                method="GET",
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    self._consecutive_429 = 0
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body = exc.read()
                if exc.code == 429:
                    self._handle_429(attempt, exc, body, url)
                    continue
                if exc.code == 401:
                    raise ApiError(
                        "access token rejected — run `migx spotify.login`"
                    ) from exc
                if exc.code == 403:
                    detail = body.decode("utf-8", "replace")[:300]
                    raise ApiError(
                        f"403 for {url}\n"
                        f"Spotify said: {detail}\n"
                        "Common causes, most likely first:\n"
                        "  1. Development-mode apps can only read items from"
                        " playlists you created or collaborate on.\n"
                        "  2. Spotify-owned playlists (Discover Weekly,"
                        " Release Radar, Daylist, and the 37i9dQZF1... family)"
                        " need a pre-2024-11-27 quota extension. Duplicate"
                        " into a playlist you own, then pull that.\n"
                        "  3. Liked Songs is not a playlist — use"
                        " `playlist.pull liked`."
                    ) from exc
                if exc.code == 404:
                    # Never retry 404 — it is not transient.
                    raise ApiError(
                        f"404 — not found or not visible to this"
                        f" account: {url}"
                    ) from exc
                if 500 <= exc.code < 600 and attempt < MAX_RETRIES - 1:
                    self.pacer.backoff(attempt)
                    continue
                raise ApiError(f"HTTP {exc.code} for {url}") from exc
            except urllib.error.URLError as exc:
                if attempt < MAX_RETRIES - 1:
                    self.pacer.backoff(attempt)
                    continue
                raise ApiError(
                    f"network error for {url}: {exc.reason}"
                ) from exc

        raise ApiError(f"exhausted {MAX_RETRIES} attempts for {url}")

    def _handle_429(
        self,
        attempt: int,
        exc: urllib.error.HTTPError,
        body: bytes,
        url: str,
    ) -> None:
        self._consecutive_429 += 1
        parsed = _parse_429_body(body)
        reason = (parsed.get("error") or {}).get("reason") or parsed.get(
            "reason"
        )
        retry_after = exc.headers.get("Retry-After")
        retry_s = float(retry_after) if retry_after else None

        if reason == "QUOTA_EXCEEDED":
            raise RateLimitError(
                "Spotify returned 429 QUOTA_EXCEEDED — this is an app/developer "
                "quota limit, not a temporary pace issue. Stop, wait for the "
                "quota window to reset, and reduce pull frequency. Do not retry "
                "in a loop. See https://developer.spotify.com/documentation/"
                "web-api/concepts/rate-limits"
            ) from exc

        if self._consecutive_429 >= MAX_CONSECUTIVE_429:
            raise RateLimitError(
                f"Spotify rate-limited us {self._consecutive_429} times in a "
                f"row (last Retry-After={retry_s!r}). Stopping to protect API "
                f"access. Wait and re-run later; prefer "
                f"`playlist.pull --if-changed` so unchanged playlists cost one "
                f"metadata request only. URL: {url}"
            ) from exc

        if attempt >= MAX_RETRIES - 1:
            raise RateLimitError(
                f"429 on final attempt for {url}; Retry-After={retry_s!r}"
            ) from exc

        # Honour Retry-After exactly (+ small jitter inside pacer).
        self.pacer.backoff(attempt, retry_s)

    def paged(self, path: str, **params: Any) -> Iterator[dict[str, Any]]:
        """Yield every item across a paging object, following `next` links.

        Sticky params (`fields`, and any other non-paging keys the caller
        passed) are re-applied on every page. Spotify's `next` omits them.
        """
        params.setdefault("limit", 50)
        # Params that must not change mid-walk. offset is owned by `next`.
        sticky = {
            k: v
            for k, v in params.items()
            if k not in ("offset", "limit") and v is not None
        }
        page = self.get(path, **params)
        while True:
            for item in page.get("items", []):
                yield item
            nxt = page.get("next")
            if not nxt:
                return
            # Full URL + host allowlist + sticky fields (never drop mid-walk).
            page = self.get(reapply_query_params(nxt, sticky))

    # ------------------------------------------------------------ surfaces

    def me(self) -> dict[str, Any]:
        return self.get("/me")

    def playlists(self) -> Iterator[dict[str, Any]]:
        yield from self.paged("/me/playlists", fields=_PLAYLIST_LIST_FIELDS)

    def playlist(self, playlist_id: str) -> dict[str, Any]:
        return self.get(
            f"/playlists/{playlist_id}", fields=_PLAYLIST_META_FIELDS
        )

    def playlist_items(self, playlist_id: str) -> Iterator[dict[str, Any]]:
        """Playlist contents via `/items`.

        The old `/playlists/{id}/tracks` endpoint was removed in the
        2026-03-09 API migration and now 403s for every playlist. `/items`
        replaces it and renames `track` -> `item` in each row; `mirror.build`
        accepts both shapes so `/me/tracks` (still `track`) keeps working.
        """
        yield from self.paged(f"/playlists/{playlist_id}/items")

    def saved_tracks(self) -> Iterator[dict[str, Any]]:
        """Liked Songs — official `/me/tracks` only."""
        yield from self.paged("/me/tracks")
