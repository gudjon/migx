---
id: arch-track-model
type: ddd-bounded-context
title: "track-model — the Track aggregate read across every thread"
owns:
  - src/track/                  # Track, GlobalTrackCache, Beats, Cue, Keys, ReplayGain, Bpm, TrackRecord, metadata
exclude: []
thread_domain: any (read)
rt_safety: soft
subdomain: core
upstream: [arch-sources-decode]
downstream: [arch-engine-realtime, arch-library-db, arch-analyzer, arch-waveform-render]
maturity: hardened
fork_delta: upstream-tracking
agents_md: src/track/AGENTS.md
last_audited: "2026-07-17"
---

# track-model — bounded context

The in-memory model of a loaded track and its musical structure: `Track` plus its `Beats`, `Cue`s,
`Keys`, `ReplayGain` and `TrackRecord` metadata. It is read from **every** thread domain — the RT engine
reads the beatgrid for sync, the GUI reads cues and tags, analysis writes results back — so lifetime is
governed by `GlobalTrackCache` and shared as immutable snapshots (`BeatsPointer`, etc.). Reading an
already-resolved immutable snapshot is RT-callable; creating/destroying a `Track` or taking the cache
lock is **not** (`rt_safety: soft`). Pointers, never copies — `src/track/` is the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `Track` | `track/track.cpp` | the aggregate root: metadata + beats + cues + keys + record |
| `GlobalTrackCache` | `track/globaltrackcache.cpp` | single-instance cache governing `Track` lifetime |
| `Beats` | `track/beats.cpp` | immutable beatgrid snapshot (`BeatsPointer`) |
| `BeatFactory` | `track/beatfactory.cpp` | constructs `Beats` from analysis / stored data |
| `Cue` | `track/cue.cpp` | a hotcue / loop / marker on the track |
| `Keys` | `track/keys.cpp` | musical-key data (`KeyFactory` builds it) |
| `ReplayGain` | `track/replaygain.cpp` | loudness-normalisation gain |
| `Bpm` | `track/bpm.cpp` | tempo value type |
| `TrackRecord` | `track/trackrecord.cpp` | the persistable metadata record |

## Invariants (an agent MUST respect these)
- **Track lifetime happens off the RT thread (`P-17`):** `Track` construction/destruction and
  `GlobalTrackCache` locking are GUI/worker-thread work; the RT engine holds a resolved pointer only.
- **RT reads take an immutable snapshot (`P-16`):** the engine reads `Beats`/gain via an immutable
  shared pointer swapped atomically — it never locks the cache or mutates a `Track` on the callback.
- **One canonical home per fact (`P-07`):** the `Track` (and its file tags) is the source of truth; the
  library DB and QML models hold derived copies, reconciled back through here.
- **Single writer per mutable field (`P-06`):** a given track field has one authoritative writer at a
  time; concurrent mutation goes through the track's own guarded API, not RT-side.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `track` | the in-memory `Track` aggregate | a DB row / model entry (arch-library-db) |
| `beats` | the `Beats` beatgrid snapshot | an engine "beat" tick (arch-engine-realtime sync) |
| `cue` | a stored `Cue` marker | a controller "cue" button (arch-controllers-mapping) |
| `key` | musical `Keys` data | a `[Group],key` control key (arch-control-messaging) |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| out | beatgrid / gain read on RT | arch-engine-realtime | immutable `BeatsPointer` snapshot | — |
| in/out | persist / restore metadata | arch-library-db | `TrackDAO` ↔ `GlobalTrackCache` | — |
| in | analysis results (beats/key/gain) | arch-analyzer | `BeatFactory` / `KeyFactory` write-back | — |
| out | cues / structure for display | arch-waveform-render | `TrackPointer` reads | — |

## Key patterns (cited, not restated)
`P-16`, `P-17`, `P-07`, `P-06` — see `kanban/patterns/`. Root house rules: `/AGENTS.md`. This context is
where the RT engine and the GUI share one aggregate; the immutable-snapshot read is what keeps it safe.
