"""Last.fm read-only client — the play-history signal layer.

Why this exists: a Spotify mirror says a track is *on a list*. A scrobble says
you played it, how often, and **what you played next**. Play counts turn an
undifferentiated gap list into a priority order, and consecutive scrobbles are
the transition corpus `initiative-ai-djing-product` is built on.

Same posture as the Spotify client (`api.py`):

1. **Official host only** — `ws.audioscrobbler.com`, enforced, not assumed.
2. **Public read methods only** — user.getInfo / getLovedTracks / getTopTracks
   / getRecentTracks. These need an API key, no user authorisation.
3. **No shared secret.** It signs *write* calls (scrobble, love, account
   changes). We never write, so we never hold it.
4. **Paced.** 252k scrobbles is ~1,300 pages; a naive loop is exactly the
   burst that gets a key throttled.

See `kanban/tasks/lastfm-signal-layer.md` for product notes.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterator
from urllib.parse import urlparse

from . import ratelimit

API_BASE = "https://ws.audioscrobbler.com/2.0/"
ALLOWED_HOSTS = frozenset({"ws.audioscrobbler.com"})

USER_AGENT = "migx-cli/1 (+https://github.com/gudjon/migx; read-only)"

# Last.fm caps most paged methods at 200 per page.
PAGE_LIMIT = 200
MAX_RETRIES = 4

PERIODS = ("overall", "7day", "1month", "3month", "6month", "12month")


class LastfmError(RuntimeError):
    pass


def assert_allowed_url(url: str) -> None:
    host = (urlparse(url).hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise LastfmError(
            f"refusing request to non-API host {host!r} "
            f"(allowed: {sorted(ALLOWED_HOSTS)})"
        )


class LastfmRead:
    """Read-only Last.fm client. Never signs, never writes."""

    def __init__(
        self,
        api_key: str,
        user: str,
        pacer: ratelimit.Pacer | None = None,
    ) -> None:
        if not api_key:
            raise LastfmError(
                "no Last.fm API key — set lastfm.api_key in "
                "~/.config/migx/config.json or pass --api-key"
            )
        if not user:
            raise LastfmError("no Last.fm username — set lastfm.user")
        self._key = api_key
        self.user = user
        self.pacer = pacer or ratelimit.Pacer()
        self.requests = 0

    def call(self, method: str, **params: Any) -> dict[str, Any]:
        query = {
            "method": method,
            "user": self.user,
            "api_key": self._key,
            "format": "json",
            **{k: v for k, v in params.items() if v is not None},
        }
        url = f"{API_BASE}?{urllib.parse.urlencode(query)}"
        assert_allowed_url(url)

        for attempt in range(MAX_RETRIES):
            self.pacer.wait()
            self.requests += 1
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    self.pacer.backoff(attempt, exc.headers.get("Retry-After"))
                    continue
                if 500 <= exc.code < 600 and attempt < MAX_RETRIES - 1:
                    self.pacer.backoff(attempt)
                    continue
                raise LastfmError(f"HTTP {exc.code} for {method}") from exc
            except urllib.error.URLError as exc:
                if attempt < MAX_RETRIES - 1:
                    self.pacer.backoff(attempt)
                    continue
                raise LastfmError(f"network error: {exc.reason}") from exc

            # Last.fm returns errors as HTTP 200 with an `error` code, so a
            # status check alone would silently accept failure.
            if isinstance(body, dict) and "error" in body:
                raise LastfmError(
                    f"Last.fm error {body['error']}: "
                    f"{body.get('message', 'unknown')}"
                )
            return body

        raise LastfmError(f"exhausted {MAX_RETRIES} attempts for {method}")

    # ------------------------------------------------------------- surfaces

    def info(self) -> dict[str, Any]:
        return self.call("user.getInfo").get("user", {})

    def _paged(
        self,
        method: str,
        root: str,
        node: str,
        limit: int | None = None,
        **params: Any,
    ) -> Iterator[dict[str, Any]]:
        """Walk a paged Last.fm collection, newest first."""
        page = 1
        seen = 0
        while True:
            body = self.call(
                method, limit=PAGE_LIMIT, page=page, **params
            ).get(root, {})
            items = body.get(node) or []
            if isinstance(items, dict):  # single result is not wrapped
                items = [items]
            if not items:
                return
            for item in items:
                yield item
                seen += 1
                if limit and seen >= limit:
                    return

            attrs = body.get("@attr") or {}
            total_pages = int(attrs.get("totalPages") or 1)
            if page >= total_pages:
                return
            page += 1

    def loved(self, limit: int | None = None) -> Iterator[dict[str, Any]]:
        yield from self._paged(
            "user.getLovedTracks", "lovedtracks", "track", limit
        )

    def top_tracks(
        self, period: str = "overall", limit: int | None = None
    ) -> Iterator[dict[str, Any]]:
        if period not in PERIODS:
            raise LastfmError(f"period {period!r} not in {', '.join(PERIODS)}")
        yield from self._paged(
            "user.getTopTracks", "toptracks", "track", limit, period=period
        )

    def recent(
        self, limit: int | None = None, since: int | None = None
    ) -> Iterator[dict[str, Any]]:
        """Scrobbles, newest first. `since` is a unix timestamp.

        Passing `since` is how an archive stays cheap: after the first full
        pull we only ever ask for what happened after the last scrobble.
        """
        yield from self._paged(
            "user.getRecentTracks",
            "recenttracks",
            "track",
            limit,
            **({"from": since} if since else {}),
        )


# ------------------------------------------------------------- normalising


def _text(node: Any) -> str:
    """Last.fm returns either a bare string or {'#text': ...}."""
    if isinstance(node, dict):
        return str(node.get("#text") or node.get("name") or "").strip()
    return str(node or "").strip()


def entry(track: dict[str, Any]) -> dict[str, Any]:
    """Normalise one Last.fm track into the shape resolve.py already scores."""
    artist = _text(track.get("artist"))
    played = (track.get("date") or {}).get("uts")
    mbid = track.get("mbid") or None
    playcount = track.get("playcount")

    return {
        "title": _text(track.get("name")),
        "artists": [artist] if artist else [],
        "album": _text(track.get("album")) or None,
        "mbid": mbid,
        "url": track.get("url"),
        "playcount": int(playcount) if playcount else None,
        "played_at": int(played) if played else None,
        # Last.fm has no ISRC. resolve.py's scored path handles that — it is
        # exactly the artist+title+duration case it was built for.
        "isrc": None,
    }
