"""Resolver layer — turn a mirror identity into a local file path.

A resolver answers: *where is the audio for this identity?* Core ships
`local-files`. Other resolvers may register by name; outputs still pass the
quality gate so nothing self-certifies.

    identity -> Resolver.resolve() -> path | None -> quality.verdict() -> index

Match order, strongest first:
    1. ISRC   exact; a globally unique recording id needs no scoring
    2. score  artist + title + duration + variant, best candidate wins

The scoring model is adapted from spotDL's `utils/matching.py` (MIT), which is
the most battle-tested public implementation of this problem. Two deliberate
departures, because a DJ library is not a consumer one:

- spotDL *penalises* "remix / live / instrumental" as false positives. For a
  DJ those words are often the track you actually want. Here they are treated
  as **identity**: a variant mismatch between target and candidate is a heavy
  penalty in either direction, so "Song" never silently resolves to
  "Song (Extended Mix)" — you would think you owned a track you do not.
- Words that are genuinely noise for *matching* ("original mix", "remaster",
  "explicit") are stripped instead, and never penalised.
"""

from __future__ import annotations

import math
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

from . import quality, tags

AUDIO_EXTS = {".mp3", ".flac", ".wav", ".aif", ".aiff", ".m4a", ".alac"}

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


# Words that CHANGE which recording this is. A DJ owning the radio edit does
# not own the extended mix, so a mismatch here is a different track.
_VARIANT_TOKENS = frozenset(
    {
        "remix",
        "extended",
        "edit",
        "dub",
        "instrumental",
        "acapella",
        "cappella",
        "acoustic",
        "live",
        "vip",
        "bootleg",
        "rework",
        "reprise",
        "mix",
        "version",
        "club",
        "radio",
    }
)

# Rejection floors, adapted from spotDL's thresholds.
MIN_NAME_SCORE = 60.0
MIN_ARTIST_SCORE = 70.0
MIN_TIME_SCORE = 25.0
MIN_TOTAL_SCORE = 70.0
VARIANT_MISMATCH_PENALTY = 35.0


def similarity(left: str, right: str) -> float:
    """0-100 string similarity, order-insensitive on word order."""
    if not left or not right:
        return 0.0
    if left == right:
        return 100.0
    a = " ".join(sorted(left.split()))
    b = " ".join(sorted(right.split()))
    return SequenceMatcher(None, a, b).ratio() * 100.0


def variants(title: str) -> frozenset[str]:
    """The variant tokens present in a title, after noise is stripped."""
    return frozenset(normalise(title).split()) & _VARIANT_TOKENS


def time_score(want_ms: Any, got_s: Any) -> float | None:
    """Exponential decay on the duration delta; None when either is unknown."""
    if not want_ms or not got_s:
        return None
    delta = abs((want_ms / 1000.0) - float(got_s))
    return math.exp(-0.1 * delta) * 100.0


def score_candidate(
    entry: dict[str, Any], record: dict[str, Any]
) -> float | None:
    """Score one local file against a target entry. None means rejected."""
    target_title = entry.get("title") or ""
    cand_title = record.get("title") or ""
    name = similarity(normalise(target_title), normalise(cand_title))

    # Compare every credited artist on both sides and keep the best pair.
    #
    # Stores disagree about who the "artist" is on a collaboration. Beatport
    # sold "Jon Hopkins - Reckoning (feat. Imogen Heap)" with artist="Imogen
    # Heap" and album_artist="Jon Hopkins", while the catalogue credits Jon
    # Hopkins. Scoring only artists[0] against only `artist` scored that 27.3
    # and rejected a track bought straight off the want-list.
    target_names = [normalise(a) for a in (entry.get("artists") or [])]
    cand_names = [
        normalise(record.get(field) or "")
        for field in ("artist", "album_artist")
    ]
    pairs = [
        similarity(t, c) for t in target_names if t for c in cand_names if c
    ]
    # An untagged file cannot disprove the artist; lean on name + duration.
    artist = max(pairs) if pairs else None

    if variants(target_title) != variants(cand_title):
        name -= VARIANT_MISMATCH_PENALTY

    if name < MIN_NAME_SCORE:
        return None
    if artist is not None and artist < MIN_ARTIST_SCORE:
        return None

    timing = time_score(entry.get("duration_ms"), record.get("duration_s"))
    if timing is not None and timing < MIN_TIME_SCORE:
        return None

    parts = [name] + ([artist] if artist is not None else [])
    total = sum(parts) / len(parts)
    if timing is not None:
        # Duration confirms rather than dominates: it is the tie-breaker
        # between two plausible titles, not the primary signal.
        total = total * 0.8 + timing * 0.2
    return total if total >= MIN_TOTAL_SCORE else None


