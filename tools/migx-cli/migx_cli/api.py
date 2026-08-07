"""Thin Spotify Web API client — stdlib only, read-only.

Handles pagination and 429 backpressure.

Metadata only. This client never requests, decodes, or stores audio: Spotify's
audio is DRM-protected and app-bound, and ripping it violates their ToS
(`kanban/knowledge/spotify-octave-style-doable-steps.md`). We read identities.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterator

from . import ratelimit

API_BASE = "https://api.spotify.com/v1"
MAX_RETRIES = 5

# Identifies the client honestly. Spotify asks for a real User-Agent, and a
# recognisable one is the opposite of the evasion that actually gets clients
# blocked.
USER_AGENT = "migx-cli/1 (+https://github.com/gudjon/migx)"


class ApiError(RuntimeError):
    pass


class SpotifyRead:
    def __init__(
        self, token: str, pacer: ratelimit.Pacer | None = None
    ) -> None:
        self._token = token
        self.pacer = pacer or ratelimit.Pacer()
        self.requests = 0

    def get(self, path: str, **params: Any) -> dict[str, Any]:
        url = path if path.startswith("http") else f"{API_BASE}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        for attempt in range(MAX_RETRIES):
            # Pace *before* every attempt, including retries: a burst is what
            # trips the rolling window, not the total request count.
            self.pacer.wait()
            self.requests += 1
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    # Spotify telling us exactly what it wants. Honour it.
                    retry_after = exc.headers.get("Retry-After")
                    self.pacer.backoff(
                        attempt,
                        float(retry_after) if retry_after else None,
                    )
                    continue
                if exc.code == 401:
                    raise ApiError(
                        "access token rejected — run `migx spotify.login`"
                    ) from exc
                if exc.code == 403:
                    raise ApiError(
                        f"403 for {url}\n"
                        "Spotify-owned playlists (Discover Weekly,"
                        " Release Radar, Daylist) "
                        "are unavailable to apps without a"
                        " pre-2024-11-27 quota extension. "
                        "Duplicate the playlist inside Spotify, then"
                        " pull your copy."
                    ) from exc
                if exc.code == 404:
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

    def paged(self, path: str, **params: Any) -> Iterator[dict[str, Any]]:
        """Yield every item across a paging object, following `next` links."""
        params.setdefault("limit", 50)
        page = self.get(path, **params)
        while True:
            for item in page.get("items", []):
                yield item
            nxt = page.get("next")
            if not nxt:
                return
            page = self.get(nxt)

    # ------------------------------------------------------------ surfaces

    def me(self) -> dict[str, Any]:
        return self.get("/me")

    def playlists(self) -> Iterator[dict[str, Any]]:
        yield from self.paged("/me/playlists")

    def playlist(self, playlist_id: str) -> dict[str, Any]:
        return self.get(f"/playlists/{playlist_id}")

    def playlist_items(self, playlist_id: str) -> Iterator[dict[str, Any]]:
        yield from self.paged(
            f"/playlists/{playlist_id}/tracks",
            additional_types="track",
        )

    def saved_tracks(self) -> Iterator[dict[str, Any]]:
        """Liked Songs."""
        yield from self.paged("/me/tracks")
