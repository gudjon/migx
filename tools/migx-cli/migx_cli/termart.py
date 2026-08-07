"""Terminal art — optional PNG/JPEG cover rendering via chafa.

Pure optional dependency: if `chafa` is not on PATH, callers get a text
placeholder. Never required for CLI/TUI correctness (ADR-008 degrade-safe).

Chafa formats:
  * `symbols` + `-c none` — Unicode half-blocks, **no ANSI escapes** (safe for
    stdlib curses `addstr`).
  * `kitty` / `iterm` / `sixels` — real raster; only for raw stdout (not curses).

Install (macOS): `brew install chafa`
Docs: https://hpjansson.org/chafa/
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

# Common cover filenames (folder art next to the audio file).
_COVER_NAMES = (
    "cover.jpg",
    "cover.jpeg",
    "cover.png",
    "cover.webp",
    "folder.jpg",
    "folder.jpeg",
    "folder.png",
    "front.jpg",
    "front.jpeg",
    "front.png",
    "AlbumArt.jpg",
    "AlbumArt.png",
    "AlbumArtSmall.jpg",
)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
_IMAGE_EXTS = IMAGE_EXTS  # alias

# ANSI CSI / OSC sequences (defensive strip if a future flag leaks colour).
_ANSI_RE = re.compile(r"\x1b(?:\[[0-9;?]*[ -/]*[@-~]|].*?(?:\x1b\\|\x07))")


def chafa_bin() -> str | None:
    """Resolved chafa binary, or None if unavailable."""
    explicit = os.environ.get("MIGX_CHAFA_BIN", "").strip()
    if explicit:
        path = Path(explicit).expanduser()
        return str(path) if path.is_file() and os.access(path, os.X_OK) else None
    return shutil.which("chafa")


def available() -> bool:
    return chafa_bin() is not None


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def find_cover(track_path: Path | str) -> Path | None:
    """Locate cover art beside a track, without decoding audio tags.

    Order: explicit sibling names → any image in the track's directory →
    sidecar dir images → library `_Inbox/.thumb` fuzzy stem match.
    """
    track = Path(track_path).expanduser()
    if not track.is_file():
        return None
    parent = track.parent

    for name in _COVER_NAMES:
        candidate = parent / name
        if candidate.is_file():
            return candidate

    # Prefer a single image in the same folder (label packs often drop one PNG).
    images = sorted(
        p
        for p in parent.iterdir()
        if p.is_file() and p.suffix.lower() in _IMAGE_EXTS
    )
    if len(images) == 1:
        return images[0]

    sidecar_dir = Path(str(track) + ".migx")
    if sidecar_dir.is_dir():
        for name in _COVER_NAMES:
            candidate = sidecar_dir / name
            if candidate.is_file():
                return candidate
        side_imgs = sorted(
            p
            for p in sidecar_dir.iterdir()
            if p.is_file() and p.suffix.lower() in _IMAGE_EXTS
        )
        if side_imgs:
            return side_imgs[0]

    # Downloader thumbs: Music/_Inbox/.thumb/<title>.png
    for root in (parent, parent.parent):
        thumb = root / ".thumb"
        if not thumb.is_dir():
            continue
        stem = track.stem.lower()
        # Exact stem first, then containment (thumbs are often longer YT titles).
        for p in sorted(thumb.iterdir()):
            if p.suffix.lower() not in _IMAGE_EXTS:
                continue
            if p.stem.lower() == stem:
                return p
        for p in sorted(thumb.iterdir()):
            if p.suffix.lower() not in _IMAGE_EXTS:
                continue
            name = p.stem.lower()
            if stem in name or name in stem:
                return p
    return None


def render(
    image: Path | str,
    *,
    cols: int = 40,
    rows: int = 12,
    color: bool = False,
    fmt: str = "symbols",
) -> dict[str, Any]:
    """Render an image to terminal text via chafa.

    Returns a small report dict so CLI/TUI share one shape:
      ok, lines, path, engine (chafa|placeholder), reason?
    """
    path = Path(image).expanduser()
    cols = max(8, min(int(cols), 200))
    rows = max(4, min(int(rows), 80))

    if not path.is_file():
        return {
            "ok": False,
            "path": str(path),
            "engine": "placeholder",
            "reason": "file not found",
            "lines": _placeholder(cols, rows, "no image"),
        }

    binary = chafa_bin()
    if not binary:
        return {
            "ok": False,
            "path": str(path),
            "engine": "placeholder",
            "reason": "chafa not installed (brew install chafa)",
            "lines": _placeholder(cols, rows, "install chafa"),
        }

    # symbols + colors none is the curses-safe default.
    colors = "16" if color and fmt == "symbols" else "none"
    if fmt in ("kitty", "iterm", "sixels"):
        # Raster protocols need their own colour path; leave to chafa.
        cmd = [
            binary,
            "-f",
            fmt,
            "-s",
            f"{cols}x{rows}",
            str(path),
        ]
    else:
        cmd = [
            binary,
            "-f",
            "symbols",
            "-c",
            colors,
            "-s",
            f"{cols}x{rows}",
            str(path),
        ]

    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "ok": False,
            "path": str(path),
            "engine": "placeholder",
            "reason": str(exc),
            "lines": _placeholder(cols, rows, "chafa failed"),
        }

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "chafa failed").strip().splitlines()
        reason = err[0] if err else f"chafa exit {proc.returncode}"
        return {
            "ok": False,
            "path": str(path),
            "engine": "placeholder",
            "reason": reason,
            "lines": _placeholder(cols, rows, "chafa error"),
        }

    text = strip_ansi(proc.stdout or "")
    # Drop cursor-hide leftovers and pure blank lines.
    lines = [ln.rstrip() for ln in text.splitlines()]
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    if not any(ln.strip() for ln in lines):
        return {
            "ok": False,
            "path": str(path),
            "engine": "placeholder",
            "reason": "empty chafa output",
            "lines": _placeholder(cols, rows, "empty"),
        }

    return {
        "ok": True,
        "path": str(path),
        "engine": "chafa",
        "format": fmt,
        "colors": colors,
        "cols": cols,
        "rows": rows,
        "lines": lines,
    }


def render_for_track(
    track_path: Path | str,
    *,
    cols: int = 40,
    rows: int = 12,
    color: bool = False,
) -> dict[str, Any]:
    """Find cover for a track path and render it (or placeholder)."""
    cover = find_cover(track_path)
    if cover is None:
        return {
            "ok": False,
            "path": None,
            "track": str(track_path),
            "engine": "placeholder",
            "reason": "no cover found beside track",
            "lines": _placeholder(cols, rows, "no cover"),
        }
    report = render(cover, cols=cols, rows=rows, color=color)
    report["track"] = str(track_path)
    report["cover"] = str(cover)
    return report


def _placeholder(cols: int, rows: int, label: str) -> list[str]:
    """Minimal box so layout stays stable without chafa."""
    w = max(12, min(cols, 48))
    h = max(3, min(rows, 8))
    top = "┌" + "─" * (w - 2) + "┐"
    bot = "└" + "─" * (w - 2) + "┘"
    mid_label = label[: w - 4]
    pad = w - 4 - len(mid_label)
    left = pad // 2
    right = pad - left
    mid = "│ " + (" " * left) + mid_label + (" " * right) + " │"
    empty = "│" + " " * (w - 2) + "│"
    body = [empty] * max(0, h - 3)
    # Put label in the vertical centre of the body.
    if body:
        body[len(body) // 2] = mid
        lines = [top, *body, bot]
    else:
        lines = [top, mid, bot]
    return lines
