"""Interactive dashboard over the same data the commands emit.

Deliberately split in two:

* `snapshot()` is pure — it reads config, mirrors, Collection and want-list and
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

from . import config, layout, quality, tags

PANES = ("Overview", "Playlists", "Want-list", "Collection")


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
        meta = tags.read(path)
        probe = quality.inspect(path)
        rows.append(
            {
                "name": path.name,
                "artist": meta.get("artist") or "",
                "tier": probe.get("tier") or "",
                "bpm": meta.get("bpm"),
                "camelot": meta.get("camelot"),
                "duration_s": probe.get("duration_s"),
            }
        )
    return rows


def _wantlist(root: Path) -> list[dict[str, Any]]:
    path = Path(root) / "_wantlist.json"
    if not path.is_file():
        return []
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return doc.get("items", [])


def snapshot() -> dict[str, Any]:
    """Everything the dashboard shows. Pure — safe to call in a test."""
    cfg = config.load()
    root = Path(config.get(cfg, "library.root"))
    mirror_root = Path(config.get(cfg, "spotify.mirror_root"))

    mirrors = _mirrors(mirror_root)
    collection = _collection(root)
    want = _wantlist(root)
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
        "want": want,
        "want_acquire": sum(1 for w in want if w.get("want") == "acquire"),
        "want_upgrade": sum(1 for w in want if w.get("want") == "upgrade"),
        "template": config.get(cfg, "library.template"),
        "tiers": config.get(cfg, "quality.allow_tiers"),
        "linked_ok": config.get(cfg, "spotify.client_id") not in (None, ""),
    }


def _rows(pane: str, snap: dict[str, Any]) -> list[str]:
    """Render one pane as plain lines — also what the tests assert on."""
    if pane == "Overview":
        gap = snap["want_acquire"]
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
            f"want-list   {gap:>6}  to acquire"
            f"   ({snap['want_upgrade']} to upgrade)",
            "",
            f"spotify     {'linked' if snap['linked_ok'] else 'not linked'}",
        ]
    if pane == "Playlists":
        return [
            f"{m['tracks']:>5}  {m['week']:9}  {m['name'][:52]}"
            for m in snap["mirrors"]
        ] or ["(no mirrors — run playlist.pull)"]
    if pane == "Want-list":
        out = []
        for w in snap["want"]:
            artist = (w.get("artists") or [""])[0]
            tag = "UPGR" if w.get("want") == "upgrade" else "BUY "
            out.append(
                f"{tag} {w.get('isrc') or '-':14} {artist[:24]:26}"
                f" {(w.get('title') or '')[:34]}"
            )
        return out or ["(no want-list — run library.missing)"]
    rows = []
    for c in snap["collection"]:
        secs = int(c["duration_s"] or 0)
        bpm = f"{round(c['bpm']):>3}" if c["bpm"] else "  -"
        key = c["camelot"] or "--"
        rows.append(
            f"{bpm} {key:3} {secs // 60}:{secs % 60:02d}  "
            f"{c['tier']:12} {c['name'][:46]}"
        )
    return rows or ["(Collection is empty — run library.ingest)"]


def run() -> int:  # pragma: no cover - needs a terminal
    import curses

    def draw(stdscr) -> None:
        curses.curs_set(0)
        stdscr.nodelay(False)
        pane, top = 0, 0
        snap = snapshot()

        while True:
            stdscr.erase()
            height, width = stdscr.getmaxyx()
            tabs = "  ".join(
                f"[{i + 1}] {name}" for i, name in enumerate(PANES)
            )
            stdscr.addnstr(0, 0, f" migx  {tabs}", width - 1, curses.A_BOLD)
            stdscr.addnstr(
                1, 0, " " + "-" * max(0, min(width - 2, 78)), width - 1
            )

            rows = _rows(PANES[pane], snap)
            view = height - 4
            top = max(0, min(top, max(0, len(rows) - view)))
            for offset, line in enumerate(rows[top : top + view]):
                stdscr.addnstr(2 + offset, 1, line, width - 2)

            footer = (
                f" {PANES[pane]}  {top + 1}-"
                f"{min(len(rows), top + view)} of {len(rows)}"
                "   j/k scroll  1-4 pane  r refresh  q quit"
            )
            stdscr.addnstr(height - 1, 0, footer, width - 1, curses.A_REVERSE)
            stdscr.refresh()

            key = stdscr.getch()
            if key in (ord("q"), 27):
                return
            if key in (ord("j"), curses.KEY_DOWN):
                top += 1
            elif key in (ord("k"), curses.KEY_UP):
                top = max(0, top - 1)
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
            elif ord("1") <= key <= ord("4"):
                pane, top = key - ord("1"), 0

    curses.wrapper(draw)
    return 0
