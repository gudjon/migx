---
id: arch-musicbrainz
type: ddd-bounded-context
title: "musicbrainz — online metadata lookup over async network tasks"
owns:
  - src/musicbrainz/            # TagFetcher, ChromaPrinter, MusicBrainz*, web/ lookup tasks
  - src/network/                # WebTask, JsonWebTask, NetworkTask — the async HTTP task base
exclude: []
thread_domain: worker
rt_safety: none
subdomain: generic
upstream: [arch-track-model]
downstream: [arch-library-db, arch-track-model]
maturity: operational
fork_delta: upstream-tracking
agents_md: src/musicbrainz/AGENTS.md
last_audited: "2026-07-17"
---

# musicbrainz — bounded context

Identifies a track online and fills in its tags. `TagFetcher` fingerprints the audio with
`ChromaPrinter` (AcoustID/Chromaprint), runs an `AcoustidLookupTask` then a `MusicBrainzRecordingsTask`,
and returns candidate metadata to the tag dialogs. The `src/network/` half is the reusable async plumbing
— `WebTask`/`JsonWebTask` wrap `QNetworkAccessManager` request/reply into signalled task objects. It is
network/worker code (`rt_safety: none`), never on the audio path. Pointers, never copies —
`src/musicbrainz/` + `src/network/` are the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `TagFetcher` | `musicbrainz/tagfetcher.cpp` | orchestrates fingerprint → lookup → recordings |
| `ChromaPrinter` | `musicbrainz/chromaprinter.cpp` | Chromaprint acoustic fingerprint |
| `AcoustidLookupTask` | `musicbrainz/web/acoustidlookuptask.cpp` | AcoustID id lookup task |
| `MusicBrainzRecordingsTask` | `musicbrainz/web/musicbrainzrecordingstask.cpp` | MusicBrainz recordings query |
| `CoverArtArchiveLinksTask` | `musicbrainz/web/coverartarchivelinkstask.cpp` | Cover Art Archive link lookup |
| `MusicBrainzXml` | `musicbrainz/musicbrainzxml.cpp` | parses the MB XML response |
| `WebTask` | `network/webtask.cpp` | abstract async HTTP task (request/abort/reply signals) |
| `JsonWebTask` | `network/jsonwebtask.cpp` | JSON-bodied `WebTask` specialisation |

## Invariants (an agent MUST respect these)
- **Fully async, off the RT thread (`P-17`/`P-20`):** every request is a non-blocking `WebTask` on the
  network thread; nothing here blocks a UI or audio thread waiting on I/O.
- **Fail loud (`AP-16`):** network/lookup errors are reported to the caller (dialog/log), not swallowed
  into an empty result that looks like "no match".
- **Results are proposals, not writes (`P-07`):** the fetched metadata is offered to the user/`Track`;
  this context does not silently overwrite the canonical track record.
- **Qt affinity (`P-20`):** tasks are QObjects delivering results via queued signals on their owning
  thread; no cross-thread synchronous slot into GUI/RT.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `fingerprint` | Chromaprint acoustic hash of the audio | a beatgrid / analysis result (arch-analyzer) |
| `recording` | a MusicBrainz recording entity | an audio recording session (broadcast/recording) |
| `task` | an async `WebTask` request object | an `AnalyzerThread` job (arch-analyzer) |
| `tag` | fetched metadata proposal | a file tag written by metadata sources (arch-sources-decode) |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| in | track audio + existing tags | arch-track-model | `TrackPointer` | — |
| out | proposed metadata / cover art | arch-track-model | signalled result to tag dialogs | — |
| out | accepted metadata persistence | arch-library-db | `TrackDAO` via the accepting UI | — |

## Key patterns (cited, not restated)
`P-17`, `P-20`, `P-07`, `AP-16` — see `kanban/patterns/`. Root house rules: `/AGENTS.md`. This is a
generic-subdomain integration; its discipline is async tasks and loud failure, not RT physics.
