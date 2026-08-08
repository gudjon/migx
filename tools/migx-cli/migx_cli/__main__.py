"""migx CLI — the command surface both the TUI and an agent drive.

Every command is one of four kinds (ADR-008 draft):
    command     mutates state; routed through a single writer
    query       pure read, no side effect
    event       engine -> client push (not yet implemented)
    capability  introspection, so an agent can discover the surface

`--json` makes any command emit machine-readable output on stdout. Human text
goes to stderr, so an agent can pipe stdout without filtering prose.

Run:  python3 -m migx_cli <command> [options]
      python3 -m migx_cli system.capabilities --json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import (
    analyze,
    api,
    auth,
    config,
    feedback,
    ingest,
    layout,
    mirror,
    notes,
    naming,
    quality,
    ratelimit,
    rename,
    resolve,
    setplan,
    session,
    setplay,
    sidecar,
    termart,
    tracklist,
    tui,
    watch,
)

REPO = Path(__file__).resolve().parents[3]
DEFAULT_MIRROR_ROOT = (
    REPO / "kanban" / "planning" / "_data" / "spotify-mirrors"
)

CAPABILITIES: list[dict[str, Any]] = [
    {
        "id": "spotify.login",
        "kind": "command",
        "summary": "Link a Spotify account via OAuth 2.0 PKCE"
        " (no client secret).",
        "args": {
            "--client-id": "str, else $MIGX_SPOTIFY_CLIENT_ID",
            "--timeout": "int seconds, default 180",
        },
        "writes": "macOS Keychain (service=migx-spotify)",
    },
    {
        "id": "spotify.status",
        "kind": "query",
        "summary": "Report whether an account is linked, and with"
        " which scopes.",
        "emits": "migx.auth-status/1",
        "note": "OAuth PKCE read-only; hosts accounts.spotify.com + api.spotify.com.",
    },
    {
        "id": "spotify.logout",
        "kind": "command",
        "summary": "Delete the stored refresh token.",
        "writes": "macOS Keychain (service=migx-spotify)",
    },
    {
        "id": "playlist.list",
        "kind": "query",
        "summary": "List playlists reachable by this account, plus"
        " Liked Songs.",
        "emits": "migx.playlist-index/1",
        "note": "Spotify-owned playlists (Discover Weekly, Release"
        " Radar, Daylist) are "
        "NOT reachable via the Web API for apps without a"
        " pre-2024-11-27 quota "
        "extension. Duplicate them inside Spotify, then pull your copy.",
    },
    {
        "id": "playlist.pull",
        "kind": "command",
        "summary": "Snapshot one playlist (or 'liked') to a dated"
        " mirror document.",
        "args": {
            "id": "playlist id/URI/URL, or the literal 'liked'",
            "--out": "output path (default: derived weekly path)",
            "--root": "mirror root directory",
            "--force-full": "re-page even if snapshot_id is unchanged",
            "--min-interval": "seconds between API calls (default 0.3)",
        },
        "emits": "migx.playlist-mirror/1",
        "note": "Official Web API only, read-only scopes, metadata only. "
        "Unchanged playlists skip track pages by default (snapshot_id).",
    },
    {
        "id": "library.inspect",
        "kind": "query",
        "summary": "Classify local audio files against the DJ quality bar.",
        "args": {
            "paths": "one or more files or directories",
            "--allow-tier": "additionally accept a tier (e.g. mp3-vbr-high)",
        },
        "emits": "migx.quality-report/1",
        "note": "The bar is a contract on the FILE, not on where it"
        " came from: "
        "true 320 CBR or lossless passes, everything else is refused.",
    },
    {
        "id": "library.resolve",
        "kind": "command",
        "summary": "Match a mirror against files you already own.",
        "args": {
            "mirror": "path to a migx.playlist-mirror/1 document",
            "--root": "library root to scan (repeatable)",
            "--out": "write the report here",
            "--allow-tier": "accept an extra quality tier",
        },
        "emits": "migx.resolution-report/1",
        "resolvers": resolve.available(),
        "note": "Ships the local-files resolver only. Every hit is gated on"
        " the quality bar, so no resolver self-certifies.",
    },
    {
        "id": "library.missing",
        "kind": "query",
        "summary": "Missing tracks and quality upgrades vs Collection.",
        "args": {
            "mirror": "mirror document, or a resolution report",
            "--root": "library root to scan (repeatable)",
            "--out": "write the gap list here",
        },
        "emits": "migx.gap-list/1",
        "note": "ISRC-keyed. A file below the bar is an upgrade, not a"
        " second missing entry.",
    },
    {
        "id": "library.ingest",
        "kind": "command",
        "summary": "File audio into Collection/ with correct name and tags.",
        "args": {
            "paths": "files or directories to ingest",
            "--library": "the Music/ root (Collection lives under it)",
            "--mirror": "optional mirror to take canonical identity from",
            "--template": "dj | library | flat",
            "--move": "move instead of copy",
            "--dry-run": "report without touching the filesystem",
        },
        "emits": "migx.ingest-report/1",
        "note": "Normalises files you already have; it does not acquire"
        " anything. Every file passes the quality gate first, and an existing"
        " Collection path is never overwritten.",
    },
    {
        "id": "crate.sync",
        "kind": "command",
        "summary": "Build a crate of symlinks from a playlist mirror.",
        "args": {
            "mirror": "a migx.playlist-mirror/1 document",
            "--library": "the Music/ root",
            "--crate": "crate name (defaults to the playlist name)",
            "--m3u8": "also write a playlist file",
        },
        "emits": "migx.crate-report/1",
        "note": "Crates contain links only (hardlink by default) — every"
        " unique track stays"
        " exactly one file in Collection/. Deleting a crate never"
        " costs audio.",
    },
    {
        "id": "library.dedupe",
        "kind": "query",
        "summary": "Find tracks present more than once in Collection/.",
        "args": {"--library": "the Music/ root"},
        "emits": "migx.dedupe-report/1",
    },
    {
        "id": "config.init",
        "kind": "command",
        "summary": "Write a complete config file with every key present.",
        "args": {
            "--library": "library root (Collection/ lives under it)",
            "--client-id": "Spotify client id (public; PKCE uses no secret)",
            "--force": "overwrite an existing config",
        },
        "emits": "migx.config/1",
    },
    {
        "id": "config.show",
        "kind": "query",
        "summary": "Print resolved settings and where each value came from.",
        "emits": "migx.config/1",
        "note": "Precedence is flag > env > file > default, so an explicit"
        " flag can never be silently overridden by a config file.",
    },
    {
        "id": "track.pull",
        "kind": "query",
        "summary": "Resolve Spotify track links into an identity sheet.",
        "args": {
            "links": "track URLs, URIs, ids, or - to read stdin",
            "--out": "write a TSV here (opens in Numbers/Excel)",
        },
        "emits": "migx.track-sheet/1",
        "note": "Mirror-first: reads your local mirrors, so it needs no API"
        " call and works offline. /v1/tracks is 403 for development-mode"
        " apps anyway.",
    },
    {
        "id": "track.note",
        "kind": "command",
        "summary": "Set a DJ note and tags on a track ('girly song').",
        "args": {
            "track": "path, or a fragment matched against the Collection",
            "--note": "free text",
            "--tag": "repeatable short tag",
            "--append": "extend instead of replacing",
        },
        "writes": "<track>.migx/track.json (sidecar is the SSoT)",
    },
    {
        "id": "track.cue",
        "kind": "command",
        "summary": "Bookmark a moment: 'mix out here, 1:30'.",
        "args": {
            "track": "path or Collection fragment",
            "at": "position — 90, 1:30, or 1m30s",
            "label": "the reminder",
            "--color": "hex, for the deck display",
            "--hotcue": "hotcue slot number",
        },
        "writes": "<track>.migx/track.json cues[]",
    },
    {
        "id": "track.show",
        "kind": "query",
        "summary": "Notes, tags and cues for a track.",
        "emits": "migx.track-sidecar/1",
    },
    {
        "id": "library.analyze",
        "kind": "command",
        "summary": "Detect BPM and key, storing them in the sidecar.",
        "args": {
            "paths": "files or directories (default: the Collection)",
            "--force": "re-analyze tracks that already have bpm+key",
            "--bin": "path to migx-analyze",
        },
        "writes": "<track>.migx/track.json (bpm, key, camelot)",
        "note": "Runs the app's own AnalyzerBeats/AnalyzerKey via the"
        " migx-analyze binary — there is no second detector.",
    },
    {
        "id": "library.watch",
        "kind": "command",
        "summary": "Watch _Inbox and file new purchases automatically.",
        "args": {
            "--inbox": "directory to watch (default: <library>/_Inbox)",
            "--interval": "seconds between polls (default 10)",
            "--settle": "seconds a file must be unchanged (default 20)",
            "--once": "single pass, then exit (for launchd/cron)",
            "--copy": "copy instead of moving out of the inbox",
            "--no-analyze": "skip BPM/key detection",
        },
        "emits": "migx.ingest-report/1 per batch",
        "note": "Never touches a file until its size and mtime have been"
        " stable — a download in progress is indistinguishable from a"
        " finished file by name alone.",
    },
    {
        "id": "library.rename",
        "kind": "command",
        "summary": "Re-file tracks under their current name after analysis.",
        "args": {
            "--dry-run": "show what would move",
            "--template": "dj | library | flat",
        },
        "emits": "migx.rename-report/1",
        "note": "Moves the audio, its .migx sidecar, and every crate entry"
        " sharing the inode — a sidecar or crate left behind is worse than"
        " a stale name.",
    },
    {
        "id": "library.art",
        "kind": "query",
        "summary": "Render cover art in the terminal (optional chafa).",
        "args": {
            "track": "path or Collection fragment, or a bare image path",
            "--width": "columns (default 40)",
            "--height": "rows (default 12)",
            "--color": "16-colour symbols (default mono, curses-safe)",
            "--format": "symbols | kitty | iterm | sixels",
        },
        "emits": "migx.term-art/1",
        "note": "Requires chafa on PATH (brew install chafa). Degrades to a"
        " text placeholder when chafa or cover is missing — never a hard fail"
        " for the rest of the CLI. symbols+-c none is safe for curses TUI.",
    },
    {
        "id": "library.covers",
        "kind": "command",
        "summary": "Backfill cover.<ext> for Collection tracks missing folder art.",
        "args": {
            "paths": "files or dirs (default: Collection/)",
            "--thumb": "extra .thumb dir (default: <library>/_Inbox/.thumb)",
            "--no-embedded": "skip ID3 APIC extraction",
            "--dry-run": "report without writing",
        },
        "emits": "migx.cover-report/1",
        "note": "Sources: _Inbox/.thumb fuzzy match, then embedded APIC."
        " Never overwrites an existing cover.* file.",
    },
    {
        "id": "set.plan",
        "kind": "query",
        "summary": "Order Collection tracks into a mixable running set.",
        "args": {
            "--opener": "path or filename to lead with (default: coldest opening)",
            "--limit": "plan only the first N tracks of the pool",
            "--out": "also write the order as an .m3u8 playlist",
        },
        "emits": "migx.set-plan/1",
        "note": "Plans an ORDER only — no deck, no engine, no playback."
        " Scores each pair with the same mixing.plan() the Deck view shows, so"
        " the set never disagrees with what a DJ reads about one transition."
        " Greedy: it can strand awkward tracks late, which is why every row"
        " prints its own pitch and reach instead of hiding them.",
    },
    {
        "id": "set.play",
        "kind": "command",
        "summary": "Render a planned set into one continuous beatmatched mix.",
        "args": {
            "--out": "output audio file (default: <library>/Sets/<date>.mp3)",
            "--limit": "mix only the first N tracks",
            "--seconds": "seconds played per track (default 90)",
            "--crossfade": "blend length in seconds (default 12)",
            "--opener": "path or filename to lead with",
            "--no-play": "render only, do not start playback",
        },
        "emits": "migx.set-mix/1",
        "writes": "an audio file",
        "note": "PREVIEW ONLY — a pre-rendered mix is Automix, an explicit"
        " anti-identity; sets are meant to be performed live. Offline render, NOT the engine — no deck, no RT thread, so"
        " nothing here may be reused on the audio callback path. Pitch numbers"
        " come from mixing.beatmatch(), the same source the Deck view shows."
        " A track that cannot reach the running tempo within ±8% plays native"
        " and gets a short cut instead of a forced blend. Requires ffmpeg"
        " (override with MIGX_FFMPEG_BIN).",
    },
    {
        "id": "track.feedback",
        "kind": "command",
        "summary": "Record what the DJ said about a track, so the next set differs.",
        "args": {
            "track": "path, Collection fragment, or 'now' (session.bind)",
            "--fit": "worked | weak | retire — did it land?",
            "--placement": "opener | peak — where does it belong?",
            "--segment": "shorter | longer",
            "--transition": "1-5, how well the blend INTO this track worked",
            "--note": "free text, kept verbatim for a human",
        },
        "writes": "the track's sidecar (append-only, timestamped); "
        "also mirrors into <library>/_session.jsonl",
        "emits": "migx.feedback/1",
        "note": "Takes STRUCTURED verdicts, never free speech — the agent"
        " interpreting the DJ turns talk into flags, so no language guessing"
        " happens near the library. set.plan / Arrange honour these: retire"
        " excludes; opener/peak move the opening slot; weak/worked and"
        " transition 1..5 nudge next-track rank; segment changes set.play"
        " length.",
    },
    {
        "id": "session.now",
        "kind": "query",
        "summary": "What track is 'now' for coaching (library _live.json).",
        "emits": "migx.live-status/1",
        "note": "Written off-RT by session.bind or TUI. Agents read this before"
        " track.feedback so speech attaches to the right file id.",
    },
    {
        "id": "session.bind",
        "kind": "command",
        "summary": "Point session.now at a track (path, fragment, or Collection).",
        "args": {
            "track": "path or Collection fragment",
            "--deck": "A | B | label",
            "--position": "seconds into the track (optional)",
        },
        "writes": "<library>/_live.json",
        "emits": "migx.live-status/1",
    },
    {
        "id": "session.room",
        "kind": "command",
        "summary": "Session-local crowd/theme/energy (this night only).",
        "args": {
            "--theme": "e.g. melodic, peak, cool-down",
            "--energy": "low | mid | high",
            "--note": "free text room read",
        },
        "writes": "<library>/_live.json room{}",
        "emits": "migx.live-status/1",
    },
    {
        "id": "session.clear",
        "kind": "command",
        "summary": "Clear live binding (end of set / prep).",
        "writes": "removes <library>/_live.json; appends clear to _session.jsonl",
        "note": "Night log is kept so session.show can still reconstruct the set.",
    },
    {
        "id": "session.show",
        "kind": "query",
        "summary": "Reconstruct tonight's plays + feedback from the session log.",
        "args": {
            "--limit": "only the last N events (optional)",
        },
        "emits": "migx.session-log/1",
        "note": "Reads <library>/_session.jsonl (append-only). Bind/room/feedback/"
        "clear all append; agents use this for night harvest / Dream loop.",
    },
    {
        "id": "system.capabilities",
        "kind": "capability",
        "summary": "This manifest.",
        "emits": "migx.capability-manifest/1",
    },
]

AUDIO_EXTS = {
    ".mp3",
    ".flac",
    ".wav",
    ".aif",
    ".aiff",
    ".m4a",
    ".alac",
    ".aac",
    ".ogg",
}


def _out(payload: Any, as_json: bool, human: str | None = None) -> None:
    if as_json:
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    elif human is not None:
        print(human)


def _extract_id(raw: str) -> str:
    """Accept a bare id, spotify:playlist:<id>, or an open.spotify.com URL."""
    raw = raw.strip()
    if raw.startswith("spotify:"):
        return raw.rsplit(":", 1)[-1]
    if "open.spotify.com" in raw:
        tail = raw.split("open.spotify.com/", 1)[1]
        return tail.split("?", 1)[0].rstrip("/").rsplit("/", 1)[-1]
    return raw


# ------------------------------------------------------------------ commands


def cmd_login(args: argparse.Namespace) -> int:
    cid = auth.client_id(args.client_id)
    auth.login(cid, timeout_s=args.timeout, open_browser=not args.no_browser)
    token = auth.access_token(cid)
    me = api.SpotifyRead(token).me()
    _out(
        {
            "logged_in": True,
            "user": me.get("id"),
            "display_name": me.get("display_name"),
            "product": me.get("product"),
        },
        args.json,
        f"Linked Spotify account: {me.get('display_name') or me.get('id')}",
    )
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    st = auth.status()
    st["schema"] = "migx.auth-status/1"
    human = "linked" if st["logged_in"] else "not linked — run `spotify.login`"
    _out(st, args.json, f"Spotify: {human}\nScopes: {', '.join(st['scopes'])}")
    return 0 if st["logged_in"] else 1


def cmd_logout(args: argparse.Namespace) -> int:
    removed = auth.logout()
    _out(
        {"logged_out": removed},
        args.json,
        "Removed stored Spotify token." if removed else "No stored token.",
    )
    return 0


def cmd_playlist_list(args: argparse.Namespace) -> int:
    cfg = config.load()
    interval = config.get(
        cfg, "spotify.min_interval_s", ratelimit.DEFAULT_MIN_INTERVAL_S
    )
    pacer = ratelimit.Pacer(float(interval))
    client = api.SpotifyRead(auth.access_token(), pacer=pacer)
    rows = [
        {
            "id": "liked",
            "name": "Liked Songs",
            "owner": "you",
            "tracks": None,
            "kind": "saved",
        }
    ]
    for pl in client.playlists():
        rows.append(
            {
                "id": pl.get("id"),
                "name": pl.get("name"),
                "owner": (pl.get("owner") or {}).get("display_name"),
                "tracks": (pl.get("tracks") or {}).get("total"),
                "kind": "playlist",
            }
        )
    doc = {
        "schema": "migx.playlist-index/1",
        "count": len(rows),
        "playlists": rows,
    }
    if args.json:
        _out(doc, True)
    else:
        for row in rows:
            total = row["tracks"] if row["tracks"] is not None else "-"
            print(f"{str(row['id']):24} {str(total):>5}  {row['name']}")
        print(
            "\nDiscover Weekly / Release Radar are Spotify-owned and"
            " not reachable via the API.\nDuplicate them into your"
            " own playlist, then pull that.",
            file=sys.stderr,
        )
    return 0


def _unchanged_since(path: Path, snapshot_id: str | None) -> bool:
    """True when an existing mirror already has this exact snapshot."""
    if not snapshot_id or not path.is_file():
        return False
    try:
        prior = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return prior.get("snapshot_id") == snapshot_id


def cmd_playlist_pull(args: argparse.Namespace) -> int:
    cfg = config.load()
    if args.min_interval is None:
        args.min_interval = config.get(
            cfg, "spotify.min_interval_s", ratelimit.DEFAULT_MIN_INTERVAL_S
        )
    if not args.root:
        args.root = config.get(cfg, "spotify.mirror_root")
    # Default is snapshot short-circuit ON (Spotify-recommended). Agents and
    # cron can re-run freely without re-paging unchanged playlists.
    if_changed = not bool(getattr(args, "force_full", False))

    pacer = ratelimit.Pacer(float(args.min_interval))
    client = api.SpotifyRead(auth.access_token(), pacer=pacer)

    if args.id == "liked":
        # Liked Songs has no snapshot_id; always a full pull of /me/tracks.
        doc = mirror.build(
            source_id="liked",
            source_name="Liked Songs",
            owner="me",
            items=client.saved_tracks(),
        )
    else:
        pid = _extract_id(args.id)
        meta = client.playlist(pid)
        snapshot = meta.get("snapshot_id")
        head = mirror.build(
            source_id=pid,
            source_name=meta.get("name") or pid,
            owner=(meta.get("owner") or {}).get("display_name"),
            snapshot_id=snapshot,
            items=[],
        )

        # The cheapest request is the one never made: an unchanged snapshot_id
        # means every track page would be identical. Spotify themselves
        # recommend this. It is worth more for staying inside the rate limit
        # than any amount of backoff.
        root = (
            Path(args.root).expanduser() if args.root else DEFAULT_MIRROR_ROOT
        )
        target = (
            Path(args.out).expanduser()
            if args.out
            else mirror.default_path(root, head)
        )
        if if_changed and _unchanged_since(target, snapshot):
            _out(
                {
                    "schema": "migx.playlist-mirror/1",
                    "path": str(target),
                    "skipped": True,
                    "reason": "snapshot_id unchanged",
                    "requests": client.requests,
                },
                args.json,
                f"unchanged (snapshot {snapshot}) — kept {target}",
            )
            return 0

        doc = mirror.build(
            source_id=pid,
            source_name=meta.get("name") or pid,
            owner=(meta.get("owner") or {}).get("display_name"),
            snapshot_id=snapshot,
            items=client.playlist_items(pid),
        )

    root = Path(args.root).expanduser() if args.root else DEFAULT_MIRROR_ROOT
    path = (
        Path(args.out).expanduser()
        if args.out
        else mirror.default_path(root, doc)
    )
    mirror.write(doc, path)

    result = {
        "schema": doc["schema"],
        "path": str(path),
        "track_count": doc["track_count"],
        "skipped": doc["skipped_count"],
        "captured_week": doc["captured_week"],
        "requests": client.requests,
        "throttled": client.pacer.throttled,
        "paced_seconds": round(client.pacer.waited_s, 2),
    }
    _out(
        result,
        args.json,
        f"Mirrored {doc['track_count']} tracks "
        f"({doc['skipped_count']} skipped) -> {path}",
    )

    if args.preview and not args.json:
        print("\nNaming preview:", file=sys.stderr)
        for entry in doc["tracks"][:5]:
            print(f"  {naming.render(entry)}", file=sys.stderr)
    return 0


def cmd_library_inspect(args: argparse.Namespace) -> int:
    targets: list[Path] = []
    for raw in args.paths:
        p = Path(raw).expanduser()
        if p.is_dir():
            targets += sorted(
                f for f in p.rglob("*") if f.suffix.lower() in AUDIO_EXTS
            )
        else:
            targets.append(p)

    allow = tuple(quality.DEFAULT_ELIGIBLE) + tuple(args.allow_tier or ())
    rows = [
        quality.verdict(quality.inspect(t), allow_tiers=allow) for t in targets
    ]
    passed = sum(1 for r in rows if r["eligible"])

    doc = {
        "schema": "migx.quality-report/1",
        "allowed_tiers": list(allow),
        "checked": len(rows),
        "passed": passed,
        "refused": len(rows) - passed,
        "files": rows,
    }
    if args.json:
        _out(doc, True)
    else:
        for r in rows:
            mark = "pass  " if r["eligible"] else "REFUSE"
            rate = r.get("bitrate_kbps")
            print(
                f"{mark} {r['tier']:14} {str(rate or '-'):>5} "
                f"{Path(r['path']).name}  ({r.get('reason', '')})"
            )
        print(
            f"\n{passed}/{len(rows)} eligible for library.index",
            file=sys.stderr,
        )
    return 0 if passed == len(rows) else 1


def _config_roots(cfg: dict[str, Any]) -> list[str]:
    """Collection first, then any extra roots the config declares."""
    root = config.get(cfg, "library.root")
    roots = [str(layout.collection_dir(Path(root)))] if root else []
    roots += [
        str(Path(r).expanduser())
        for r in config.get(cfg, "library.extra_roots", []) or []
    ]
    return roots or [str(Path.home() / "Music")]


def _load_mirror(path: str) -> dict[str, Any]:
    doc = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    schema = doc.get("schema", "")
    if not schema.startswith(
        ("migx.playlist-mirror/", "migx.resolution-report/")
    ):
        raise api.ApiError(
            f"{path}: expected migx.playlist-mirror/1, got {schema or '?'}"
        )
    return doc


def _run_resolve(args: argparse.Namespace) -> dict[str, Any]:
    doc = _load_mirror(args.mirror)
    if doc["schema"].startswith("migx.resolution-report/"):
        return doc  # already resolved; reuse rather than rescan
    cfg = config.load()
    roots = args.root or _config_roots(cfg)
    resolver = resolve.get_resolver(
        getattr(args, "resolver", None) or "local-files", roots
    )
    resolver.scan()
    allow = tuple(quality.DEFAULT_ELIGIBLE) + tuple(args.allow_tier or ())
    return resolve.resolve_mirror(doc, resolver, allow_tiers=allow)


def cmd_library_resolve(args: argparse.Namespace) -> int:
    report = _run_resolve(args)
    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.json:
        _out(report, True)
    else:
        print(f"scanned {report['scanned_files']} local files")
        print(f"resolved   {report['resolved_count']}/{report['total']}")
        print(f"below bar  {report['below_bar_count']}")
        print(f"missing    {report['missing_count']}")
        for row in report["resolved"][:10]:
            print(f"  ok  [{row['method']}] {row['title']}")
        if args.out:
            print(f"\nreport -> {args.out}", file=sys.stderr)
    return 0


def cmd_library_missing(args: argparse.Namespace) -> int:
    if args.all:
        cfg = config.load()
        root = Path(config.get(cfg, "spotify.mirror_root")).expanduser()
        mirrors = sorted(
            f
            for f in root.rglob("*.json")
            if not f.name.startswith("_pull-all")
        )
        # Scan the Collection once, not once per mirror — 83 rescans of the
        # same tree is the difference between seconds and minutes.
        resolver = resolve.get_resolver(
            args.resolver or "local-files", _config_roots(cfg)
        )
        resolver.scan()
        allow = tuple(quality.DEFAULT_ELIGIBLE) + tuple(args.allow_tier or ())
        per = []
        for path in mirrors:
            doc = json.loads(path.read_text(encoding="utf-8"))
            per.append(
                resolve.gap_list(
                    resolve.resolve_mirror(doc, resolver, allow_tiers=allow)
                )
            )
        gaps = resolve.merge_gap_lists(per)
        gaps["mirrors"] = len(per)
        gaps["scanned_files"] = resolver.scanned
        # Land in the one place the TUI and everything else look.
        if not args.out:
            args.out = str(
                layout.gap_list_path(Path(config.get(cfg, "library.root")))
            )
    else:
        gaps = resolve.gap_list(_run_resolve(args))
    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(gaps, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.json:
        _out(gaps, True)
    else:
        print(
            f"missing {gaps['missing_count']} · "
            f"upgrade {gaps['upgrade_count']}"
        )
        if args.all:
            print(
                f"across {gaps.get('mirrors')} mirrors · "
                f"{gaps.get('scanned_files')} local files scanned"
            )
        shown = gaps["items"] if not args.all else gaps["items"][:25]
        for item in shown:
            tag = "UPGR" if item.get("status") == "upgrade" else "MISS"
            isrc = item.get("isrc") or "-"
            rank = f"x{item['on_playlists']:<2}" if args.all else "   "
            print(f"{tag} {rank} {isrc:14} {item.get('label') or ''}")
        if args.all and len(gaps["items"]) > len(shown):
            print(
                f"... {len(gaps['items']) - len(shown)} more "
                f"(--json or --out for all)",
                file=sys.stderr,
            )
    return 0


def cmd_library_ingest(args: argparse.Namespace) -> int:
    cfg = config.load()
    args.library = config.resolve(args.library, cfg, "library.root")
    if args.template is None:
        args.template = config.get(cfg, "library.template", "dj")
    sources: list[Path] = []
    for raw in args.paths:
        p = Path(raw).expanduser()
        if p.is_dir():
            sources += sorted(
                f
                for f in p.rglob("*")
                if f.suffix.lower() in AUDIO_EXTS and not f.is_symlink()
            )
        else:
            sources.append(p)

    doc = _load_mirror(args.mirror) if args.mirror else None
    allow = tuple(quality.DEFAULT_ELIGIBLE) + tuple(args.allow_tier or ())
    report = ingest.ingest(
        sources,
        Path(args.library).expanduser(),
        mirror=doc,
        template=args.template,
        move=args.move,
        dry_run=args.dry_run,
        allow_tiers=allow,
    )

    if args.json:
        _out(report, True)
    else:
        verb = "would file" if args.dry_run else "filed"
        print(
            f"{verb} {report['filed_count']} · "
            f"refused {report['refused_count']} · "
            f"already present {report['duplicate_count']}"
        )
        for row in report["filed"]:
            rel = Path(row["destination"]).relative_to(report["collection"])
            print(f"  + [{row['matched']}] {rel}")
        for row in report["refused"]:
            print(
                f"  ! {row['tier']:14} {Path(row['source']).name}"
                f"  ({row.get('reason', '')})"
            )
    return 0 if report["refused_count"] == 0 else 1


def cmd_crate_sync(args: argparse.Namespace) -> int:
    args.library = config.resolve(args.library, config.load(), "library.root")
    root = Path(args.library).expanduser()
    # A crate is built out of the Collection, so that is what we scan unless
    # the caller points somewhere else explicitly.
    if not args.root:
        args.root = [str(layout.collection_dir(root))]
    report = _run_resolve(args)
    cfg_crate = config.load()
    crate_name = args.crate or report.get("source_name") or "crate"
    crate = layout.crate_dir(root, crate_name)

    linked = []
    for row in report["resolved"]:
        link = layout.link_into_crate(
            Path(row["path"]),
            crate,
            mode=config.get(
                cfg_crate, "library.crate_link_mode", layout.HARDLINK
            ),
        )
        linked.append({**row, "link": str(link)})

    playlist = None
    if args.m3u8:
        playlist = str(
            layout.write_m3u8(
                layout.playlist_path(root, crate_name),
                report["resolved"],
                root=root,
            )
        )

    doc = {
        "schema": "migx.crate-report/1",
        "crate": str(crate),
        "crate_name": crate_name,
        "playlist": playlist,
        "linked_count": len(linked),
        "missing_count": report["missing_count"],
        "below_bar_count": report["below_bar_count"],
        "linked": linked,
        "missing": report["missing"],
    }
    if args.json:
        _out(doc, True)
    else:
        print(
            f"crate {crate_name}: {len(linked)} linked, "
            f"{report['missing_count']} missing, "
            f"{report['below_bar_count']} below bar"
        )
        print(f"  {crate}")
        if playlist:
            print(f"  {playlist}")
        print(
            "\nLinks only — the audio stays one file in Collection/.",
            file=sys.stderr,
        )
    return 0


def cmd_library_dedupe(args: argparse.Namespace) -> int:
    args.library = config.resolve(args.library, config.load(), "library.root")
    dupes = layout.find_duplicates(Path(args.library).expanduser())
    doc = {
        "schema": "migx.dedupe-report/1",
        "groups": len(dupes),
        "duplicates": dupes,
    }
    if args.json:
        _out(doc, True)
    else:
        if not dupes:
            print("no duplicates — every track is exactly one file")
        for key, paths in dupes.items():
            print(f"{key}")
            for p in paths:
                print(f"  {p}")
    return 0 if not dupes else 1


def cmd_config_init(args: argparse.Namespace) -> int:
    target = config.path()
    if target.exists() and not args.force:
        print(
            f"error: {target} exists — pass --force to overwrite",
            file=sys.stderr,
        )
        return 2

    doc = config.scaffold(
        library_root=args.library,
        client_id=args.client_id
        or os.environ.get("MIGX_SPOTIFY_CLIENT_ID", ""),
    )
    written = config.save(doc, target)
    if args.json:
        _out({"path": str(written), **doc}, True)
    else:
        print(f"wrote {written}")
        print(f"  library root : {doc['library']['root']}")
        print(f"  template     : {doc['library']['template']}")
        print(f"  quality bar  : {', '.join(doc['quality']['allow_tiers'])}")
    return 0


def cmd_config_show(args: argparse.Namespace) -> int:
    target = config.path()
    doc = config.load(target)
    origins = config.sources(target)

    if args.json:
        _out(
            {
                "path": str(target),
                "exists": target.is_file(),
                "sources": origins,
                **doc,
            },
            True,
        )
    else:
        print(
            f"config: {target}"
            f"{'' if target.is_file() else '  (not created yet)'}"
        )
        for dotted in sorted(origins):
            value = config.get(doc, dotted) or "(unset)"
            print(f"  {dotted:22} {str(value):46} [{origins[dotted]}]")
        print(f"  library.template       {doc['library']['template']}")
        print(
            f"  quality.allow_tiers    "
            f"{', '.join(doc['quality']['allow_tiers'])}"
        )
    return 0


def cmd_track_pull(args: argparse.Namespace) -> int:
    cfg = config.load()
    raw = args.links
    if raw == ["-"] or not raw:
        raw = sys.stdin.read().split()
    ids = tracklist.extract_ids(raw)
    if not ids:
        print("error: no Spotify track ids found in input", file=sys.stderr)
        return 2

    roots = _config_roots(cfg)
    resolver = resolve.get_resolver("local-files", roots)
    resolver.scan()
    sheet = tracklist.build(
        ids, Path(config.get(cfg, "spotify.mirror_root")), resolver
    )

    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(tracklist.to_tsv(sheet), encoding="utf-8")

    if args.json:
        _out(sheet, True)
    else:
        print(
            f"{sheet['resolved']}/{sheet['requested']} resolved from "
            f"mirrors · {sheet['owned']} already owned"
        )
        for r in sheet["tracks"]:
            ms = r.get("duration_ms") or 0
            mark = "OWNED" if r["owned"] else f"x{len(r['on_playlists'])}"
            print(
                f"  {mark:>6} {r.get('isrc') or '-':14} "
                f"{(r['artists'] or [''])[0][:20]:22} "
                f"{(r.get('title') or '')[:34]:36} "
                f"{ms // 60000}:{(ms // 1000) % 60:02d}"
            )
        for sid in sheet["unresolved"]:
            print(
                f"  {'?':>6} not on any mirrored playlist: {sid}",
                file=sys.stderr,
            )
        if args.out:
            print(f"\nsheet -> {args.out}", file=sys.stderr)
    return 0


def _find_track(fragment: str) -> Path | None:
    """A path, or the single Collection file whose name contains fragment."""
    direct = Path(fragment).expanduser()
    if direct.is_file():
        return direct
    root = Path(config.get(config.load(), "library.root"))
    needle = fragment.lower()
    hits = [
        p
        for p in layout.collection_dir(root).rglob("*")
        if p.is_file()
        and not p.name.startswith(".")
        and needle in p.name.lower()
    ]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        print(f"error: no track matching {fragment!r}", file=sys.stderr)
    else:
        print(
            f"error: {fragment!r} matches {len(hits)} tracks:", file=sys.stderr
        )
        for h in hits[:8]:
            print(f"  {h.name}", file=sys.stderr)
    return None


def cmd_track_note(args: argparse.Namespace) -> int:
    track = _find_track(args.track)
    if track is None:
        return 2
    data = sidecar.set_note(
        track, note=args.note, tags=args.tag or None, append=args.append
    )
    _out(
        {"schema": "migx.track-sidecar/1", "track": str(track), **data},
        args.json,
        f"{track.name}\n  notes: {data.get('notes') or '—'}\n"
        f"  tags : {', '.join(data.get('tags') or []) or '—'}",
    )
    return 0


def cmd_track_cue(args: argparse.Namespace) -> int:
    track = _find_track(args.track)
    if track is None:
        return 2
    try:
        position = sidecar.parse_position(args.at)
    except ValueError:
        print(
            f"error: cannot read position {args.at!r} — try 90, 1:30, 1m30s",
            file=sys.stderr,
        )
        return 2
    data = sidecar.add_cue(
        track, position, args.label, color=args.color, hotcue=args.hotcue
    )
    _out(
        {"schema": "migx.track-sidecar/1", "track": str(track), **data},
        args.json,
        f"{track.name}\n  + {sidecar.fmt_position(position)}  {args.label}",
    )
    return 0


def cmd_track_show(args: argparse.Namespace) -> int:
    track = _find_track(args.track)
    if track is None:
        return 2
    data = sidecar.read(track)
    if args.json:
        _out(
            {"schema": "migx.track-sidecar/1", "track": str(track), **data},
            True,
        )
        return 0
    print(track.name)
    print(f"  notes: {data.get('notes') or '—'}")
    # notes.md — the prose half of the sidecar. Shown after the typed fields
    # because it is what a DJ actually reads before deciding to play a track.
    note = notes.read(track)
    if note["meta"]:
        for key, value in note["meta"].items():
            shown = ", ".join(value) if isinstance(value, list) else value
            print(f"  {key}: {shown}")
    if note["body"]:
        print()
        for line in note["body"].splitlines():
            print(f"  {line}")
        print()
    print(f"  tags : {', '.join(data.get('tags') or []) or '—'}")
    cues = data.get("cues") or []
    if not cues:
        print("  cues : —")
    for index, cue in enumerate(cues):
        print(
            f"  [{index}] {sidecar.fmt_position(cue.get('position')):>6}  "
            f"{cue.get('label') or cue.get('type') or ''}"
        )
    return 0


def cmd_set_plan(args: argparse.Namespace) -> int:
    """Order the Collection into a set every transition can survive."""
    cfg = config.load()
    lib_root = Path(config.get(cfg, "library.root"))

    # Reuses the TUI's loader so a set is planned from exactly the rows the
    # Library pane shows — two readers of Collection would drift.
    pool = tui._collection(lib_root)
    if args.limit:
        pool = pool[: args.limit]

    plan = setplan.plan_set(pool, library_root=lib_root, opener=args.opener)
    rows = plan["tracks"]

    written = None
    if args.out and rows:
        entries = [
            {
                "path": r["path"],
                "title": Path(r["path"]).stem,
                "artists": [""],
                "duration_ms": int((r.get("duration_s") or 0) * 1000),
            }
            for r in rows
        ]
        written = layout.write_m3u8(
            Path(args.out).expanduser(), entries, root=lib_root
        )
        plan["playlist"] = str(written)

    if not rows:
        _out(plan, args.json, plan.get("note", "nothing to plan"))
        return 1

    lines = [
        f"{len(rows)} tracks  {int(plan['duration_s'] // 60)}m"
        f"{int(plan['duration_s'] % 60):02d}s   "
        f"{plan['in_easy_range']}/{plan['transitions']} transitions within ±8%",
        "",
        f"{'#':>2}  {'BPM':>4} {'KEY':>4}  {'TRACK':<40} {'MOVE':<14} "
        f"{'PITCH':>7}  REACH",
        "-" * 92,
    ]
    for row in rows:
        name = (row["name"] or "")[:39]
        bpm = f"{row['bpm']:.0f}" if row.get("bpm") else "?"
        head = f"{row['position']:>2}  {bpm:>4} {row['camelot'] or '?':>4}  {name:<40} "
        move = row["transition"]
        if move is None:
            lines.append(head + "(open cold)")
            continue
        pitch = (
            f"{move['pitch_pct']:>+6.1f}%"
            if move.get("pitch_pct") is not None
            else "     ?"
        )
        lines.append(
            head
            + f"{move['technique']:<14} {pitch}  "
            + (move.get("fits_range") or "OUT OF RANGE")
        )
    if plan["unplannable"]:
        lines.append("")
        lines.append(
            f"{len(plan['unplannable'])} track(s) skipped — no bpm/key yet; "
            "run `library.analyze`"
        )
    if written:
        lines.append("")
        lines.append(f"playlist: {written}")

    _out(plan, args.json, "\n".join(lines))
    return 0


def cmd_set_play(args: argparse.Namespace) -> int:
    """Perform a planned set: render it as one beatmatched mix, then play it."""
    cfg = config.load()
    lib_root = Path(config.get(cfg, "library.root"))

    pool = tui._collection(lib_root)
    plan = setplan.plan_set(pool, library_root=lib_root, opener=args.opener)
    rows = plan["tracks"]
    if not rows:
        _out(plan, args.json, plan.get("note", "nothing to play"))
        return 1
    if args.limit:
        rows = rows[: args.limit]

    segments = setplay.build_segments(
        rows, seconds=args.seconds, crossfade=args.crossfade
    )
    out = (
        Path(args.out).expanduser()
        if args.out
        else lib_root / "Sets" / "migx-set.mp3"
    )

    result = setplay.render(segments, out)
    payload = {
        "schema": "migx.set-mix/1",
        "tracks": len(segments),
        "expected_duration_s": setplay.expected_duration(segments),
        "beatmatched": sum(1 for s in segments if s["beatmatched"]),
        "segments": segments,
        **({"path": result["path"]} if result.get("ok") else {}),
        **({"error": result["error"]} if not result.get("ok") else {}),
    }
    if not result.get("ok"):
        _out(payload, args.json, f"render failed: {result['error']}")
        return 1

    lines = [
        f"mixed {len(segments)} tracks -> {out}",
        f"  {setplay.expected_duration(segments) / 60:.1f} min, "
        f"{payload['beatmatched']}/{max(0, len(segments) - 1)} beatmatched",
        "",
    ]
    for seg in segments:
        move = (
            f"pitched {(seg['tempo_ratio'] - 1) * 100:+.1f}% -> "
            f"{seg['played_bpm']:.0f} BPM"
            if seg["beatmatched"]
            else ("opens" if seg["position"] == 1 else "cut (out of range)")
        )
        lines.append(
            f"  {seg['position']:>2}  {seg['bpm']:>3.0f} {seg['camelot'] or '?':>4}"
            f"  {(seg['name'] or '')[:44]:<44} {move}"
        )
    _out(payload, args.json, "\n".join(lines))

    if not args.no_play:
        # afplay is macOS-native and needs no extra dependency. Backgrounded so
        # the CLI does not block for the length of the mix.
        subprocess.Popen(
            ["afplay", str(out)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"\nplaying — `killall afplay` to stop", file=sys.stderr)
    return 0


def _resolve_feedback_track(raw: str) -> Path | None:
    """Path, Collection fragment, or the live-bound 'now' track."""
    if raw.strip().lower() in ("now", ".", "live"):
        cfg = config.load()
        root = Path(config.get(cfg, "library.root"))
        track = session.resolve_now_track(root)
        if track is None:
            print(
                "error: nothing bound — run session.bind <track> first",
                file=sys.stderr,
            )
        return track
    return _find_track(raw)


def cmd_track_feedback(args: argparse.Namespace) -> int:
    """Persist one structured verdict against a track."""
    track = _resolve_feedback_track(args.track)
    if track is None:
        return 2
    try:
        doc = feedback.record(
            track,
            fit=args.fit,
            placement=args.placement,
            note=args.note,
            segment=args.segment,
            transition=args.transition,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    # Mirror into the night log so session.show reconstructs floor judgment
    # in order. Lifetime sidecar is still the SSoT for set.plan priors.
    try:
        cfg = config.load()
        root = Path(config.get(cfg, "library.root"))
        session.log_feedback(
            root,
            track,
            fit=args.fit,
            placement=args.placement,
            segment=args.segment,
            transition=args.transition,
            note=args.note,
        )
    except (OSError, ValueError, TypeError, KeyError):
        pass

    current = feedback.latest(doc)
    payload = {
        "schema": "migx.feedback/1",
        "track": str(track),
        "entries": len(doc.get("feedback") or []),
        "in_force": current,
    }
    said = ", ".join(f"{k}={v}" for k, v in current.items())
    effect = (
        "excluded from future sets"
        if current.get("fit") == "retire"
        else "will bias the next set.plan"
    )
    _out(payload, args.json, f"recorded on {track.name}: {said}\n  -> {effect}")
    return 0


def cmd_session_now(args: argparse.Namespace) -> int:
    cfg = config.load()
    root = Path(config.get(cfg, "library.root"))
    doc = session.read(root)
    bound = session.resolve_now_track(root)
    if doc.get("path") and bound is None:
        doc["stale"] = True
        doc["stale_reason"] = "bound path no longer exists"
    human = (
        f"now: {doc.get('title') or '—'}  "
        f"[{doc.get('deck') or '-'}]  "
        f"{doc.get('path') or '(unbound)'}"
    )
    if doc.get("room"):
        room = doc["room"]
        bits = [f"{k}={v}" for k, v in room.items() if v]
        if bits:
            human += f"\nroom: {', '.join(bits)}"
    _out(doc, args.json, human)
    return 0 if doc.get("path") else 1


def cmd_session_bind(args: argparse.Namespace) -> int:
    cfg = config.load()
    root = Path(config.get(cfg, "library.root"))
    track = _find_track(args.track)
    if track is None:
        return 2
    try:
        doc = session.bind(
            root,
            track,
            deck=args.deck,
            position_s=args.position,
            source="cli",
        )
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    _out(
        doc,
        args.json,
        f"bound now -> {track.name}"
        + (f"  deck {args.deck}" if args.deck else ""),
    )
    return 0


def cmd_session_room(args: argparse.Namespace) -> int:
    if not any((args.theme, args.energy, args.note)):
        print(
            "error: pass --theme, --energy, and/or --note",
            file=sys.stderr,
        )
        return 2
    cfg = config.load()
    root = Path(config.get(cfg, "library.root"))
    doc = session.set_room(
        root, theme=args.theme, energy=args.energy, note=args.note
    )
    room = doc.get("room") or {}
    human = "room: " + (
        ", ".join(f"{k}={v}" for k, v in room.items() if v) or "—"
    )
    _out(doc, args.json, human)
    return 0


def cmd_session_clear(args: argparse.Namespace) -> int:
    cfg = config.load()
    root = Path(config.get(cfg, "library.root"))
    session.clear(root)
    _out(
        {"schema": "migx.live-status/1", "path": None, "cleared": True},
        args.json,
        "live binding cleared",
    )
    return 0


def cmd_session_show(args: argparse.Namespace) -> int:
    """Reconstruct tonight's plays + feedback from the append-only log."""
    cfg = config.load()
    root = Path(config.get(cfg, "library.root"))
    limit = args.limit if getattr(args, "limit", None) else None
    doc = session.reconstruct(root, limit=limit)
    human = session.format_show(doc)
    _out(doc, args.json, human)
    return 0 if doc.get("event_count") else 1


