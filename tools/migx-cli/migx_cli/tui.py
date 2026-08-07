"""Interactive dashboard over the same data the commands emit.

Deliberately split in two:

* `snapshot()` is pure — it reads config, mirrors, Collection and gap list and
  returns plain dicts. Testable offline, no terminal involved.
* `run()` is a thin `curses` layer that draws a snapshot.

That split is the point. A TUI whose logic is welded to the screen cannot be
tested, and this one is the *second* client of the command surface (`ADR-008`)
— it must not become a place where behaviour hides. Anything the TUI shows is
something a command already emits.

stdlib `curses`, no Textual: `tools/` has carried zero third-party Python
dependencies and this is not the feature to break that for.

Run: ./tools/migx-cli/migx-tui
"""

from __future__ import annotations

import glob
import json
import os
from pathlib import Path
from typing import Any

from . import config, layout, quality, resolve, sidecar, spark, tags

PANES = ("Overview", "Library", "Arrange", "Prep", "Track")


def _mirrors(mirror_root: Path) -> list[dict[str, Any]]:
    rows = []
    pattern = str(Path(mirror_root).expanduser() / "**" / "*.json")
    for path in sorted(glob.glob(pattern, recursive=True)):
        if "_pull-all" in os.path.basename(path):
            continue
        try:
            doc = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rows.append(
            {
                "name": doc.get("source_name") or Path(path).stem,
                "tracks": doc.get("track_count") or 0,
                "week": doc.get("captured_week") or "",
                "owner": doc.get("owner") or "",
            }
        )
    rows.sort(key=lambda r: -r["tracks"])
    return rows


def _collection(root: Path) -> list[dict[str, Any]]:
    rows = []
    coll = layout.collection_dir(root)
    if not coll.is_dir():
        return rows
    for path in sorted(coll.rglob("*")):
        if path.is_dir() or path.name.startswith("."):
            continue
        # Skip sidecar contents: <track>.mp3.migx/track.json sits under
        # Collection/ and is metadata, not a track.
        if path.suffix.lower() not in resolve.AUDIO_EXTS:
            continue
        meta = tags.read(path)
        probe = quality.inspect(path)
        side = sidecar.read(path)
        rows.append(
            {
                "name": path.name,
                "path": str(path),
                "artist": meta.get("artist") or "",
                "tier": probe.get("tier") or "",
                "bpm": meta.get("bpm") or side.get("bpm"),
                "camelot": meta.get("camelot"),
                "duration_s": probe.get("duration_s"),
                "energy": (side.get("energy_curve") or {}).get("all") or [],
                "notes": side.get("notes") or "",
                "tags": side.get("tags") or [],
                "cues": side.get("cues") or [],
            }
        )
    return rows


def _gaps(root: Path) -> list[dict[str, Any]]:
    """Load a gap list written by library.missing --out (if present)."""
    path = layout.gap_list_path(root)
    if not path.is_file():
        return []
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return doc.get("items", [])


def _status(item: dict[str, Any]) -> str:
    """Current schema says `status`; an older artifact on disk says `want`."""
    raw = item.get("status") or item.get("want") or "missing"
    return "upgrade" if raw == "upgrade" else "missing"


def _item_status(item: dict[str, Any]) -> str:
    return item.get("status") or "missing"


def snapshot() -> dict[str, Any]:
    """Everything the dashboard shows. Pure — safe to call in a test."""
    cfg = config.load()
    root = Path(config.get(cfg, "library.root"))
    mirror_root = Path(config.get(cfg, "spotify.mirror_root"))

    mirrors = _mirrors(mirror_root)
    collection = _collection(root)
    gaps = _gaps(root)
    crates = []
    crate_root = root / layout.CRATES
    if crate_root.is_dir():
        for d in sorted(crate_root.iterdir()):
            if d.is_dir():
                crates.append(
                    {"name": d.name, "tracks": sum(1 for _ in d.iterdir())}
                )

    analysed = sum(1 for c in collection if c["bpm"] and c["camelot"])
    return {
        "library_root": str(root),
        "library_exists": root.is_dir(),
        "mirror_root": str(mirror_root),
        "mirrors": mirrors,
        "mirror_count": len(mirrors),
        "mirror_tracks": sum(m["tracks"] for m in mirrors),
        "collection": collection,
        "collection_count": len(collection),
        "analysed_count": analysed,
        "crates": crates,
        "gaps": gaps,
        "missing_count": sum(1 for g in gaps if _item_status(g) == "missing"),
        "upgrade_count": sum(1 for g in gaps if _item_status(g) == "upgrade"),
        "template": config.get(cfg, "library.template"),
        "tiers": config.get(cfg, "quality.allow_tiers"),
        "linked_ok": config.get(cfg, "spotify.client_id") not in (None, ""),
        "selected": 0,
    }


