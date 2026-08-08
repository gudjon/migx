# `migx` - the TUI-first command spine

Migx is built **TUI first**. The rich human terminal workspace, deterministic CLI,
one-shot JSON, and external agents such as Claude Code and Codex all drive the
same command/query/event/capability core. Same handlers, schemas, validation, and
receipts; no second-class consumer and no private UI control plane.

Canonical decision: [`ADR-008`](../../kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md).
Interaction reference:
[`tui-first-agentic-dj-workstation`](../../kanban/knowledge/tui-first-agentic-dj-workstation.md).

The current command core and TUI are stdlib only - no `spotipy`,
`typer`, or `textual`. A richer TUI may later use an isolated framework
dependency, but CLI/JSON/agent use must not require the renderer. Dependencies
get added from measured evidence.

```bash
./tools/migx-cli/migx system.capabilities        # what exists (agents start here)
./tools/migx-cli/migx system.capabilities --json # machine-readable
```

## Product surface and current truth

| Surface | Contract | Current state |
| --- | --- | --- |
| `migx` | Human TUI workspace | planned |
| `tools/migx-cli/migx-tui` | Interactive preparation TUI | multi-mode adapter built and snapshot-tested |
| `migx <noun>.<verb> ...` | Deterministic CLI | library/preparation subset built |
| `migx <noun>.<verb> ... --json` | One-shot machine result | built for current commands |
| `migx --agent` | Long-lived JSONL requests, events, cancellation, receipts | planned |
| `migx mcp-server` | Optional tools over the same core | planned |

Today this package is library/preparation only. The TUI has Overview, Library,
Arrange, Prep, Track, and Deck modes; selection; analyzed BPM/key/energy; cue
markers; DJ notes; color roles; energy sparklines; a full-screen track heatmap;
and data-backed transition support over a pure snapshot. It does not control a
deck, subscribe to engine events, or touch a ControlObject. Do not describe LIVE
control or agent capabilities as shipped until their code and gates exist.

```bash
./tools/migx-cli/migx-tui
```

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

## Spotify Web API client (engineering notes)

Wave 1 talks to the official Web API with OAuth PKCE. Practical client hygiene:

| Practice | Why |
| --- | --- |
| Host allowlist (`api.spotify.com` / `accounts.spotify.com`) | Stay on documented endpoints |
| Read-only scopes | Library/playlist identity only |
| Pace (default 0.3s) + `Retry-After` | Avoid 429 storms |
| Circuit break on repeated 429s | Fail loud instead of hammering |
| `snapshot_id` short-circuit on `playlist.pull` | Cheap re-polls |
| Access token cache + refresh lock | Avoid refresh thrash / silent logout |

## Session coaching (live "now" + structured feedback)

While a track is in focus, bind it so a coding agent (voice/chat) can attach
floor judgment without guessing which file you mean — **CLI only, no MCP**.

```bash
./tools/migx-cli/migx session.bind "Reckoning" --deck A
./tools/migx-cli/migx session.now --json
./tools/migx-cli/migx session.room --theme melodic --energy mid
./tools/migx-cli/migx track.feedback now --fit retire --note "felt tired"
./tools/migx-cli/migx track.feedback now --segment shorter --transition 2
./tools/migx-cli/migx session.show              # reconstruct the night
./tools/migx-cli/migx session.show --json       # plays[] + events[] for agents
./tools/migx-cli/migx session.clear             # unbind; log stays for show
```

Files (library root, off-RT): `_live.json` (current bind + room),
`_session.jsonl` (append-only bind / room / feedback / clear).

**What feedback does to the next set** (lifetime sidecar → `set.plan` / TUI Arrange):

| Verdict | Effect |
| --- | --- |
| `--fit retire` | excluded from the set (reported, never silent) |
| `--fit weak` / `worked` | demotes / promotes as next-track candidate |
| `--placement opener` / `peak` | opening-slot preference |
| `--transition 1..5` | how well blends *into* this track landed |
| `--segment shorter` / `longer` | play length for offline audition (`set.play`) |

TUI: open Track mode (`t`) also runs `session.bind` (source=`tui`).  
Agent skill: `.claude/skills/migx-session-coach/` — maps speech → these commands.  
Research: `kanban/knowledge/session-coaching-multimodal-agent.md`.

## Cover art in the terminal (optional chafa)

Track covers can render as Unicode art when [chafa](https://hpjansson.org/chafa/)
is installed. This is **optional** — missing chafa or missing cover degrades to a
placeholder / silent skip; the rest of the CLI never depends on it.

```bash
brew install chafa                         # macOS
./tools/migx-cli/migx library.art cover.png
./tools/migx-cli/migx library.art "7 Seconds" --width 48 --height 14
./tools/migx-cli/migx library.art track.mp3 --format iterm   # iTerm2 raster
./tools/migx-cli/migx-tui                  # Track mode (t) shows mono art if found
```

Cover discovery (no tag decoding): `cover.jpg` / `folder.png` next to the audio,
images in `<track>.migx/`, or a fuzzy match under `_Inbox/.thumb/`.  
**Ingest / watch:** when a cover is found next to the source (or in `.thumb`),
`library.ingest` copies it to `cover.<ext>` beside the Collection file so art
survives after the inbox is drained.

**Backfill existing Collection** (thumbs left behind, or embedded APIC):

```bash
./tools/migx-cli/migx library.covers --dry-run
./tools/migx-cli/migx library.covers              # default: _Inbox/.thumb + APIC
./tools/migx-cli/migx library.covers --no-embedded
```

Override binary: `MIGX_CHAFA_BIN=/path/to/chafa`.  
Curses uses **symbols + monochrome** only (no ANSI); `--color` / kitty / sixels
are for raw TTY stdout.

## Quality gate (on the file)

Classify local audio by **what the file actually is**, not how it was produced:

```bash
./tools/migx-cli/migx library.inspect ~/Music/incoming
```

| Tier | Verdict |
| --- | --- |
| `lossless` (FLAC/WAV/AIFF/ALAC) | eligible |
| `mp3-320-cbr` (true 320 CBR) | eligible |
| `mp3-vbr-high` (VBR ≥ 220 kbps) | needs `--allow-tier mp3-vbr-high` |
| `below-bar` | refused |

## Common loop

```text
spotify.login → playlist.pull → library.resolve → library.missing
     → files land under the library root → library.ingest / crate.sync
```

```bash
./tools/migx-cli/migx library.resolve mirror.json --root ~/Music
./tools/migx-cli/migx library.missing mirror.json --root ~/Music --json
```

### The resolver seam

A resolver answers: *where is the audio for this identity?*

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

### Own-but-low is an upgrade, not “missing”

A file that fails the quality bar is **not** absent. It lands in `below_bar` and
`library.missing` marks it `upgrade` so a weak encode is not treated as a brand-new gap.

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
