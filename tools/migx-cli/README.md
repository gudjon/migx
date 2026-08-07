# `migx` CLI — the command spine

The interface layer both clients drive: the **DJ TUI/UI** and the **agentic peers**
(Claude Code, Codex, Grok). Same commands, same schemas, no second-class consumer.

Stdlib only — no `spotipy`, no `typer`, no `textual`. `tools/` has carried zero
Python dependencies and wave 1 keeps it that way; deps get added from evidence,
not upfront.

```bash
./tools/migx-cli/migx system.capabilities        # what exists (agents start here)
./tools/migx-cli/migx system.capabilities --json # machine-readable
```

## Interface kinds

Every command is exactly one of four kinds (ADR-008, draft):

| Kind | Meaning |
| --- | --- |
| `command` | mutates state; routed through a single writer (`P-06`) |
| `query` | pure read, no side effect |
| `event` | engine → client push (not yet implemented) |
| `capability` | introspection, so an agent can discover the surface |

`--json` works before *or* after the subcommand. Machine output goes to **stdout**,
human prose to **stderr**, so an agent can pipe stdout without filtering.

## Wave 1 — Spotify identity + playlist mirroring

```bash
export MIGX_SPOTIFY_CLIENT_ID=<your app's client id>
./tools/migx-cli/migx spotify.login          # OAuth 2.0 PKCE, loopback, Keychain
./tools/migx-cli/migx spotify.status --json
./tools/migx-cli/migx playlist.list
./tools/migx-cli/migx playlist.pull liked --preview
./tools/migx-cli/migx playlist.pull 37i9dQZF1DXcBWIGoYBM5M
```

Register an app at <https://developer.spotify.com/dashboard> with redirect URI
exactly `http://127.0.0.1:8888/callback`. **PKCE means there is no client secret** —
a secret shipped in a CLI is not a secret. The refresh token lives in the macOS
Keychain, and rotation is persisted on every refresh (single-use refresh tokens
otherwise cause silent lockout).

Scopes are read-only: `user-library-read`, `playlist-read-private`,
`playlist-read-collaborative`. This tool never writes to your Spotify account.

### Discover Weekly / Release Radar

Not reachable. Since **2024-11-27** Spotify blocks algorithmic and Spotify-owned
editorial playlists for apps without a prior quota extension. `playlist.pull` on
one returns a 403 explaining the fix:

> **Duplicate the playlist inside Spotify, then pull your copy.** A playlist *you*
> own is ordinary `playlist-read-private` data.

This is better than API access would have been: DW is regenerated every Monday and
RR every Friday, destroying the previous week. Dated mirrors give Migx a
longitudinal taste corpus Spotify itself does not retain.

## Metadata only — and the quality gate

This CLI reads **identities**, never audio. Spotify's audio is DRM-protected and
app-bound; ripping it violates their ToS, and routing around it through YouTube is
copyright infringement with a lossy→lossy transcode attached. See
`kanban/knowledge/spotify-octave-style-doable-steps.md`.

The bar is enforced as a contract on the **file**, not on the pipeline:

```bash
./tools/migx-cli/migx library.inspect ~/Music/incoming
```

| Tier | Verdict |
| --- | --- |
| `lossless` (FLAC/WAV/AIFF/ALAC) | eligible |
| `mp3-320-cbr` (true 320 CBR) | eligible |
| `mp3-vbr-high` (VBR ≥ 220 kbps) | needs `--allow-tier mp3-vbr-high` |
| `below-bar` | refused |

That makes the engineering line and the licensing line the same line: the sources
that cut legal corners are the same ones that cannot produce true 320 CBR.

## The loop

```text
spotify.login → playlist.pull → library.resolve → library.missing (ISRC want-list)
     → you buy on Beatport/Bandcamp → local resolver fills paths → library.index
```

The resolver is an interface. Core ships the **local-files** resolver only;
acquisition backends stay out of core.

## Test

```bash
python3 tools/migx-cli/test_migx_cli.py    # offline, no encoder needed
```

Quality-gate parsing was verified against `ffmpeg`-encoded fixtures (320/192/128
CBR, V0 VBR, FLAC, WAV, ALAC, AAC); every bitrate reading matched `ffprobe`. The
committed tests use synthetic headers so CI needs no encoder.
