---
id: arch-waveform-render
type: ddd-bounded-context
title: "waveform-render — display-clock waveform drawing off a lock-free engine tap"
owns:
  - src/waveform/               # WaveformWidgetFactory, VisualPlayPosition, VSyncThread, renderers/, widgets/, Waveform
exclude: []
thread_domain: gpu-render
rt_safety: soft
subdomain: supporting
upstream: [arch-engine-realtime, arch-track-model, arch-analyzer, arch-rendergraph]
downstream: [arch-skin-widgets, arch-qml-ui]
maturity: developing
fork_delta: migx-divergent
agents_md: src/waveform/AGENTS.md
last_audited: "2026-07-17"
---

# waveform-render — bounded context

Draws the scrolling waveforms and overviews. `WaveformWidgetFactory` builds the per-deck renderer stack,
`VSyncThread` paces redraws on the **display clock**, and each frame reads the current playhead from
`VisualPlayPosition` — a lock-free `ControlValueAtomic<VisualPlayPositionData>` the engine writes and
the renderer samples without ever touching the audio thread. It renders on the GPU/display path
(`rt_safety: soft`: it must not block, but it is *not* on the audio deadline). Waveform pixel/summary
data comes from arch-analyzer; the low-level scene primitives come from arch-rendergraph. Pointers,
never copies — `src/waveform/` is the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `WaveformWidgetFactory` | `waveform/waveformwidgetfactory.cpp` | builds/owns per-deck waveform widgets + renderers |
| `VisualPlayPosition` | `waveform/visualplayposition.cpp` | lock-free engine→render playhead tap (`ControlValueAtomic<VisualPlayPositionData>`) |
| `VSyncThread` | `waveform/vsyncthread.cpp` | display-clock redraw pacing |
| `Waveform` | `waveform/waveform.cpp` | the per-track waveform summary data |
| `VisualsManager` | `waveform/visualsmanager.cpp` | registry of visual objects per channel |
| `WaveformRenderer` | `waveform/renderers/allshader/waveformrenderer.cpp` | RHI/shader signal renderer |
| `WaveformRendererRGB` | `waveform/renderers/allshader/waveformrendererrgb.cpp` | RGB signal renderer |
| `WaveformRenderMark` | `waveform/renderers/allshader/waveformrendermark.cpp` | cue/mark overlay renderer |

## Invariants (an agent MUST respect these)
- **GPU/waveform work never gates the audio deadline (`P-21`/`AP-02`):** the render path is independent
  of the callback; a slow frame drops visuals, it must never stall or feed back into `process()`.
- **The engine tap is read-only and lock-free (`P-16`):** the renderer *reads* `VisualPlayPosition`; it
  never writes engine state or takes a lock the audio thread could contend.
- **Redraw on the display clock, not the audio period (`P-23`):** frames are paced by `VSyncThread`/the
  display refresh, never triggered per audio buffer.
- **Waveform data stays in GPU buffers across frames (`P-22`/`AP-12`):** upload once; do not re-copy the
  summary CPU→GPU every frame in the hot path.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `waveform` | the on-screen signal drawing + its data | the raw audio `CSAMPLE` buffer (arch-engine-realtime) |
| `play position` | `VisualPlayPositionData` sampled for draw | the engine's authoritative play position control |
| `renderer` | a `Waveform*Renderer` draw stage | a `rendergraph` node/material (arch-rendergraph) |
| `vsync` | display-refresh redraw pacing | audio sample-rate / buffer period |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| in | playhead / visual state | arch-engine-realtime | `VisualPlayPosition` lock-free atomic | boundaries/engine-to-waveform.md |
| in | waveform summary data | arch-analyzer | `Waveform` / `AnalyzerWaveform` output | — |
| in | scene primitives / shaders | arch-rendergraph | geometry + material nodes | — |
| out | embedded waveform widgets | arch-skin-widgets, arch-qml-ui | `WWaveformViewer` / `QmlWaveformDisplay` | — |

## Key patterns (cited, not restated)
`P-21`, `P-22`, `P-23`, `AP-12`, `P-16`, `AP-02` — see `kanban/patterns/`. Root house rules: `/AGENTS.md`.
The lock-free `VisualPlayPosition` tap is the canonical example of reading engine state without the RT lock.
