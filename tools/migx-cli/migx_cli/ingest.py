"""Ingest — the intake valve that keeps the Collection clean.

One job: take audio files that are already on disk and file them into
`Collection/` with the right name, the right tags, and no duplicates. It does
not acquire anything; it normalises what you bring it, whatever the source —
a CD you ripped, a Bandcamp or Beatport purchase, a promo.

Every file passes the quality gate before it is filed (`quality.py`), and every
filed file carries its ISRC when one is known, so a later `library.resolve`
matches it exactly instead of guessing.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from . import layout, naming, quality, tags, tagwrite

TEMPLATES = {
    "dj": naming.TEMPLATE_DJ,
    "library": naming.TEMPLATE_LIBRARY,
    "flat": naming.TEMPLATE_FLAT,
}


def _mirror_index(doc: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    """Index mirror entries by ISRC and by normalised artist|title."""
    from . import resolve

    index: dict[str, dict[str, Any]] = {}
    if not doc:
        return index
    for entry in doc.get("tracks", []):
        isrc = (entry.get("isrc") or "").replace("-", "").upper()
        if isrc:
            index.setdefault(f"isrc:{isrc}", entry)
        title = resolve.normalise(entry.get("title") or "")
        artist = resolve.normalise((entry.get("artists") or [""])[0])
        if title:
            index.setdefault(f"at:{artist}|{title}", entry)
    return index


def _identify(path: Path, index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Best available metadata: the mirror's when matched, else the
    file's own tags."""
    from . import resolve

    meta = tags.read(path)
    isrc = (meta.get("isrc") or "").replace("-", "").upper()

    hit = None
    if isrc:
        hit = index.get(f"isrc:{isrc}")
    if hit is None:
        title = resolve.normalise(meta.get("title") or path.stem)
        artist = resolve.normalise(meta.get("artist") or "")
        hit = index.get(f"at:{artist}|{title}")

    if hit:
        # Mirror wins on identity (it is the canonical catalogue record), but
        # never invents what it does not have.
        return {
            "title": hit.get("title") or meta.get("title"),
            "artists": hit.get("artists")
            or ([meta["artist"]] if meta.get("artist") else []),
            "artist": (hit.get("artists") or [meta.get("artist")])[0],
            "album": hit.get("album") or meta.get("album"),
            "album_artist": hit.get("album_artist")
            or meta.get("album_artist"),
            "track_number": hit.get("track_number")
            or meta.get("track_number"),
            "disc_number": hit.get("disc_number"),
            "release_date": hit.get("release_date"),
            "isrc": hit.get("isrc") or meta.get("isrc"),
            "bpm": meta.get("bpm"),
            "camelot": meta.get("camelot"),
            "matched": "mirror",
        }

    return {
        "title": meta.get("title") or path.stem,
        "artists": [meta["artist"]] if meta.get("artist") else [],
        "artist": meta.get("artist"),
        "album": meta.get("album"),
        "album_artist": meta.get("album_artist"),
        "track_number": meta.get("track_number"),
        "isrc": meta.get("isrc"),
        "bpm": meta.get("bpm"),
        "camelot": meta.get("camelot"),
        "matched": "file-tags",
    }


def ingest(
    sources: list[Path],
    root: Path,
    *,
    mirror: dict[str, Any] | None = None,
    template: str = "dj",
    move: bool = False,
    dry_run: bool = False,
    allow_tiers: tuple[str, ...] = quality.DEFAULT_ELIGIBLE,
) -> dict[str, Any]:
    index = _mirror_index(mirror)
    tmpl = TEMPLATES.get(template, naming.TEMPLATE_DJ)

    filed, refused, duplicates = [], [], []

    for src in sources:
        src = Path(src)
        verdict = quality.verdict(
            quality.inspect(src), allow_tiers=allow_tiers
        )
        meta = _identify(src, index)

        row = {
            "source": str(src),
            "title": meta.get("title"),
            "artist": meta.get("artist"),
            "isrc": meta.get("isrc"),
            "tier": verdict["tier"],
            "matched": meta["matched"],
        }

        if not verdict["eligible"]:
            refused.append({**row, "reason": verdict.get("reason")})
            continue

        dest = layout.collection_path(
            root, meta, template=tmpl, ext=src.suffix.lstrip(".")
        )
        row["destination"] = str(dest)

        if dest.exists():
            # The Collection already holds this exact path. Never silently
            # overwrite and never file a second copy — that is the invariant.
            duplicates.append({**row, "reason": "already in Collection"})
            continue

        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if move:
                shutil.move(str(src), dest)
            else:
                shutil.copy2(src, dest)
            if tagwrite.write(dest, meta):
                row["tags_written"] = True

        filed.append(row)

    return {
        "schema": "migx.ingest-report/1",
        "collection": str(layout.collection_dir(root)),
        "template": template,
        "dry_run": dry_run,
        "filed_count": len(filed),
        "refused_count": len(refused),
        "duplicate_count": len(duplicates),
        "filed": filed,
        "refused": refused,
        "duplicates": duplicates,
    }
