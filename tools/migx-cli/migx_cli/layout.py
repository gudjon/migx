"""Filesystem layout — Collection is the one home, Crates are flight cases.

The invariant, and the whole point:

    **Every unique track exists as exactly one audio file.**

`Collection/` holds that file. Everything else — crates, night selections,
playlists — is a *reference* to it: a symlink or an `.m3u8` line, never a copy.
Deleting a crate can never cost you audio.

This is the same rule the repo already runs on doctrinally (MG-3, one canonical
home, cite don't copy) applied to audio, and it composes with the house
in `kanban/knowledge/filesystem-driven-architecture.md`: sidecars beside the
audio are the metadata SSoT, SQLite stays a rebuildable index.

    Music/
      Collection/A/Amelie Lens/128 8A - … Feel It.mp3          <- file
      Crates/Night - 2026-08-15 Club X/128 8A - ….mp3           <- link
      Playlists/Peak.m3u8                                             <- text
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable

COLLECTION = "Collection"
CRATES = "Crates"
PLAYLISTS = "Playlists"
INBOX = "_Inbox"


def alpha_bucket(name: str) -> str:
    """First-letter shelf: '0-9' for digits, 'A'-'Z', '#' for anything else."""
    for char in (name or "").strip():
        if char.isdigit():
            return "0-9"
        if char.isalpha():
            folded = char.upper()
            return folded if "A" <= folded <= "Z" else "#"
    return "#"


def collection_dir(root: Path) -> Path:
    return Path(root).expanduser() / COLLECTION


def crate_dir(root: Path, crate: str) -> Path:
    from . import naming

    return Path(root).expanduser() / CRATES / naming.sanitize(crate)


def playlist_path(root: Path, name: str) -> Path:
    from . import naming

    return (
        Path(root).expanduser() / PLAYLISTS / f"{naming.sanitize(name)}.m3u8"
    )


def collection_path(
    root: Path, entry: dict[str, Any], *, template: str, ext: str
) -> Path:
    """Absolute destination for one track inside the Collection.

    Shelved by the *album artist's* initial so an album stays together
    even when
    individual tracks credit different featured artists.
    """
    from . import naming

    artists = entry.get("artists") or []
    shelf_name = entry.get("album_artist") or (artists[0] if artists else "")
    relative = naming.render(entry, template=template, ext=ext)
    return collection_dir(root) / alpha_bucket(shelf_name) / relative


def link_into_crate(
    target: Path, crate: Path, *, relative: bool = True
) -> Path:
    """Symlink one Collection file into a crate. Never copies.

    Relative by default so the whole `Music/` tree stays movable and rsyncable
    without every link breaking.
    """
    crate.mkdir(parents=True, exist_ok=True)
    # Resolve BOTH sides before computing the relative path. On macOS /tmp and
    # /var are themselves symlinks, so mixing a resolved target with an
    # unresolved crate directory yields a relative path that points nowhere.
    target = Path(target).resolve()
    crate = crate.resolve()
    link = crate / target.name

    if link.is_symlink() or link.exists():
        # Idempotent: re-linking an already-crated track is a no-op, not an
        # error, so `crate.sync` can be re-run safely.
        try:
            if link.resolve() == target:
                return link
        except OSError:
            pass
        link.unlink()

    source = os.path.relpath(target, crate) if relative else str(target)
    link.symlink_to(source)
    return link


def write_m3u8(
    path: Path, tracks: Iterable[dict[str, Any]], *, root: Path | None = None
) -> Path:
    """Write an extended M3U every DJ app can import.

    Paths are relative to the playlist file when a root is given, so the tree
    stays portable.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["#EXTM3U"]
    for track in tracks:
        target = Path(track["path"])
        seconds = int((track.get("duration_ms") or 0) / 1000)
        artist = (track.get("artists") or [""])[0]
        lines.append(f"#EXTINF:{seconds},{artist} - {track.get('title', '')}")
        if root is not None:
            lines.append(os.path.relpath(target, path.parent))
        else:
            lines.append(str(target))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def find_duplicates(root: Path) -> dict[str, list[str]]:
    """Same-size real files sharing a name — the SSoT violation to hunt.

    Symlinks are skipped by design: a crate link is a reference, not a copy.
    """
    from . import tags

    seen: dict[str, list[str]] = {}
    collection = collection_dir(root)
    if not collection.is_dir():
        return {}

    for path in sorted(collection.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        if path.suffix.lower() not in {
            ".mp3",
            ".flac",
            ".wav",
            ".aiff",
            ".aif",
            ".m4a",
        }:
            continue
        meta = tags.read(path)
        key = meta.get("isrc") or f"{meta.get('artist')}|{meta.get('title')}"
        if not key or key == "None|None":
            continue
        seen.setdefault(key, []).append(str(path))

    return {k: v for k, v in seen.items() if len(v) > 1}
