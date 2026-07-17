# AGENTS.md — waveform/ (display-clock waveform drawing off a lock-free engine tap)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-waveform-render.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
Draws the scrolling waveforms and overviews. `WaveformWidgetFactory` builds the per-deck renderer stack,
`VSyncThread` paces redraws on the **display clock**, and each frame reads the playhead from
`VisualPlayPosition` — a lock-free `ControlValueAtomic<VisualPlayPositionData>` the engine writes and the
renderer samples without touching the audio thread. Renders on the GPU/display path (must not block, but
is *not* on the audio deadline).

## Key files
- `waveformwidgetfactory.cpp/.h` — builds/owns per-deck waveform widgets + renderers.
- `visualplayposition.cpp/.h` — the lock-free engine→render playhead tap
  (`ControlValueAtomic<VisualPlayPositionData>` in `visualplayposition.h`).
- `vsyncthread.cpp/.h` — display-clock redraw pacing; `visualsmanager.cpp` — per-channel visual registry.
- `waveform.cpp/.h` — the per-track waveform summary data.
- `renderers/allshader/` — `waveformrenderer.cpp`, `waveformrendererrgb.cpp`, `waveformrendermark.cpp`, …
  (RHI/shader draw stages). `widgets/` — the hosting waveform widgets.

## Invariants you MUST respect
- **GPU/waveform work never gates the audio deadline:** the render path is independent of the callback;
  a slow frame drops visuals, it must never stall or feed back into `process()`. `P-21`, `AP-02`.
- **The engine tap is read-only and lock-free:** the renderer *reads* `VisualPlayPosition`; it never
  writes engine state or takes a lock the audio thread could contend. `P-16`.
- **Redraw on the display clock, not the audio period:** frames are paced by `VSyncThread`/display
  refresh, never triggered per audio buffer. `P-23`.
- **Waveform data stays in GPU buffers across frames:** upload once; no per-frame CPU→GPU re-copy of the
  summary in the hot path. `P-22`, `AP-12`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R Waveform` (GoogleTest; `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Blocking on, or synchronizing the render path with, the audio callback (`P-21`, `AP-02`).
- Writing engine state (or taking an RT-contended lock) from a renderer instead of reading the tap (`P-16`).
- Re-uploading waveform summary CPU→GPU every frame in the draw hot path (`P-22`, `AP-12`).

## Cross-references
Upstream: `src/engine/AGENTS.md` (`VisualPlayPosition` tap), `src/analyzer/AGENTS.md` (summary data),
`src/rendergraph/AGENTS.md` (scene primitives). Downstream: `src/skin/AGENTS.md`, `src/qml/AGENTS.md`.
Seam: `kanban/architecture/ddd/boundaries/engine-to-waveform.md`. Card:
`kanban/architecture/ddd/bounded-contexts/arch-waveform-render.md`.
