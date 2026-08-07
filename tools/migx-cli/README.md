# `migx` - the TUI-first command spine

Migx is built **TUI first**. The rich human terminal workspace, deterministic CLI,
one-shot JSON, and external agents such as Claude Code and Codex all drive the
same command/query/event/capability core. Same handlers, schemas, validation, and
receipts; no second-class consumer and no private UI control plane.

Canonical decision: [`ADR-008`](../../kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md).
Interaction reference:
[`tui-first-agentic-dj-workstation`](../../kanban/knowledge/tui-first-agentic-dj-workstation.md).

The current command core is stdlib only - no `spotipy`, `typer`, or `textual`.
The future TUI may use an isolated framework dependency, but CLI/JSON/agent use
must not require the renderer. Dependencies get added from measured evidence.

```bash
./tools/migx-cli/migx system.capabilities        # what exists (agents start here)
./tools/migx-cli/migx system.capabilities --json # machine-readable
```

## Product surface and current truth

| Surface | Contract | Current state |
| --- | --- | --- |
| `migx` | Human TUI workspace | planned |
| `migx <noun>.<verb> ...` | Deterministic CLI | metadata/library subset built |
| `migx <noun>.<verb> ... --json` | One-shot machine result | built for current commands |
| `migx --agent` | Long-lived JSONL requests, events, cancellation, receipts | planned |
| `migx mcp-server` | Optional tools over the same core | planned |

Today this package is metadata/library only. It does not control a deck, subscribe
to engine events, or touch a ControlObject. Do not describe planned TUI or agent
capabilities as shipped until their code and gates exist.

## Interface kinds

Every surface entry is exactly one of four kinds (ADR-008, accepted):

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

## Ban / block posture (hard rules)

Migx is built so a normal user **does not get Spotify API access cut off** for
using this CLI. That is not a guarantee against every future platform policy
change, but these are the methods Spotify documents as correct:

| Rule | What we do |
| --- | --- |
| Official OAuth only | PKCE to `accounts.spotify.com` — no client secret, no unofficial “free API” |
| Official Web API only | Requests only to `api.spotify.com` — host allowlist rejects anything else |
| Read-only scopes | `user-library-read`, `playlist-read-private`, `playlist-read-collaborative` only |
| Metadata only | Never requests, decrypts, or stores audio / streams |
| Honest client | Real `User-Agent`; no browser automation of the player |
| Pace | Min interval between calls (default **0.3s**); honour `Retry-After` |
| Circuit break | Stop after repeated 429s; distinguish `QUOTA_EXCEEDED` from pace limits |
| Skip work | `playlist.pull` defaults to **snapshot_id short-circuit** (one meta request when unchanged) |
| Sparse fields | Request only the fields the mirror schema needs |
| Token hygiene | Access token cached in Keychain until near expiry; refresh serialised |

**What actually gets people in trouble** (and what we never do):

- Unofficial clients that reverse-engineer Spotify’s internal APIs (e.g. SpotipyFree-class paths)
- Stream ripping / librespot / zotify-class tools
- Driving the web player with computer-use to capture audio
- Retrying 404s or hammering through 429s without backoff
- Write scopes that modify the user’s library without need

Rate limits (429) are temporary throttles. **Account bans** are a different axis —
they attach to DRM circumvention and ToS abuse, not to a well-behaved OAuth
metadata client. Stay on this path.

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

```bash
./tools/migx-cli/migx library.resolve mirror.json --root ~/Music
./tools/migx-cli/migx library.missing mirror.json --root ~/Music --json
```

### The resolver seam

A resolver answers exactly one question: *where is the audio for this identity?*

| Element | Rule |
| --- | --- |
| Input | one mirror entry; **ISRC is the join key** |
| Output | a path to an existing local file, or `None` |
| Purity | must not mutate the mirror, must not write the index |
| Gate | output **always** passes `quality.verdict` — no resolver self-certifies |
| Registration | by name; core ships `local-files` only |

Match order: **ISRC** (exact, needs no scoring) → **scored** (best candidate
above the floor wins).

The scoring model is adapted from [spotDL's `utils/matching.py`][spotdl] (MIT,
so compatible with Migx's GPL-2): artist similarity, title similarity, and a
duration term with exponential decay, with rejection floors rather than a
single blended threshold.

**One deliberate inversion for DJ use.** spotDL *penalises* `remix`, `live`,
`instrumental` as likely false positives — correct for a consumer who wants the
album version. For a DJ those are frequently the track you actually want, so
here they are treated as **identity**: a variant mismatch in *either* direction
is penalised, and `Feel It` never silently resolves to `Feel It (Extended Mix)`.
Words that really are noise for matching — `(Original Mix)`, `Remastered 2011`,
`(feat. …)`, accents — are stripped instead, and never penalised.

Normalisation applies to *matching only*, never to naming.

[spotdl]: https://github.com/spotDL/spotify-downloader

### Own-but-low is an upgrade, never a re-buy

A file you already own that fails the quality bar is **not** missing. It lands in
`below_bar` and the want-list marks it `upgrade`, so you never pay twice for a
track you have — you just replace a 128 kbps copy with a proper one.

ISRC also survives tagger disagreement: it is read from the standard `TSRC`
frame *and* from `TXXX:ISRC`, which is where ffmpeg and several taggers actually
write it. Missing that frame silently downgrades every match to fuzzy.

## Test

```bash
python3 tools/migx-cli/test_migx_cli.py    # offline, no encoder needed
```

Quality-gate parsing was verified against `ffmpeg`-encoded fixtures (320/192/128
CBR, V0 VBR, FLAC, WAV, ALAC, AAC); every bitrate reading matched `ffprobe`. The
committed tests use synthetic headers so CI needs no encoder.
