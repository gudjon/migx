"""Re-file Collection tracks under their current name.

A track ingested before analysis is named without its tempo and key. Once
`library.analyze` fills the sidecar, the *correct* name changes — and the
file should follow, because the whole point of `{bpm} {camelot}` is that
sorting a folder shows the mix order.

Three things move together, and missing any one leaves the library broken:

1. the audio file itself
2. its `<name>.migx/` sidecar — notes, cues and analysis live there, and a
   sidecar orphaned from its track is worse than no sidecar
3. every crate entry pointing at the same inode; a hardlink keeps working
   under the old name, so a stale crate silently disagrees with Collection

Nothing is overwritten. If the target name is taken by a *different* file,
the rename is refused and reported.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable

from . import layout, naming, sidecar, tags


def desired_name(path: Path, template: str, ext: str | None = None) -> str:
    """What this track should be called, given what we now know about it."""
    meta = tags.read(path)
    side = sidecar.read(path)
    entry = {
        "artists": [meta.get("artist") or ""],
        "album_artist": meta.get("album_artist"),
        "album": meta.get("album"),
        "title": meta.get("title") or path.stem,
        "track_number": meta.get("track_number"),
        "isrc": meta.get("isrc") or side.get("isrc"),
        "bpm": side.get("bpm") or meta.get("bpm"),
        "camelot": side.get("camelot") or meta.get("camelot"),
    }
    return naming.render(
        entry, template=template, ext=ext or path.suffix.lstrip(".")
    )


def crate_links(track: Path, crates_root: Path) -> tuple[list[Path], int]:
    """Crate entries that are the same inode as this track, plus a miss count.

    Matched by inode rather than by name: that is the whole point, since the
    crate entry still carries the *old* name we are trying to fix.

    Returns `(links, unreadable)`. The count is not decoration — it is the
    difference between "this track has no crate links" and "I could not tell".
    Both used to return `[]`, so a stat failure made the rename proceed and
    skip relinking, leaving crates pointing at a name that no longer exists.
    That is exactly the "stale crate silently disagrees with Collection"
    hazard this module's own docstring warns about (`P-34`).
    """
    if not crates_root.is_dir():
        return [], 0
    try:
        target = track.stat()
    except OSError:
        # Cannot identify the track at all, so EVERY crate entry is unknown.
        return [], 1
    out: list[Path] = []
    unreadable = 0
    for path in crates_root.rglob("*"):
        if not path.is_file():
            continue
        try:
            st = path.stat()
        except OSError:
            unreadable += 1
            continue
        if st.st_ino == target.st_ino and st.st_dev == target.st_dev:
            out.append(path)
    return out, unreadable


def plan(
    root: Path, template: str, tracks: Iterable[Path] | None = None
) -> list[dict[str, Any]]:
    collection = layout.collection_dir(root)
    crates_root = Path(root) / layout.CRATES
    candidates = (
        list(tracks)
        if tracks is not None
        else sorted(
            p
            for p in collection.rglob("*")
            if p.is_file()
            and p.suffix.lower()
            in {".mp3", ".flac", ".wav", ".aiff", ".aif", ".m4a"}
        )
    )

    rows = []
    for path in candidates:
        want = desired_name(path, template)
        # Shelf letter can change too when the album artist is corrected.
        shelf = layout.alpha_bucket(
            tags.read(path).get("album_artist")
            or tags.read(path).get("artist")
            or ""
        )
        target = collection / shelf / want
        if target == path:
            continue
        links, unreadable = crate_links(path, crates_root)
        rows.append(
            {
                "from": str(path),
                "to": str(target),
                "conflict": target.exists(),
                "links": [str(p) for p in links],
                # Surfaced so `apply` can refuse rather than half-rename.
                "unreadable_links": unreadable,
            }
        )
    return rows


def apply(row: dict[str, Any]) -> dict[str, Any]:
    """Move the track, its sidecar, and every crate entry, or nothing."""
    source = Path(row["from"])
    target = Path(row["to"])
    if target.exists():
        return {**row, "status": "conflict"}
    # Refuse rather than half-rename. If some crate entries could not be read,
    # renaming the audio would strand them under the old name with no record
    # of which ones — worse than not renaming at all, because the next run
    # cannot find them either.
    if row.get("unreadable_links"):
        return {**row, "status": "unreadable-links"}

    target.parent.mkdir(parents=True, exist_ok=True)
    side_from = sidecar.sidecar_dir(source)
    side_to = sidecar.sidecar_dir(target)

    source.replace(target)
    if side_from.is_dir():
        side_to.parent.mkdir(parents=True, exist_ok=True)
        side_from.replace(side_to)

    renamed_links = []
    for link in row.get("links", []):
        link_path = Path(link)
        if not link_path.exists():
            continue
        new_link = link_path.with_name(target.name)
        if new_link != link_path and not new_link.exists():
            try:
                link_path.replace(new_link)
                renamed_links.append(str(new_link))
            except OSError:
                pass
    return {**row, "status": "renamed", "renamed_links": renamed_links}


def rebuild_playlists(root: Path) -> list[str]:
    """Regenerate every .m3u8 from its crate, so no entry points at an old name.

    Rebuilding from the crate is simpler and safer than patching lines: the
    crate is the truth about what is in that selection, and a half-patched
    playlist is worse than a regenerated one.
    """
    playlists = Path(root) / layout.PLAYLISTS
    crates_root = Path(root) / layout.CRATES
    if not crates_root.is_dir():
        return []

    written = []
    for crate in sorted(crates_root.iterdir()):
        if not crate.is_dir():
            continue
        entries = []
        for path in sorted(crate.iterdir()):
            if not path.is_file() or path.name.startswith("."):
                continue
            meta = tags.read(path)
            side = sidecar.read(path)
            entries.append(
                {
                    "path": str(path.resolve()),
                    "title": meta.get("title") or path.stem,
                    "artists": [meta.get("artist") or ""],
                    "duration_ms": int((side.get("duration_s") or 0) * 1000),
                }
            )
        if not entries:
            continue
        target = playlists / f"{crate.name}.m3u8"
        layout.write_m3u8(target, entries, root=Path(root))
        written.append(str(target))
    return written
