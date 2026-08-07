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
import sys
from pathlib import Path
from typing import Any

from . import (
    api,
    auth,
    config,
    ingest,
    layout,
    mirror,
    naming,
    quality,
    ratelimit,
    resolve,
    tracklist,
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
        "summary": "The want-list: what to acquire, and what to upgrade.",
        "args": {
            "mirror": "mirror document, or a resolution report",
            "--root": "library root to scan (repeatable)",
            "--out": "write the want-list here",
        },
        "emits": "migx.want-list/1",
        "note": "ISRC-keyed so store lookup is exact. Owning a file below"
        " the bar is an upgrade, never a re-buy.",
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
        "summary": "Resolve Spotify track links into an actionable sheet.",
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
    want = resolve.want_list(_run_resolve(args))
    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(want, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.json:
        _out(want, True)
    else:
        print(
            f"acquire {want['acquire_count']} · "
            f"upgrade {want['upgrade_count']}"
        )
        for item in want["items"]:
            tag = "BUY " if item["want"] == "acquire" else "UPGR"
            isrc = item.get("isrc") or "-"
            print(f"{tag} {isrc:14} {item['store_query']}")
        print(
            "\nISRC is exact — search it at your store before the text query.",
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

    p = sub.add_parser("library.missing", help="the ISRC-keyed want-list")
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