def cmd_library_covers(args: argparse.Namespace) -> int:
    """Backfill cover art for tracks already in Collection."""
    cfg = config.load()
    lib_root = Path(config.get(cfg, "library.root"))
    roots = args.paths or [str(layout.collection_dir(lib_root))]
    tracks: list[Path] = []
    for raw in roots:
        p = Path(raw).expanduser()
        if p.is_dir():
            tracks += sorted(
                f
                for f in p.rglob("*")
                if f.is_file()
                and f.suffix.lower() in AUDIO_EXTS
                and not f.is_symlink()
            )
        elif p.is_file():
            tracks.append(p)

    thumb_dirs: list[Path] = []
    if args.thumb:
        thumb_dirs.append(Path(args.thumb).expanduser())
    else:
        default_thumb = lib_root / layout.INBOX / ".thumb"
        if default_thumb.is_dir():
            thumb_dirs.append(default_thumb)

    report = termart.attach_covers(
        tracks,
        thumb_dirs=thumb_dirs,
        extract_embedded=not args.no_embedded,
        dry_run=args.dry_run,
    )
    if args.json:
        _out(report, True)
    else:
        print(
            f"attached {report['attached_count']} · "
            f"skipped {report['skipped_count']} · "
            f"missing {report['missing_count']}"
            f"{'  (dry-run)' if report['dry_run'] else ''}"
        )
        for row in report["attached"][:20]:
            method = row.get("method") or "?"
            print(
                f"  + [{method}] {Path(row['track']).name} -> "
                f"{Path(row.get('cover') or '').name}"
            )
        if report["attached_count"] > 20:
            print(f"  … {report['attached_count'] - 20} more")
    return 0