def track_view(
    track: dict[str, Any] | None, width: int = 72, height: int = 8
) -> list[tuple[str, list[int] | None]]:
    """One song, full screen: waveform, time axis, cues, notes.

    Rows are (text, per-column heat) so the caller can paint the waveform as
    a heatmap and leave the prose alone.
    """
    if not track:
        return [
            ("(no track selected — pick one in Library and press t)", None)
        ]

    out: list[tuple[str, list[int] | None]] = []
    out.append((track["name"], None))
    bpm = f"{round(track['bpm'])}" if track.get("bpm") else "--"
    meta = (
        f"{bpm} BPM   {track.get('camelot') or '--'}   "
        f"{sidecar.fmt_position(track.get('duration_s'))}   "
        f"{track.get('tier') or ''}"
    )
    out.append((meta, None))
    out.append(("", None))

    energy = track.get("energy") or []
    if energy:
        for row, heats in spark.waveform(energy, width, height):
            out.append((row, heats))
        out.append(
            (spark.time_axis(track.get("duration_s") or 0, width), None)
        )
        for line in spark.cue_ruler(
            track.get("cues") or [], track.get("duration_s") or 0, width
        ):
            out.append((line, None))
    else:
        out.append(("(not analysed — run: migx library.analyze)", None))
        for cue in track.get("cues") or []:
            out.append(
                (
                    f"  {sidecar.fmt_position(cue.get('position')):>6}  "
                    f"{cue.get('label') or ''}",
                    None,
                )
            )

    if track.get("notes"):
        out.append(("", None))
        out.append((track["notes"], None))
    if track.get("tags"):
        out.append(("#" + "  #".join(track["tags"]), None))
    return out


def _selected(snap: dict[str, Any]) -> dict[str, Any] | None:
    index = snap.get("selected", 0)
    collection = snap.get("collection") or []
    if not collection:
        return None
    return collection[max(0, min(index, len(collection) - 1))]


def _rows(pane: str, snap: dict[str, Any]) -> list[str]:
    """Render one pane as plain lines — also what the tests assert on."""
    if pane == "Overview":
        return [
            f"library     {snap['library_root']}"
            f"{'' if snap['library_exists'] else '   (NOT MOUNTED)'}",
            f"template    {snap['template']}    "
            f"quality {', '.join(snap['tiers'])}",
            "",
            f"mirrors     {snap['mirror_count']:>6}  playlists"
            f"   ({snap['mirror_tracks']} track entries)",
            f"collection  {snap['collection_count']:>6}  files"
            f"   ({snap['analysed_count']} with BPM+key)",
            f"crates      {len(snap['crates']):>6}",
            f"gaps        {snap['missing_count']:>6}  missing"
            f"   ({snap['upgrade_count']} to upgrade)",
            "",
            f"spotify     {'linked' if snap['linked_ok'] else 'not linked'}",
        ]
    if pane == "Arrange":
        return [
            f"{m['tracks']:>5}  {m['week']:9}  {m['name'][:52]}"
            for m in snap["mirrors"]
        ] or ["(no mirrors — run playlist.pull)"]
    if pane == "Gaps":
        out = []
        for g in snap["gaps"]:
            artist = (g.get("artists") or [""])[0]
            tag = "UPGR" if _item_status(g) == "upgrade" else "MISS"
            out.append(
                f"{tag} {g.get('isrc') or '-':14} {artist[:24]:26}"
                f" {(g.get('title') or '')[:34]}"
            )
        return out or ["(no gaps — run library.missing)"]
    if pane == "Track":
        return [text for text, _ in track_view(_selected(snap), 64, 6)]
    if pane == "_Notes":
        out = []
        for c in snap["collection"]:
            if not (c["notes"] or c["tags"] or c["cues"]):
                continue
            out.append(f"@{c['name'][:60]}")
            if c["energy"]:
                width = 56
                out.append("  " + spark.sparkline(c["energy"], width))
                for line in spark.cue_ruler(
                    c["cues"], c["duration_s"] or 0, width
                ):
                    out.append("  " + line)
            if c["notes"]:
                out.append(f"    {c['notes']}")
            if c["tags"]:
                out.append(f"    #{'  #'.join(c['tags'])}")
            for cue in c["cues"]:
                out.append(
                    f"    {sidecar.fmt_position(cue.get('position')):>6}  "
                    f"{cue.get('label') or cue.get('type') or ''}"
                )
            out.append("")
        return out or [
            "(no notes yet — try: migx track.note <track> --note …)"
        ]

    rows = []
    for c in snap["collection"]:
        secs = int(c["duration_s"] or 0)
        bpm = f"{round(c['bpm']):>3}" if c["bpm"] else "  -"
        key = c["camelot"] or "--"
        mark = "*" if (c["notes"] or c["tags"] or c["cues"]) else " "
        rows.append(
            f"{bpm} {key:3} {secs // 60}:{secs % 60:02d} {mark} "
            f"{c['tier']:12} {c['name'][:44]}"
        )
    return rows or ["(Collection is empty — run library.ingest)"]


