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
import sys
from pathlib import Path
from typing import Any

from . import api, auth, mirror, naming, quality, resolve

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
        },
        "emits": "migx.playlist-mirror/1",
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
    client = api.SpotifyRead(auth.access_token())
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


def cmd_playlist_pull(args: argparse.Namespace) -> int:
    client = api.SpotifyRead(auth.access_token())

    if args.id == "liked":
        doc = mirror.build(
            source_id="liked",
            source_name="Liked Songs",
            owner="me",
            items=client.saved_tracks(),
        )
    else:
        pid = _extract_id(args.id)
        meta = client.playlist(pid)
        doc = mirror.build(
            source_id=pid,
            source_name=meta.get("name") or pid,
            owner=(meta.get("owner") or {}).get("display_name"),
            snapshot_id=meta.get("snapshot_id"),
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
    roots = args.root or [str(Path.home() / "Music")]
    resolver = resolve.LocalFilesResolver(roots)
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
        "--allow-tier",
        action="append",
        default=[],
        choices=[quality.TIER_MP3_VBR, quality.TIER_UNKNOWN],
    )
    p.set_defaults(fn=cmd_library_missing)

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
