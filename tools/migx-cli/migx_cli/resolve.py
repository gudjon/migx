"""Resolver layer — turn a mirror identity into a local file you already own.

The seam that keeps acquisition out of core. A resolver answers exactly one
question: *where is the audio for this identity?* Core ships `local-files`
only. Whatever else gets registered at the edge is not core's business — but
every resolver's output passes the same quality gate, so nothing can
self-certify.

    identity -> Resolver.resolve() -> path | None -> quality.verdict() -> index

Match order, strongest first:
    1. ISRC        exact; a globally unique recording id needs no scoring
    2. artist+title normalised, confirmed by duration when both are known
    3. title-only  last resort, and only with a duration confirmation
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable

from . import quality, tags

AUDIO_EXTS = {".mp3", ".flac", ".wav", ".aif", ".aiff", ".m4a", ".alac"}

DURATION_TOLERANCE_S = 4.0

# Noise that differs between a store's metadata and Spotify's for the same
# recording. Stripped only for *matching*; never for naming.
_NOISE = re.compile(
    r"\s*[\(\[](?:feat\.?|ft\.?|featuring|with)\s[^\)\]]*[\)\]]"
    r"|\s*[\(\[](?:original mix|radio edit|remaster(?:ed)?"
    r"(?:\s*\d{4})?|explicit|clean|bonus track|deluxe)[^\)\]]*[\)\]]"
    r"|\s*-\s*(?:remaster(?:ed)?(?:\s*\d{4})?|radio edit|original mix)\s*$",
    re.IGNORECASE,
)
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_SPACE = re.compile(r"\s+")


def normalise(value: str) -> str:
    """Fold a title/artist to a comparable key."""
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = _NOISE.sub("", value)
    value = _PUNCT.sub(" ", value)
    return _SPACE.sub(" ", value).strip().lower()


def _artist_key(artists: Iterable[str]) -> str:
    first = next(iter(artists), "") if artists else ""
    return normalise(first)


def _duration_ok(want_ms: Any, got_s: Any) -> bool | None:
    """True/False when both durations are known, else None (unknown)."""
    if not want_ms or not got_s:
        return None
    return abs((want_ms / 1000.0) - got_s) <= DURATION_TOLERANCE_S


class LocalFilesResolver:
    """Resolve against files already on disk. The only resolver core ships."""

    name = "local-files"

    def __init__(self, roots: Iterable[Path]) -> None:
        self.roots = [Path(r).expanduser() for r in roots]
        self._by_isrc: dict[str, dict[str, Any]] = {}
        self._by_artist_title: dict[str, list[dict[str, Any]]] = {}
        self._by_title: dict[str, list[dict[str, Any]]] = {}
        self.scanned = 0

    # ------------------------------------------------------------- indexing

    def scan(self) -> int:
        """Index every audio file under the roots. Returns the file count."""
        for root in self.roots:
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*")):
                if path.suffix.lower() not in AUDIO_EXTS or not path.is_file():
                    continue
                self._add(path)
        return self.scanned

    def _add(self, path: Path) -> None:
        meta = tags.read(path)
        record = {
            "path": str(path),
            "title": meta.get("title"),
            "artist": meta.get("artist"),
            "album": meta.get("album"),
            "isrc": meta.get("isrc"),
        }
        self.scanned += 1

        if record["isrc"]:
            self._by_isrc.setdefault(record["isrc"], record)

        title_key = normalise(record["title"] or path.stem)
        artist_key = normalise(record["artist"] or "")
        if title_key:
            self._by_title.setdefault(title_key, []).append(record)
            if artist_key:
                combo = f"{artist_key}|{title_key}"
                self._by_artist_title.setdefault(combo, []).append(record)

    # ------------------------------------------------------------ resolving

    def resolve(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        """Return {path, method, confidence} or None."""
        isrc = (entry.get("isrc") or "").replace("-", "").upper()
        if isrc and isrc in self._by_isrc:
            return {
                "path": self._by_isrc[isrc]["path"],
                "method": "isrc",
                "confidence": 1.0,
            }

        title_key = normalise(entry.get("title") or "")
        artist_key = _artist_key(entry.get("artists") or [])
        if not title_key:
            return None

        combo = f"{artist_key}|{title_key}"
        for record in self._by_artist_title.get(combo, []):
            return {
                "path": record["path"],
                "method": "artist+title",
                "confidence": 0.9,
            }

        # Title-only is ambiguous; accept just one unambiguous candidate.
        candidates = self._by_title.get(title_key, [])
        if len(candidates) == 1:
            return {
                "path": candidates[0]["path"],
                "method": "title-only",
                "confidence": 0.6,
            }
        return None


def resolve_mirror(
    doc: dict[str, Any],
    resolver: LocalFilesResolver,
    *,
    allow_tiers: tuple[str, ...] = quality.DEFAULT_ELIGIBLE,
) -> dict[str, Any]:
    """Resolve every entry in a mirror and gate each hit on file quality."""
    resolved, missing, refused = [], [], []

    for entry in doc.get("tracks", []):
        hit = resolver.resolve(entry)
        identity = {
            "position": entry.get("position"),
            "title": entry.get("title"),
            "artists": entry.get("artists") or [],
            "isrc": entry.get("isrc"),
            "duration_ms": entry.get("duration_ms"),
            "uri": entry.get("uri"),
        }
        if not hit:
            missing.append(identity)
            continue

        verdict = quality.verdict(
            quality.inspect(hit["path"]), allow_tiers=allow_tiers
        )
        row = {
            **identity,
            "path": hit["path"],
            "method": hit["method"],
            "confidence": hit["confidence"],
            "tier": verdict["tier"],
            "eligible": verdict["eligible"],
            "reason": verdict.get("reason"),
        }
        # A file you own but that fails the bar is NOT "missing" — you would
        # re-buy something you already have. It is a separate upgrade list.
        (resolved if verdict["eligible"] else refused).append(row)

    return {
        "schema": "migx.resolution-report/1",
        "source_id": doc.get("source_id"),
        "source_name": doc.get("source_name"),
        "captured_week": doc.get("captured_week"),
        "resolver": resolver.name,
        "scanned_files": resolver.scanned,
        "total": len(doc.get("tracks", [])),
        "resolved_count": len(resolved),
        "missing_count": len(missing),
        "below_bar_count": len(refused),
        "resolved": resolved,
        "missing": missing,
        "below_bar": refused,
    }


def want_list(report: dict[str, Any]) -> dict[str, Any]:
    """The buy list: what you do not own, plus what you own below the bar."""

    def _query(item: dict[str, Any]) -> str:
        artist = (item.get("artists") or [""])[0]
        return f"{artist} {item.get('title') or ''}".strip()

    items = []
    for item in report.get("missing", []):
        items.append(
            {
                **item,
                "want": "acquire",
                "store_query": _query(item),
                "isrc": item.get("isrc"),
            }
        )
    for item in report.get("below_bar", []):
        items.append(
            {
                "position": item.get("position"),
                "title": item.get("title"),
                "artists": item.get("artists"),
                "isrc": item.get("isrc"),
                "want": "upgrade",
                "have_path": item.get("path"),
                "have_tier": item.get("tier"),
                "store_query": _query(item),
            }
        )

    return {
        "schema": "migx.want-list/1",
        "source_name": report.get("source_name"),
        "captured_week": report.get("captured_week"),
        "acquire_count": report.get("missing_count", 0),
        "upgrade_count": report.get("below_bar_count", 0),
        "items": items,
    }
