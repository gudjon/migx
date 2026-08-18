---
id: domain-to-engine
type: ddd-boundary
title: "Domain modules vs the engine — the partition seam"
status: active
owner: gudjon
created: "2026-08-18"
lastUpdated: "2026-08-18"
defers_to:
  - kanban/architecture/decisions/ADR-010-domain-modules-vs-engine.md
related:
  - control-to-engine.md
  - engine-to-soundio.md
  - engine-to-waveform.md
  - arch-engine-realtime
  - arch-mixer-decks
  - arch-control-messaging
  - arch-track-model
---

# Seam: domain modules → engine

**Decision:** [ADR-010](../../decisions/ADR-010-domain-modules-vs-engine.md).
This file is the map. The ADR is the SSoT. Existing per-payload seams stay
authoritative for their mechanism.

The 17 contexts are not 17 peers. They sit on two sides of one line. The
real-time axis (`thread_domain` / `rt_safety`) still governs *how* a context
runs. This seam governs *whether it may know about songs*.

```text
 DOMAIN MODULES                         ENGINE
 identity · Collection · sidecar        process() mix / scale / FX / sync
 crates / playlists (refs only)         CSAMPLE buffers
 mixxxdb browse (derived)               EngineSync · bufferscalers
 ArcFlow traversal (derived)            vinyl RT
 commands · session · views             soundio callback (clock origin)
                    \                 /
                     \     SEAM      /
                      control atomics
                      mixer lifecycle
                      TrackPointer load → decode FIFO
                      immutable Beats/gain snapshot
                      one-way visual tap
```

## Partition (every card, once)

| Side | Contexts |
| --- | --- |
| **ENGINE** | `arch-engine-realtime`, `arch-effects-chain` (RT half), `arch-vinylcontrol`, `arch-audio-io` |
| **DOMAIN** | `arch-library-db`, `arch-track-model` (aggregate), `arch-cli-commands`, `arch-analyzer`, `arch-musicbrainz`, `arch-qml-ui`, `arch-skin-widgets`, `arch-controllers-mapping`, `arch-rendergraph` |
| **SEAM** | `arch-control-messaging`, `arch-mixer-decks`, `arch-sources-decode` (worker), `arch-waveform-render` (tap), `arch-track-model` (RT snapshot read only) |

`arch-track-model` is domain. The callback may *read* an already-resolved
immutable snapshot. That read is a crossing, not a reason to put `Track`
mutation in `src/engine/`.

Views and controllers sit on the domain side: they emit intent. They do not
call `process()`.

## What may cross

Closed list. If a new payload is not one of these, it needs an ADR, not a
convenient `#include`.

| # | Payload | From → to | Mechanism | Detail |
| --- | --- | --- | --- | --- |
| 1 | `[Group],key` doubles | domain intent → engine; engine status → domain | `ControlValueAtomic` / `PollingControlProxy` | `control-to-engine.md` |
| 2 | `EngineChannel*` | mixer → engine | GUI-constructed pointer, lifetime off-RT | `arch-mixer-decks` |
| 3 | `TrackPointer` load/eject | mixer → `EngineBuffer::loadTrack` | GUI thread only (`enginebuffer.cpp:1580`); reader FIFO | `basetrackplayer.cpp` → `cachingreader/` |
| 4 | decoded PCM chunks | decode worker → `process()` | preallocated cache + `util/fifo.h` | `arch-sources-decode` |
| 5 | `BeatsPointer` / gain | track-model → sync/scale | immutable snapshot, no cache lock | `arch-track-model` |
| 6 | playhead / visual state | engine → display | lock-free `VisualPlayPosition` | `engine-to-waveform.md` |

Engine → device (`CSAMPLE` master) is **not** this seam.
`engine-to-soundio.md`.

## What must not cross

- Collection, crate, playlist, ISRC, Spotify, sidecar, session, ArcFlow, DAO,
  `mixxxdb.sqlite` — **no symbol** of these in `src/engine/` `process*()`.
- Domain `QObject` mutated or slot-delivered on the callback (`P-20`, `AP-14`).
- Engine calling a command handler, or a command handler calling `process()`.
- Alloc / lock / I/O on the callback (`P-02`). Page faults from a fresh mmap
  count as I/O.

## The mixer is the door, not a third product

`PlayerManager` / `BaseTrackPlayer` construct the engine node and load the
track. Library, crates, TUI, and agents stop at the player:

```text
command / view / crate
        → PlayerManager / BaseTrackPlayer     (DOMAIN + SEAM, GUI)
            → EngineBuffer::loadTrack         (GUI; queues worker)
                → CachingReaderWorker         (worker decode)
                    → PCM cache
                        → EngineBuffer::process  (ENGINE, audio callback)
```

Do not grow session, ontology, or browse logic in `src/mixer/` just because
it can see both sides.

## Indexes (domain only)

Sidecar is SSoT for authored metadata. `mixxxdb.sqlite` is the browse index.
ArcFlow is the traversal index. Both indexes are rebuildable from disk.
Neither is visible to the engine. Cite
`filesystem-driven-architecture.md` and
`arcflow-tui-agentic-dj-integration.md` — do not copy them.

## Qt peel (engine side)

`EngineObject : QObject` and `Qt::DirectConnection` inside `src/engine/` are
why the partition is currently soft. New engine code does not add `Q_OBJECT`.
New wiring polls atomics in `process()`. Removing the base class is a later
wave, gated on `ctest -R Engine` and a p99/underrun contract (`P-03`/`P-18`).