# Semantic colour roles, not raw numbers, so the palette is changed in one
# place and a mono terminal simply gets A_NORMAL.
ROLE_HEAD, ROLE_OK, ROLE_WARN, ROLE_DIM, ROLE_CUE, ROLE_TAG = range(1, 7)
# Heat bands for the waveform, cool to hot. Offset so they never collide with
# the semantic roles above.
ROLE_HEAT_BASE = 10


def _init_colours() -> dict[int, int]:
    import curses

    if not curses.has_colors():
        return {}
    curses.start_color()
    curses.use_default_colors()
    pairs = {
        ROLE_HEAD: (curses.COLOR_CYAN, -1),
        ROLE_OK: (curses.COLOR_GREEN, -1),
        ROLE_WARN: (curses.COLOR_YELLOW, -1),
        ROLE_DIM: (curses.COLOR_BLUE, -1),
        ROLE_CUE: (curses.COLOR_MAGENTA, -1),
        ROLE_TAG: (curses.COLOR_YELLOW, -1),
    }
    heat_colours = [
        curses.COLOR_BLUE,
        curses.COLOR_CYAN,
        curses.COLOR_GREEN,
        curses.COLOR_YELLOW,
        curses.COLOR_RED,
    ]
    for band, colour in enumerate(heat_colours[: spark.HEAT_LEVELS]):
        pairs[ROLE_HEAT_BASE + band] = (colour, -1)
    for role, (fg, bg) in pairs.items():
        curses.init_pair(role, fg, bg)
    return {role: curses.color_pair(role) for role in pairs}


def _line_attr(pane: str, line: str, colours: dict[int, int]) -> int:
    """Colour by what the line means, decided from its rendered shape."""
    if not colours:
        return 0
    stripped = line.strip()
    if pane == "Notes":
        if stripped.startswith("@"):
            return colours[ROLE_HEAD]
        if stripped.startswith("#"):
            return colours[ROLE_TAG]
        if stripped[:1].isdigit() and ":" in stripped[:6]:
            return colours[ROLE_CUE]
        return colours[ROLE_DIM]
    if pane == "Gaps":
        return colours[ROLE_WARN] if stripped.startswith("UPGR") else 0
    if pane == "Collection":
        return colours[ROLE_OK] if " * " in line else 0
    if pane == "Overview" and "NOT MOUNTED" in line:
        return colours[ROLE_WARN]
    return 0


def run() -> int:  # pragma: no cover - needs a terminal
    import curses

    def draw(stdscr) -> None:
        curses.curs_set(0)
        colours = _init_colours()
        stdscr.nodelay(False)
        pane, top = 0, 0
        snap = snapshot()

        while True:
            stdscr.erase()
            height, width = stdscr.getmaxyx()
            tabs = "  ".join(
                f"[{i + 1}] {name}" for i, name in enumerate(PANES)
            )
            head_attr = curses.A_BOLD | colours.get(ROLE_HEAD, 0)
            stdscr.addnstr(0, 0, f" migx  {tabs}", width - 1, head_attr)
            stdscr.addnstr(
                1, 0, " " + "-" * max(0, min(width - 2, 78)), width - 1
            )

            rows = _rows(PANES[pane], snap)
            view = height - 4
            top = max(0, min(top, max(0, len(rows) - view)))
            for offset, line in enumerate(rows[top : top + view]):
                stdscr.addnstr(
                    2 + offset,
                    1,
                    line,
                    width - 2,
                    _line_attr(PANES[pane], line, colours),
                )

            footer = (
                f" {PANES[pane]}  {top + 1}-"
                f"{min(len(rows), top + view)} of {len(rows)}"
                "   j/k move  1-5 mode  t track  r refresh  q quit"
            )
            stdscr.addnstr(height - 1, 0, footer, width - 1, curses.A_REVERSE)
            stdscr.refresh()

            key = stdscr.getch()
            if key in (ord("q"), 27):
                return
            if key in (ord("j"), curses.KEY_DOWN):
                if PANES[pane] == "Library":
                    snap["selected"] = min(
                        len(snap["collection"]) - 1,
                        snap.get("selected", 0) + 1,
                    )
                top += 1
            elif key in (ord("k"), curses.KEY_UP):
                if PANES[pane] == "Library":
                    snap["selected"] = max(0, snap.get("selected", 0) - 1)
                top = max(0, top - 1)
            elif key in (ord("t"), ord("\n"), curses.KEY_ENTER):
                pane, top = PANES.index("Track"), 0
            elif key in (curses.KEY_NPAGE, ord(" ")):
                top += view
            elif key == curses.KEY_PPAGE:
                top = max(0, top - view)
            elif key in (ord("g"),):
                top = 0
            elif key in (ord("G"),):
                top = max(0, len(rows) - view)
            elif key == ord("r"):
                snap = snapshot()
            elif key == ord("\t"):
                pane, top = (pane + 1) % len(PANES), 0
            elif ord("1") <= key <= ord("5"):
                pane, top = key - ord("1"), 0

    curses.wrapper(draw)
    return 0
