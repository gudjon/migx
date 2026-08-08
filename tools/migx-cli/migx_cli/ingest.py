"""Ingest — file on-disk audio into Collection/.

One job: take audio files already on disk and place them under `Collection/`
with the right name, tags, and no duplicates. Every file passes the quality
gate first (`quality.py`); ISRC is preserved when present so later
`library.resolve` can match exactly. Cover art found beside the source (or
in a downloader `.thumb/`) is copied as `cover.<ext>` next to the filed
track so `library.art` / Track TUI still work after the inbox drains.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from . import layout, naming, quality, tags, tagwrite, termart

TEMPLATES = {
    "dj": naming.TEMPLATE_DJ,
    "library": naming.TEMPLATE_LIBRARY,
    "flat": naming.TEMPLATE_FLAT,
}


def _place_cover(cover_src: Path, audio_dest: Path) -> Path | None:
    """Copy cover next to the filed audio as cover.<ext> for termart.

    Shared album folders keep one cover.jpg — never overwrite an existing
    cover file (first track wins). Returns the path that termart will find.
    """
    dest = audio_dest.parent / f"cover{cover_src.suffix.lower()}"
    if dest.exists():
        return dest if dest.is_file() else None
    try:
        shutil.copy2(cover_src, dest)
    except OSError:
        return None
    return dest


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
        # Try both credits: a store may file a collaboration under either.
        for field in ("artist", "album_artist"):
            artist = resolve.normalise(meta.get(field) or "")
            hit = index.get(f"at:{artist}|{title}")
            if hit is not None:
                break

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


def _existing_index(root: Path):
    """Index the Collection so a duplicate is caught by identity, not path.

    Path-based dedup misses the real case: the same recording filed twice
    under different artist credits ("Diplo - Don't Be Afraid" and "Soulwax -
    Don't Be Afraid" are one track). Reusing the resolver means ISRC wins,
    and scored artist/title/duration catches the rest.
    """
    from . import resolve

    resolver = resolve.get_resolver(
        "local-files", [str(layout.collection_dir(root))]
    )
    resolver.scan()
    return resolver


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
    existing = _existing_index(root)

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

        # Same recording, different filename: the store credited a different
        # artist, so the rendered path does not collide even though the track
        # is already here. Identity catches what the path cannot.
        already = existing.resolve(
            {
                "title": meta.get("title"),
                "artists": meta.get("artists") or [],
                "isrc": meta.get("isrc"),
                "duration_ms": int((verdict.get("duration_s") or 0) * 1000),
            }
        )
        if already:
            duplicates.append(
                {
                    **row,
                    "reason": f"already in Collection as "
                    f"{Path(already['path']).name} "
                    f"(matched by {already['method']})",
                    "existing_path": already["path"],
                }
            )
            continue

        # Locate cover *before* move — after a move the inbox path is gone and
        # Collection shelves do not contain _Inbox/.thumb.
        cover_src = termart.find_cover(src)
        if cover_src is not None:
            row["cover_source"] = str(cover_src)

        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if move:
                shutil.move(str(src), dest)
            else:
                shutil.copy2(src, dest)
            if tagwrite.write(dest, meta):
                row["tags_written"] = True
            if cover_src is not None and cover_src.is_file():
                placed = _place_cover(cover_src, dest)
                if placed is not None:
                    row["cover"] = str(placed)

        elif cover_src is not None:
            # Dry-run: show where the cover would land.
            row["cover"] = str(
                dest.parent / f"cover{cover_src.suffix.lower()}"
            )

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
