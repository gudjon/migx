---
id: arch-engine-realtime
type: ddd-bounded-context
title: "engine-realtime — the real-time audio processing graph"
owns:
  - src/engine/                 # EngineMixer, EngineBuffer, channels/, bufferscalers/, cachingreader/, filters/, controls/, sidechain/
  - src/engine/sync/            # EngineSync, InternalClock, Syncable — beat/tempo sync authority
exclude:
  - src/engine/effects/         # → arch-effects-chain
thread_domain: rt-audio
rt_safety: hard
subdomain: core
upstream: [arch-audio-io, arch-control-messaging, arch-sources-decode]
downstream: [arch-audio-io, arch-waveform-render, arch-vinylcontrol]
maturity: hardened
fork_delta: upstream-tracking
agents_md: src/engine/AGENTS.md
last_audited: "2026-07-17"
---

# engine-realtime — bounded context

The per-buffer audio processing graph: it pulls decoded samples, applies rate/scratch/keylock scaling,
mixes channels through gain/EQ/crossfader, and produces the master buffer the sound device consumes.
Everything reachable from its `process*()` methods runs on the **real-time audio callback thread** and
is `rt_safety: hard`. Pointers, never copies — `src/engine/` is the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `EngineMixer` | `engine/enginemixer.cpp` | top of the per-buffer process graph; owns master/headphone mix |
| `EngineBuffer` | `engine/enginebuffer.cpp` | per-deck playback, rate, scratch, keylock, slip state |
| `EngineChannel` | `engine/channels/` | a deck / sampler / mic / aux bus node |
| `EngineSync` | `engine/sync/enginesync.cpp` | master-clock / beat-sync authority (single master) |
| `EngineWorkerScheduler` | `engine/engineworkerscheduler.cpp` | dispatches off-RT-thread work (e.g. cachingreader) |
| `ReadAheadManager` | `engine/readaheadmanager.cpp` | feeds samples to the scalers ahead of playback |
| bufferscalers/ | `engine/bufferscalers/` | time-stretch / pitch (RubberBand, Soundtouch) |

## Invariants (an agent MUST respect these)
- **RT boundary (hard, `P-02`/`AP-02`):** `process()`-reachable code allocates nothing, locks nothing,
  does no I/O, does not block. Cross-thread out = lock-free ring (`util/fifo.h`) / atomic double-buffer
  / `ControlObject` (`P-16`). Object lifetime happens off this thread (`P-17`).
- **Qt affinity (`P-20`/`AP-14`):** may *emit* Qt signals; must never *receive* one synchronously or
  mutate a GUI QObject on the audio thread.
- **Single sync master (`P-06`):** exactly one `Syncable` is master at a time; `EngineSync` owns the election.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `buffer` | one audio callback's frame block (`CSAMPLE*`) | library "track buffer" (arch-library-db) |
| `channel` | an `EngineChannel` (deck/sampler/mic/aux) | an audio-interface channel (arch-audio-io) |
| `rate` | playback speed ratio incl. tempo + scratch | MIDI "rate" control input (arch-controllers-mapping) |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| in | `[ChannelN],*` control values | arch-control-messaging | ControlObject atomics | boundaries/control-to-engine.md |
| in | decoded sample blocks | arch-sources-decode | cachingreader + worker scheduler | — |
| out | mixed master `CSAMPLE` buffer | arch-audio-io | `SoundManager` callback | boundaries/engine-to-soundio.md |
| out | play position / waveform taps | arch-waveform-render | `VisualPlayPosition`, lock-free | boundaries/engine-to-waveform.md |

## Key patterns (cited, not restated)
`P-02`, `P-16`, `P-17`, `P-18`, `P-20`, `P-06` — see `kanban/patterns/`. Root house rules: `/AGENTS.md`.
North-star perf work here (M4 DSP) is governed by `P-03`/`P-18` benchmark contracts.