def cmd_library_art(args: argparse.Namespace) -> int:
    """Render cover art for a track or a bare image path."""
    target = Path(args.track).expanduser()
    if target.is_file() and target.suffix.lower() in termart.IMAGE_EXTS:
        report = termart.render(
            target,
            cols=args.width,
            rows=args.height,
            color=args.color,
            fmt=args.format,
        )
        report["track"] = None
        report["cover"] = str(target)
    else:
        track = _find_track(args.track)
        if track is None:
            return 2
        report = termart.render_for_track(
            track,
            cols=args.width,
            rows=args.height,
            color=args.color,
        )
        if args.format != "symbols" and report.get("cover"):
            report = termart.render(
                report["cover"],
                cols=args.width,
                rows=args.height,
                color=args.color,
                fmt=args.format,
            )
            report["track"] = str(track)

    payload = {"schema": "migx.term-art/1", "chafa": termart.available(), **report}
    if args.json:
        # Machine clients get lines as a list; no raw raster dumps in JSON.
        if report.get("format") in ("kitty", "iterm", "sixels"):
            payload = {
                **payload,
                "lines": [],
                "note": "raster format not included in --json; use human mode",
            }
        _out(payload, True)
        return 0 if report.get("ok") or report.get("engine") == "placeholder" else 1

    if report.get("reason") and not report.get("ok"):
        print(f"# {report['reason']}", file=sys.stderr)
    if report.get("cover"):
        print(f"# cover: {report['cover']}", file=sys.stderr)
    # Raster protocols must go straight to the TTY without stripping.
    if args.format in ("kitty", "iterm", "sixels") and report.get("ok"):
        # Re-run without capture for true inline graphics.
        binary = termart.chafa_bin()
        if binary and report.get("cover"):
            subprocess.run(
                [
                    binary,
                    "-f",
                    args.format,
                    "-s",
                    f"{args.width}x{args.height}",
                    report["cover"],
                ],
                check=False,
            )
            return 0
    for line in report.get("lines") or []:
        print(line)
    return 0