class LocalFilesResolver:
    """Resolve against files already on disk. The only resolver core ships."""

    name = "local-files"

    def __init__(self, roots: Iterable[Path]) -> None:
        self.roots = [Path(r).expanduser() for r in roots]
        self._by_isrc: dict[str, dict[str, Any]] = {}
        self._by_title: dict[str, list[dict[str, Any]]] = {}
        self._by_token: dict[str, list[dict[str, Any]]] = {}
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
        # One header parse per file: the tier is needed later anyway, and the
        # duration is what makes scoring possible at all.
        probe = quality.inspect(path)
        record = {
            "path": str(path),
            "title": meta.get("title") or path.stem,
            "artist": meta.get("artist"),
            "album_artist": meta.get("album_artist"),
            "album": meta.get("album"),
            "isrc": meta.get("isrc"),
            "duration_s": probe.get("duration_s"),
            "probe": probe,
        }
        self.scanned += 1

        if record["isrc"]:
            self._by_isrc.setdefault(record["isrc"], record)

        title_key = normalise(record["title"])
        if title_key:
            self._by_title.setdefault(title_key, []).append(record)
            # Token index so a near-miss title still surfaces as a candidate;
            # an exact-bucket lookup alone can never score what it never sees.
            for token in set(title_key.split()):
                if len(token) > 2:
                    self._by_token.setdefault(token, []).append(record)

    # ------------------------------------------------------------ resolving

    def _candidates(self, title_key: str) -> list[dict[str, Any]]:
        """Files worth scoring: the exact title bucket plus token overlap."""
        seen: dict[str, dict[str, Any]] = {}
        for record in self._by_title.get(title_key, []):
            seen[record["path"]] = record
        for token in set(title_key.split()):
            if len(token) > 2:
                for record in self._by_token.get(token, []):
                    seen[record["path"]] = record
        return list(seen.values())

    def resolve(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        """Return {path, method, confidence, score} or None."""
        isrc = (entry.get("isrc") or "").replace("-", "").upper()
        if isrc and isrc in self._by_isrc:
            record = self._by_isrc[isrc]
            return {
                "path": record["path"],
                "method": "isrc",
                "confidence": 1.0,
                "score": 100.0,
                "probe": record.get("probe"),
            }

        title_key = normalise(entry.get("title") or "")
        if not title_key:
            return None

        best, best_score = None, 0.0
        for record in self._candidates(title_key):
            score = score_candidate(entry, record)
            if score is not None and score > best_score:
                best, best_score = record, score

        if best is None:
            return None
        return {
            "path": best["path"],
            "method": "scored",
            "confidence": round(best_score / 100.0, 3),
            "score": round(best_score, 1),
            "probe": best.get("probe"),
        }


# Resolvers are addressed by name so `system.capabilities` can advertise what
# exists and an agent can pick one without reading the source. Core registers
# exactly one. A resolver registered at the edge still passes the quality gate
# in `resolve_mirror` — registration buys discovery, never trust.
REGISTRY: dict[str, type] = {LocalFilesResolver.name: LocalFilesResolver}


def available() -> list[str]:
    return sorted(REGISTRY)


def get_resolver(name: str, roots: Iterable[Path]):
    """Build a resolver by name, or fail with the list of known names."""
    try:
        factory = REGISTRY[name]
    except KeyError:
        raise ValueError(
            f"unknown resolver {name!r}; known: {', '.join(available())}"
        ) from None
    return factory(roots)


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

        probe = hit.get("probe") or quality.inspect(hit["path"])
        verdict = quality.verdict(probe, allow_tiers=allow_tiers)
        row = {
            **identity,
            "path": hit["path"],
            "method": hit["method"],
            "confidence": hit["confidence"],
            "score": hit.get("score"),
            "tier": verdict["tier"],
            "eligible": verdict["eligible"],
            "reason": verdict.get("reason"),
        }
        # A file on disk that fails the bar is NOT "missing" — it is an
        # upgrade candidate so the gap list stays exact.
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


def merge_gap_lists(lists: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Fold per-mirror gap lists into one, deduped and ranked.

    A track on seven of your playlists matters more than one saved once, so
    `on_playlists` becomes the priority signal — your own curation ranks the
    buy list without needing any external play-count source.
    """
    merged: dict[str, dict[str, Any]] = {}
    for gaps in lists:
        source = gaps.get("source_name") or "?"
        for item in gaps.get("items", []):
            key = item.get("isrc") or item.get("label") or ""
            if not key:
                continue
            row = merged.setdefault(
                key, {**item, "on_playlists": [], "sources": []}
            )
            if source not in row["sources"]:
                row["sources"].append(source)
            # An upgrade anywhere outranks missing: you already own something.
            if item.get("status") == "upgrade":
                row["status"] = "upgrade"
                row.setdefault("have_path", item.get("have_path"))
                row.setdefault("have_tier", item.get("have_tier"))

    items = sorted(
        ({**v, "on_playlists": len(v["sources"])} for v in merged.values()),
        key=lambda r: (-r["on_playlists"], r.get("label") or ""),
    )
    return {
        "schema": "migx.gap-list/1",
        "source_name": "(all mirrors)",
        "missing_count": sum(1 for i in items if i["status"] == "missing"),
        "upgrade_count": sum(1 for i in items if i["status"] == "upgrade"),
        "items": items,
    }


def gap_list(report: dict[str, Any]) -> dict[str, Any]:
    """Missing from Collection, plus on-disk files below the quality bar."""

    def _label(item: dict[str, Any]) -> str:
        artist = (item.get("artists") or [""])[0]
        return f"{artist} {item.get('title') or ''}".strip()

    items = []
    for item in report.get("missing", []):
        items.append(
            {
                **item,
                "status": "missing",
                "label": _label(item),
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
                "status": "upgrade",
                "have_path": item.get("path"),
                "have_tier": item.get("tier"),
                "label": _label(item),
            }
        )

    return {
        "schema": "migx.gap-list/1",
        "source_name": report.get("source_name"),
        "captured_week": report.get("captured_week"),
        "missing_count": report.get("missing_count", 0),
        "upgrade_count": report.get("below_bar_count", 0),
        "items": items,
    }
