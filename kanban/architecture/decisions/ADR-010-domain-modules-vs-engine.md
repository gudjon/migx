---
id: ADR-010
type: decision
title: "Domain modules vs the engine — two sides, one seam"
status: accepted
owner: gudjon
created: "2026-08-18"
lastUpdated: "2026-08-18"
supersedes: []
amends: [ADR-009]
related:
  - ADR-002
  - ADR-007
  - ADR-008
  - ADR-009
  - arch-engine-realtime
  - arch-control-messaging
  - arch-mixer-decks
  - arch-cli-commands
  - P-02
  - P-06
  - P-07
  - P-16
  - P-17
  - P-20
---

# ADR-010 — Domain modules vs the engine

## Context

The map has 17 bounded contexts keyed on the real-time axis. That axis is
correct and stays. What it does not name is the other load-bearing split:
**DJ meaning versus the audio callback.**

Without that split, four things keep leaking across the line:

1. Playlist folders pretending to be the collection (files copied per list).
2. `mixxxdb.sqlite` and ArcFlow both acting as libraries instead of derived indexes.
3. `EngineObject : QObject` — a GUI framework as the process-graph object model.
4. Domain types (`Track`, crate, ISRC, sidecar, session) growing new call sites
   inside `src/engine/`.

ADR-007 already says views emit intent and bind the engine only through typed
proxies. ADR-008 already says adapters share one command core. ADR-009 says the
engine stays C++ (not Swift). This ADR names the **partition those decisions
assume**.

## Decision

**Every bounded context is on the ENGINE side, the DOMAIN side, or the SEAM.
Nothing is a peer of both.**

| Side | Owns | Must never |
| --- | --- | --- |
| **ENGINE** | `process()` graph, sample buffers, sync/scale/FX, the audio-clock origin | Songs, crates, playlists, ISRC, sidecars, `mixxxdb`, ArcFlow, Spotify, sessions, GUI objects |
| **DOMAIN** | Identity, Collection/crates, sidecars, browse + traversal indexes, session, commands, views | `process()`, `CSAMPLE` mixing, RubberBand/SoundTouch, `EngineSync`, the device callback |
| **SEAM** | The only legal crossings (below) | A third product, a second writer, a second library |

**Domain module** means a bounded context that owns DJ meaning. It may run on
GUI or worker threads. It is never reachable from `process()`.

### Legal crossings (closed list)

A domain module may reach the engine only through one of:

1. **ControlObject atomics** — `[Group],key` doubles. Intent in, status out.
   Single writer (`P-06`). Value path lock-free (`P-16`). Object graph off-RT
   (`P-17`). Detail: `boundaries/control-to-engine.md`.
2. **Mixer lifecycle handoff** — `PlayerManager` constructs `EngineChannel` on
   the GUI thread and hands a pointer. `BaseTrackPlayer` is the only loader of
   a `TrackPointer` into `EngineBuffer::loadTrack` (GUI thread; comment at
   `enginebuffer.cpp:1580`). Detail: `arch-mixer-decks`.
3. **Decode FIFO** — `CachingReader` / worker. Domain supplies a path/identity;
   the worker produces decoded PCM chunks into a preallocated cache; `process()`
   reads resident samples only. `util/fifo.h` (`P-16`).
4. **Immutable snapshots** — `BeatsPointer` and gain already resolved off-RT.
   The callback reads the snapshot; it never locks `GlobalTrackCache` or mutates
   a `Track` (`arch-track-model`).
5. **One-way taps** — `VisualPlayPosition` and similar lock-free publications.
   Display clock samples them. They never gate the audio deadline.
   Detail: `boundaries/engine-to-waveform.md`.

The master buffer leaving the engine is **not** a domain crossing. It is
engine → soundio on the same callback (`boundaries/engine-to-soundio.md`).

### Forbidden crossings

- Domain `QObject` slot delivered onto the callback (`Qt::DirectConnection`
  from GUI/controller into `process()`-reachable code). Intra-engine wiring
  that still uses DirectConnection is **debt**, not a new pattern (`P-20`).
- Engine code including library DAOs, ArcFlow, sidecars, mirrors, or command
  handlers.
- Engine knowing Collection vs crate vs playlist. Those words do not exist
  inside `src/engine/`.
- `mixxxdb.sqlite` or ArcFlow on the callback — already **wont-do**.
- A second writer around the command core or around a `[Group],key`.

### Indexes stay on the domain side

| Store | Role | Side |
| --- | --- | --- |
| `Collection/` | one audio inode | DOMAIN (bytes) |
| sidecar / `.migx/` | authored musical truth | DOMAIN (SSoT) |
| `mixxxdb.sqlite` | rebuildable **browse** index | DOMAIN (derived) |
| ArcFlow | rebuildable **traversal** index | DOMAIN (derived) |
| `_mirrors/` | remote identity snapshot | DOMAIN (identity) |
| `Crates/` + `.m3u8` | references, never copies | DOMAIN (refs) |

If deleting SQLite or the ArcFlow workspace loses a cue, a BPM, or a file, the
layering is wrong (`P-07`). The engine sees none of these stores.

### Qt in the engine

ADR-009 is amended, not withdrawn:

- **Language:** the engine stays **C++**. Swift must not leak into the RT graph.
- **Object model:** `QObject` / `Q_OBJECT` / moc / `QString` ConfigKeys on
  `process()` are Mixxx inheritance. They are a **peel**, not a rewrite, and
  not a reason to add more.

New DSP is a plain `process()` node. New engine wiring polls atomics inside
`process()` (`PollingControlProxy`). Drop `EngineObject : QObject` only after
the wiring that requires it is gone.

## Consequences

- A change that needs a song, a crate, or a “why next” belongs in a domain
  module (usually `arch-cli-commands` or `arch-library-db`), then crosses the
  seam as a command → single writer → control or load.
- A change that needs a sample, a deadline, or a scaler belongs in the engine
  and takes no domain header.
- `arch-mixer-decks` remains the hardest file: it is the seam that constructs
  engine nodes. It does not become a place to grow library or session logic.
- Enforcement is review + the existing house-physics patterns. A lint that
  flags `src/engine/` including `src/library/` / `src/database/` / ArcFlow is
  a valid follow-up; it is not required to accept this ADR.

## Enforcement surfaces

| Surface | What |
| --- | --- |
| This ADR | Decision SSoT |
| `ddd/boundaries/domain-to-engine.md` | Partition + crossing list |
| `ddd/context-map.md` | Picture |
| `arch-engine-realtime` / `src/engine/AGENTS.md` | Engine-side contract |
| `arch-mixer-decks` / `src/mixer/AGENTS.md` | Lifecycle seam |
| `boundaries/control-to-engine.md` | Intent/status crossing |