def cmd_library_analyze(args: argparse.Namespace) -> int:
    cfg = config.load()
    roots = args.paths or [
        str(layout.collection_dir(Path(config.get(cfg, "library.root"))))
    ]
    targets: list[Path] = []
    for raw in roots:
        p = Path(raw).expanduser()
        if p.is_dir():
            targets += sorted(
                f
                for f in p.rglob("*")
                if f.suffix.lower() in AUDIO_EXTS and not f.is_symlink()
            )
        elif p.is_file():
            targets.append(p)

    if not args.force:
        todo = []
        for t in targets:
            side = sidecar.read(t)
            if not (side.get("bpm") and side.get("camelot")):
                todo.append(t)
        skipped = len(targets) - len(todo)
        targets = todo
    else:
        skipped = 0

    bin_path = analyze.binary(args.bin)
    if not bin_path.is_file():
        print(
            f"error: migx-analyze not built at {bin_path}\n"
            f"  build it with: ninja -C build migx-analyze",
            file=sys.stderr,
        )
        return 2
    if not targets:
        print(f"nothing to analyze ({skipped} already analysed)")
        return 0

    print(
        f"analyzing {len(targets)} track(s)"
        f"{f' ({skipped} already done)' if skipped else ''}...",
        flush=True,
    )
    # Persist each track the moment the analyzer emits it. Buffering the whole
    # batch meant a long run showed no progress and, if it died on the last
    # track, threw away every result before it.
    stored = []
    failed = 0

    def _persist(result: dict[str, Any]) -> None:
        nonlocal failed
        if result.get("error"):
            failed += 1
            print(
                f"  ! {Path(result['path']).name}: {result['error']}",
                file=sys.stderr,
            )
            return
        stored.append({**result, **analyze.store(result)})
        if not args.json:
            done = len(stored) + failed
            print(
                f"  [{done}/{len(targets)}] {Path(result['path']).name[:52]}",
                flush=True,
            )

    analyze.run(targets, bin_path, on_result=_persist)

    doc = {
        "schema": "migx.analysis-report/1",
        "analyzed": len(stored),
        "skipped": skipped,
        "failed": failed,
        "tracks": stored,
    }
    if args.json:
        _out(doc, True)
    else:
        for s in stored:
            print(
                f"  {round(s.get('bpm') or 0):>3} "
                f"{s.get('camelot') or '--':3} {s.get('key') or '':4} "
                f"{Path(s['path']).name[:50]}"
            )
    return 0


