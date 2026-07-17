---
id: arch-analyzer
type: ddd-bounded-context
title: "analyzer — off-thread beat/key/gain/waveform analysis of tracks"
owns:
  - src/analyzer/               # AnalyzerThread, TrackAnalysisScheduler, AnalyzerBeats/Key/Gain/Ebur128/Waveform, plugins/
exclude: []
thread_domain: worker
rt_safety: none
subdomain: supporting
upstream: [arch-sources-decode, arch-track-model]
downstream: [arch-track-model, arch-library-db, arch-waveform-render]
maturity: operational
fork_delta: upstream-tracking
agents_md: src/analyzer/AGENTS.md
last_audited: "2026-07-17"
---

# analyzer — bounded context

Computes a track's derived musical data. `TrackAnalysisScheduler` queues tracks and `AnalyzerThread`
runs a chain of analyzers over the decoded samples — `AnalyzerBeats` (beatgrid), `AnalyzerKey` (musical
key), `AnalyzerGain`/`AnalyzerEbur128` (loudness), `AnalyzerWaveform` (visual summary), `AnalyzerSilence`
— delegating the heavy DSP to `plugins/` (Queen Mary, KeyFinder, SoundTouch). It is pure **worker-thread**
batch work (`rt_safety: none`); results are written back into the `Track` and persisted by the library.
Pointers, never copies — `src/analyzer/` is the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `TrackAnalysisScheduler` | `analyzer/trackanalysisscheduler.cpp` | queues tracks, load-balances worker threads |
| `AnalyzerThread` | `analyzer/analyzerthread.cpp` | one worker running the analyzer chain per track |
| `AnalyzerBeats` | `analyzer/analyzerbeats.cpp` | beatgrid detection |
| `AnalyzerKey` | `analyzer/analyzerkey.cpp` | musical-key detection |
| `AnalyzerGain` / `AnalyzerEbur128` | `analyzer/analyzergain.cpp`, `analyzerebur128.cpp` | ReplayGain / EBU R128 loudness |
| `AnalyzerWaveform` | `analyzer/analyzerwaveform.cpp` | waveform summary generation |
| `AnalyzerQueenMaryBeats` | `analyzer/plugins/analyzerqueenmarybeats.cpp` | Queen Mary DSP beat plugin |
| `AnalyzerKeyFinder` | `analyzer/plugins/analyzerkeyfinder.cpp` | KeyFinder key-detection plugin |

## Invariants (an agent MUST respect these)
- **Worker-thread only (`P-17`):** analysis never touches the audio callback; it consumes decoded
  samples on its own threads and hands results back off the RT path.
- **Results flow into the canonical Track (`P-07`):** analyzers write beats/key/gain into the `Track`
  aggregate (via `BeatFactory`/`KeyFactory`), which is the source of truth — not a private side store.
- **Fail loud (`AP-16`):** an analysis failure is surfaced/logged, not silently discarded as a
  zero-length or empty result that masquerades as success.
- **A speedup must not change the result contract (`AP-02`):** DSP perf work keeps the detected
  beatgrid/key stable (or is validated against a golden), not just faster.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `analysis` | offline beat/key/gain/waveform compute | the "analysis" library feature view (arch-library-db) |
| `beats` | detected beatgrid written to a `Track` | an engine beat tick (arch-engine-realtime) |
| `gain` | computed ReplayGain/loudness | an engine channel gain control |
| `plugin` | a DSP analyzer backend (`plugins/`) | an effects backend (arch-effects-chain) |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| in | decoded samples | arch-sources-decode | `SoundSourceProxy` on the analyzer thread | — |
| out | beats / key / gain results | arch-track-model | `BeatFactory` / `KeyFactory` write-back | — |
| out | waveform summary | arch-waveform-render | `AnalyzerWaveform` → `Waveform` data | — |
| in/out | scheduling / persistence | arch-library-db | scheduler pulls rows, `AnalysisDAO` stores | — |

## Key patterns (cited, not restated)
`P-17`, `P-07`, `AP-16`, `AP-02` — see `kanban/patterns/`. Root house rules: `/AGENTS.md`. Analysis is
worker-batch by design; its only RT-relevant output is the beatgrid the engine later reads immutably.
