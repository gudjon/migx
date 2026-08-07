---
id: arch-cli-commands
type: ddd-bounded-context
title: "cli-commands — the application surface every adapter drives"
owns:
  - tools/migx-cli/             # migx_cli package: auth, api, mirror, resolve, ingest, layout, quality
exclude: []
thread_domain: worker
rt_safety: none
subdomain: core
upstream: []
downstream: [arch-library-db, arch-track-model]
maturity: developing
fork_delta: migx-new
agents_md: tools/migx-cli/README.md
last_audited: "2026-08-07"
---

# cli-commands — bounded context

The application/interface layer over the domain contexts. One command surface,
four adapter classes: the human TUI, direct CLI/JSON, agent/MCP, and a future
graphical adapter. None is a second-class client — see `ADR-008`. Pointers,
never copies: the code in `owns:` is the truth, and `system.capabilities` will
be generated from it so the manifest cannot describe a command that does not
exist.

Today this context is **metadata only**. It reads Spotify identities, matches
them against local files, and files audio into the Collection. It holds no
`ControlObject`, touches no audio callback, and decodes no audio.

An initial read-only curses dashboard is built over a pure snapshot. The richer
PREP/LIVE TUI, long-lived `--agent` stream, receipts, events, MCP adapter, and
engine bridge are planned. This bounded context records their contract without
claiming those later capabilities ship today.

## Key aggregates / classes

| Class | File | Role |
| --- | --- | --- |
| command registry | `migx_cli/__main__.py` | the surface: id, kind, args, emitted schema |
| TUI snapshot/renderer | `migx_cli/tui.py` | pure metadata snapshot + thin curses dashboard |
| `SpotifyRead` | `migx_cli/api.py` | read-only Web API client, paced + 429-aware |
| PKCE flow | `migx_cli/auth.py` | OAuth without a client secret; Keychain token store |
| mirror builder | `migx_cli/mirror.py` | playlist → `migx.playlist-mirror/1` snapshot |
| `LocalFilesResolver` | `migx_cli/resolve.py` | identity → owned file; the acquisition seam |
| quality gate | `migx_cli/quality.py` | tier verdict; nothing enters the index ungated |
| layout | `migx_cli/layout.py` | Collection (one file) + Crates (symlinks) |
| ingest | `migx_cli/ingest.py` | the intake valve into the Collection |

## Invariants (an agent MUST respect these)

- **Every command is exactly one of four kinds** — `command`, `query`, `event`,
  `capability` (`ADR-008` §3). A new kind is a decision, not a convenience.
- **Nouns come from ubiquitous language** — the `<noun>` in a command id must
  appear in some context's ubiquitous-language table. Enforced by
  `kanban/architecture/lint/verify-command-vocabulary.py`. Inventing a parallel
  vocabulary is `P-11`.
- **One writer survives every adapter (`P-06`)** — when this layer starts writing
  `[Group],key`, TUI, CLI, agent, MCP, and graphical clients route through one
  handler. Many adapters, one writer.
- **Never on the RT thread (`P-02`/`P-16`)** — nothing here may be called from
  `process*()`; when engine commands land they cross lock-free.
- **Library writes go through the DAO layer (`P-27`)** — this context never
  issues raw SQL against `mixxxdb.sqlite`.
- **Every unique track is exactly one audio file** — Collection holds it; crates
  and playlists are references (symlink / `.m3u8`), never copies.
- **No resolver self-certifies** — every resolver's output passes the quality
  gate before it can be indexed.
- **Machine output on stdout, human prose on stderr.**

## Ubiquitous language (terms precise *inside* this context)

| Term | Meaning here | Not to be confused with |
| --- | --- | --- |
| `command` | a surface entry that mutates state | a shell command, or a Qt `QAction` |
| `query` | a side-effect-free read on the surface | a SQL query (arch-library-db) |
| `capability` | introspection of the surface itself | a product capability (`ddd/capability-catalogue.md`) |
| `crate` | a directory of symlinks under `Crates/` | a DB-backed track set (arch-library-db) |
| `collection` | the one on-disk home for audio files | `TrackCollection`, the DB aggregate (arch-library-db) |
| `mirror` | a dated local snapshot of a remote playlist | a mixer/monitor "mirror" of audio |
| `resolver` | identity → local file strategy | a DNS resolver, or `Path.resolve()` |
| `gap-list` | ISRC-keyed missing + upgrade report (`migx.gap-list/1`) | a wishlist UI feature |
| `tier` | a quality classification of a file | a subscription tier |
| `spotify` | the remote catalogue this context reads identities from | a playback source (Migx has none) |
| `system` | the reserved namespace for surface introspection | the OS |
| `config` | the CLI's own settings file (`migx.config/1`) | Mixxx user preferences / `mixxx.cfg` (arch-preferences) |

## Boundaries (edges by id — detail in ../boundaries/)

| Dir | Seam | Other context | Mechanism | Doc |
| --- | --- | --- | --- | --- |
| out | filed tracks + indexing | arch-library-db | DAO layer (`P-27`), never raw SQL | — |
| out | track identity / tags | arch-track-model | file tags + sidecars | — |
| in | remote catalogue identities | *(external)* | Spotify Web API, read-only | `tools/migx-cli/README.md` |
| out | *(planned)* deck/mixer intent | arch-control-messaging | single-writer handler (`P-06`) | boundaries/control-to-engine.md |

## Key patterns (cited, not restated)

`P-02`, `P-06`, `P-07`, `P-09`, `P-11`, `P-16`, `P-27` — see `kanban/patterns/`.
Root house rules: `/AGENTS.md`. The decision that created this context: `ADR-008`.