def cmd_library_watch(args: argparse.Namespace) -> int:
    cfg = config.load()
    root = Path(config.get(cfg, "library.root"))
    inbox = (
        Path(args.inbox).expanduser() if args.inbox else root / layout.INBOX
    )
    if not inbox.is_dir():
        print(f"error: no inbox at {inbox}", file=sys.stderr)
        return 2

    mirror_doc = _load_mirror(args.mirror) if args.mirror else None
    allow = tuple(quality.DEFAULT_ELIGIBLE) + tuple(args.allow_tier or ())
    template = args.template or config.get(cfg, "library.template", "dj")

    def on_ready(paths: list[Path]) -> dict[str, Any]:
        report = ingest.ingest(
            paths,
            root,
            mirror=mirror_doc,
            template=template,
            move=not args.copy,
            allow_tiers=allow,
        )
        for row in report["filed"]:
            print(f"  + {Path(row['destination']).name}")
        for row in report["refused"]:
            print(
                f"  ! {row['tier']:12} {Path(row['source']).name}"
                f"  ({row.get('reason', '')})"
            )
        for row in report["duplicates"]:
            source = Path(row["source"])
            note = ""
            if not args.keep_duplicates:
                parked = watch.park(source, inbox)
                note = (
                    f" -> {watch.FILED_DIR}/" if parked else " (park failed)"
                )
            print(f"  = already present: {source.name}{note}")

        if report["filed"] and not args.no_analyze:
            bin_path = analyze.binary(None)
            if bin_path.is_file():
                targets = [Path(r["destination"]) for r in report["filed"]]
                for result in analyze.run(targets, bin_path):
                    if result.get("error"):
                        continue
                    stored = analyze.store(result)
                    print(
                        f"    {round(stored.get('bpm') or 0):>3} "
                        f"{stored.get('camelot') or '--':3} "
                        f"{Path(result['path']).name[:44]}"
                    )
            else:
                print(
                    "    (migx-analyze not built — skipping analysis)",
                    file=sys.stderr,
                )
        return report

    watch.run(
        inbox,
        AUDIO_EXTS,
        on_ready,
        interval_s=args.interval,
        settle_s=args.settle,
        once=args.once,
        max_wait_s=args.max_wait,
    )
    return 0


def cmd_library_rename(args: argparse.Namespace) -> int:
    cfg = config.load()
    root = Path(config.get(cfg, "library.root"))
    template = ingest.TEMPLATES.get(
        args.template or config.get(cfg, "library.template", "dj"),
        naming.TEMPLATE_DJ,
    )
    rows = rename.plan(root, template)
    if not rows:
        print("every track is already correctly named")
        return 0

    done, conflicts = [], []
    for row in rows:
        if args.dry_run:
            mark = "!" if row["conflict"] else "→"
            print(
                f"  {mark} {Path(row['from']).name[:42]:44} "
                f"{Path(row['to']).name[:42]}"
            )
            continue
        result = rename.apply(row)
        (conflicts if result["status"] == "conflict" else done).append(result)
        if result["status"] == "renamed":
            links = len(result.get("renamed_links") or [])
            print(
                f"  → {Path(result['to']).name[:52]}"
                f"{f'  (+{links} crate)' if links else ''}"
            )
        else:
            print(
                f"  ! target exists, skipped: "
                f"{Path(result['to']).name[:44]}",
                file=sys.stderr,
            )

    if args.dry_run:
        print(
            f"\n{len(rows)} would be renamed "
            f"({sum(1 for r in rows if r['conflict'])} conflicts)"
        )
        return 0

    playlists = rename.rebuild_playlists(root) if done else []
    doc = {
        "schema": "migx.rename-report/1",
        "renamed": len(done),
        "conflicts": len(conflicts),
        "playlists_rebuilt": len(playlists),
    }
    if args.json:
        _out(doc, True)
    else:
        print(
            f"\n{len(done)} renamed · {len(conflicts)} conflicts · "
            f"{len(playlists)} playlist(s) rebuilt"
        )
    return 0


def cmd_capabilities(args: argparse.Namespace) -> int:
    doc = {
        "schema": "migx.capability-manifest/1",
        "api_version": 1,
        "commands": CAPABILITIES,
    }
    if args.json:
        _out(doc, True)
    else:
        for cap in CAPABILITIES:
            print(f"{cap['kind']:11} {cap['id']:22} {cap['summary']}")
    return 0


# --------------------------------------------------------------------- main


def build_parser() -> argparse.ArgumentParser:
    # `--json` is accepted either side of the subcommand: humans type
    # it last, agents tend to template it first. Both must work.
    # agents tend to template it first. Both must work.
    common = argparse.ArgumentParser(add_help=False)
    # SUPPRESS so the subparser's default cannot clobber a flag set before the
    # subcommand; the attribute exists only where it was actually passed.
    common.add_argument(
        "--json",
        action="store_true",
        default=argparse.SUPPRESS,
        help="emit machine-readable JSON on stdout",
    )

    parser = argparse.ArgumentParser(
        prog="migx",
        description=__doc__,
        parents=[common],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(
        dest="command",
        required=True,
        parser_class=(
            lambda **kw: argparse.ArgumentParser(parents=[common], **kw)
        ),
    )

    p = sub.add_parser(
        "spotify.login", help="link a Spotify account (OAuth PKCE)"
    )
    p.add_argument("--client-id", default=None)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--no-browser", action="store_true")
    p.set_defaults(fn=cmd_login)

    sub.add_parser("spotify.status", help="show link status").set_defaults(
        fn=cmd_status
    )
    sub.add_parser("spotify.logout", help="forget stored token").set_defaults(
        fn=cmd_logout
    )
    sub.add_parser(
        "playlist.list", help="list reachable playlists"
    ).set_defaults(fn=cmd_playlist_list)

    p = sub.add_parser(
        "playlist.pull", help="snapshot a playlist to a mirror doc"
    )
    p.add_argument("id", help="playlist id/URI/URL, or 'liked'")
    p.add_argument("--out", default=None)
    p.add_argument("--root", default=None)
    p.add_argument(
        "--preview", action="store_true", help="show rendered filenames"
    )
    p.add_argument(
        "--force-full",
        action="store_true",
        help="always re-page tracks (default is skip when snapshot_id matches)",
    )
    p.add_argument(
        "--min-interval",
        type=float,
        default=None,
        help="minimum seconds between API calls (default from config / 0.3)",
    )
    p.set_defaults(fn=cmd_playlist_pull)

    p = sub.add_parser(
        "library.inspect", help="classify files against the quality bar"
    )
    p.add_argument("paths", nargs="+")
    p.add_argument(
        "--allow-tier",
        action="append",
        default=[],
        choices=[quality.TIER_MP3_VBR, quality.TIER_UNKNOWN],
        help="accept an extra tier beyond 320-CBR/lossless",
    )
    p.set_defaults(fn=cmd_library_inspect)

    p = sub.add_parser(
        "library.resolve", help="match a mirror against files you own"
    )
    p.add_argument("mirror")
    p.add_argument("--root", action="append", default=[])
    p.add_argument("--out", default=None)
    p.add_argument(
        "--resolver",
        default=None,
        choices=resolve.available(),
        help="which resolver to use (core ships local-files)",
    )
    p.add_argument(
        "--allow-tier",
        action="append",
        default=[],
        choices=[quality.TIER_MP3_VBR, quality.TIER_UNKNOWN],
    )
    p.set_defaults(fn=cmd_library_resolve)

    p = sub.add_parser("library.missing", help="missing + upgrade gap list")
    p.add_argument("mirror", nargs="?", default=None)
    p.add_argument(
        "--all",
        action="store_true",
        help="every mirror, deduped and ranked by playlist count",
    )
    p.add_argument("--root", action="append", default=[])
    p.add_argument("--out", default=None)
    p.add_argument(
        "--resolver",
        default=None,
        choices=resolve.available(),
        help="which resolver to use (core ships local-files)",
    )
    p.add_argument(
        "--allow-tier",
        action="append",
        default=[],
        choices=[quality.TIER_MP3_VBR, quality.TIER_UNKNOWN],
    )
    p.set_defaults(fn=cmd_library_missing)

    p = sub.add_parser("library.ingest", help="file audio into Collection/")
    p.add_argument("paths", nargs="+")
    p.add_argument("--library", default=None, help="the Music/ root")
    p.add_argument("--mirror", default=None)
    p.add_argument(
        "--template", default=None, choices=sorted(ingest.TEMPLATES)
    )
    p.add_argument("--move", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--allow-tier",
        action="append",
        default=[],
        choices=[quality.TIER_MP3_VBR, quality.TIER_UNKNOWN],
    )
    p.set_defaults(fn=cmd_library_ingest)

    p = sub.add_parser("crate.sync", help="symlink a mirror into a crate")
    p.add_argument("mirror")
    p.add_argument("--library", default=None)
    p.add_argument("--crate", default=None)
    p.add_argument("--m3u8", action="store_true")
    p.add_argument("--root", action="append", default=[])
    p.add_argument(
        "--allow-tier",
        action="append",
        default=[],
        choices=[quality.TIER_MP3_VBR, quality.TIER_UNKNOWN],
    )
    p.set_defaults(fn=cmd_crate_sync)

    p = sub.add_parser("library.dedupe", help="find duplicated tracks")
    p.add_argument("--library", default=None)
    p.set_defaults(fn=cmd_library_dedupe)

    p = sub.add_parser("config.init", help="write a complete config file")
    p.add_argument("--library", default=None)
    p.add_argument("--client-id", default=None)
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_config_init)

    sub.add_parser(
        "config.show", help="resolved settings and their origin"
    ).set_defaults(fn=cmd_config_show)

    p = sub.add_parser("track.pull", help="resolve Spotify links to a sheet")
    p.add_argument("links", nargs="*", default=[])
    p.add_argument("--out", default=None)
    p.set_defaults(fn=cmd_track_pull)

    p = sub.add_parser("track.note", help="set a DJ note / tags on a track")
    p.add_argument("track")
    p.add_argument("--note", default=None)
    p.add_argument("--tag", action="append", default=[])
    p.add_argument("--append", action="store_true")
    p.set_defaults(fn=cmd_track_note)

    p = sub.add_parser("track.cue", help="bookmark a moment in a track")
    p.add_argument("track")
    p.add_argument("at")
    p.add_argument("label")
    p.add_argument("--color", default=None)
    p.add_argument("--hotcue", type=int, default=None)
    p.set_defaults(fn=cmd_track_cue)

    p = sub.add_parser("track.show", help="notes, tags and cues for a track")
    p.add_argument("track")
    p.set_defaults(fn=cmd_track_show)

    p = sub.add_parser("library.analyze", help="detect BPM and key")
    p.add_argument("paths", nargs="*", default=[])
    p.add_argument("--force", action="store_true")
    p.add_argument("--bin", default=None)
    p.set_defaults(fn=cmd_library_analyze)

    p = sub.add_parser("library.watch", help="auto-file new purchases")
    p.add_argument("--inbox", default=None)
    p.add_argument("--mirror", default=None)
    p.add_argument(
        "--template", default=None, choices=sorted(ingest.TEMPLATES)
    )
    p.add_argument("--interval", type=float, default=watch.DEFAULT_INTERVAL_S)
    p.add_argument("--settle", type=float, default=watch.DEFAULT_SETTLE_S)
    p.add_argument(
        "--once",
        action="store_true",
        help="drain the inbox, then exit (launchd)",
    )
    # Must stay under the launchd StartInterval (300s) — see watch.py.
    p.add_argument(
        "--max-wait", type=float, default=watch.DEFAULT_MAX_WAIT_S
    )
    p.add_argument("--copy", action="store_true")
    p.add_argument("--no-analyze", action="store_true")
    p.add_argument(
        "--keep-duplicates",
        action="store_true",
        help="leave already-filed files in the inbox",
    )
    p.add_argument(
        "--allow-tier",
        action="append",
        default=[],
        choices=[quality.TIER_MP3_VBR, quality.TIER_UNKNOWN],
    )
    p.set_defaults(fn=cmd_library_watch)

    p = sub.add_parser("library.rename", help="re-file under current names")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--template", default=None, choices=sorted(ingest.TEMPLATES)
    )
    p.set_defaults(fn=cmd_library_rename)

    p = sub.add_parser(
        "library.art", help="render cover art in the terminal (chafa)"
    )
    p.add_argument("track", help="path, Collection fragment, or image file")
    p.add_argument("--width", type=int, default=40)
    p.add_argument("--height", type=int, default=12)
    p.add_argument(
        "--color",
        action="store_true",
        help="16-colour symbols (default mono for curses safety)",
    )
    p.add_argument(
        "--format",
        default="symbols",
        choices=["symbols", "kitty", "iterm", "sixels"],
        help="symbols = portable; kitty/iterm/sixels need a supporting TTY",
    )
    p.set_defaults(fn=cmd_library_art)

    p = sub.add_parser(
        "library.covers",
        help="backfill cover.* for tracks missing folder art",
    )
    p.add_argument("paths", nargs="*", default=[])
    p.add_argument(
        "--thumb",
        default=None,
        help="extra thumb dir (default: <library>/_Inbox/.thumb)",
    )
    p.add_argument(
        "--no-embedded",
        action="store_true",
        help="do not extract ID3 APIC frames",
    )
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_library_covers)

    p = sub.add_parser(
        "set.plan",
        help="order Collection tracks into a mixable running set",
    )
    p.add_argument(
        "--opener",
        default=None,
        help="path or filename to lead with (default: coldest opening)",
    )
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--out", default=None, help="write the order as an .m3u8")
    p.set_defaults(fn=cmd_set_plan)

    p = sub.add_parser(
        "track.feedback",
        help="record what the DJ said about a track",
    )
    p.add_argument(
        "track",
        help="path, Collection fragment, or 'now' (after session.bind)",
    )
    p.add_argument("--fit", choices=feedback.FITS, default=None)
    p.add_argument("--placement", choices=feedback.PLACEMENTS, default=None)
    p.add_argument("--segment", choices=feedback.SEGMENTS, default=None)
    p.add_argument("--transition", type=int, default=None)
    p.add_argument("--note", default=None)
    p.set_defaults(fn=cmd_track_feedback)

    sub.add_parser(
        "session.now", help="what track is 'now' for coaching"
    ).set_defaults(fn=cmd_session_now)

    p = sub.add_parser("session.bind", help="point session.now at a track")
    p.add_argument("track")
    p.add_argument("--deck", default=None)
    p.add_argument("--position", type=float, default=None)
    p.set_defaults(fn=cmd_session_bind)

    p = sub.add_parser(
        "session.room", help="session-local crowd/theme/energy"
    )
    p.add_argument("--theme", default=None)
    p.add_argument("--energy", default=None)
    p.add_argument("--note", default=None)
    p.set_defaults(fn=cmd_session_room)

    sub.add_parser(
        "session.clear", help="clear live binding"
    ).set_defaults(fn=cmd_session_clear)

    p = sub.add_parser(
        "session.show",
        help="reconstruct tonight's plays + feedback from the session log",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        help="only the last N events",
    )
    p.set_defaults(fn=cmd_session_show)

    p = sub.add_parser(
        "set.play",
        help="render a planned set into one beatmatched mix, and play it",
    )
    p.add_argument("--out", default=None, help="output audio file")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--seconds", type=float, default=setplay.DEFAULT_SECONDS)
    p.add_argument(
        "--crossfade", type=float, default=setplay.DEFAULT_CROSSFADE
    )
    p.add_argument("--opener", default=None)
    p.add_argument("--no-play", action="store_true")
    p.set_defaults(fn=cmd_set_play)

    sub.add_parser(
        "system.capabilities", help="machine-readable command manifest"
    ).set_defaults(fn=cmd_capabilities)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.json = getattr(args, "json", False)
    try:
        return args.fn(args)
    except (auth.AuthError, api.ApiError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
