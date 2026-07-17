# Problem

## What's wrong today
The waveform GL backend (`src/rendergraph/opengl/backend/basegeometrynode.cpp`) now draws from a
persistent VBO (landed by the sibling dossier `2026-07-17-gudjon-MTL--waveform-zero-copy-vbo`, merged at
HEAD `5a8f9626e4`): `render()` re-uploads the vertex buffer only when `m_geometryDirty` is set or the
byte size changed (`basegeometrynode.cpp:110-125`). That optimization measured and closed the
**steady-state** case — an unchanged frame does zero upload (`EVD-0002`).

But every `allshader` renderer's `preprocess()` calls `markDirtyGeometry()` **unconditionally** whenever
it rebuilds — e.g. `src/waveform/renderers/allshader/waveformrendererrgb.cpp:126-127`
(`geometry().allocate(reserved); markDirtyGeometry();` inside `preprocessInner()`, called every time the
displayed window moves). During **active scrubbing or a seek**, the displayed window changes every
frame, so `preprocessInner()` runs and marks dirty every frame, so `basegeometrynode.cpp`'s dirty branch
(`basegeometrynode.cpp:110-123`: `glBufferData` orphan + `glBufferSubData`, or a full reallocating
`glBufferData` on size change) executes on **every** frame in this regime — not the zero-upload path.

`EVD-0002` (`kanban/planning/2026-07-17-gudjon-MTL--waveform-zero-copy-vbo/results/EVD-0002.md`, "What is
NOT measured", point 1) says this plainly: *"Active scrubbing/playback rebuilds + marks dirty every
frame, so the VBO still uploads every frame there; the win in that regime is the (driver-dependent,
likely modest but ≥0) difference between an explicit orphaned DYNAMIC_DRAW upload and the old implicit
client-array copy — not isolated here."* That gap was never closed.

The benchmark suite has the same gap structurally: `src/test/waveformrenderbenchmark.cpp`'s
`BM_WaveformRGBPreprocess`/`BM_WaveformFilteredPreprocess` (`waveformrenderbenchmark.cpp:191-219`) sweep
scrub positions via `runScrub()` (`waveformrenderbenchmark.cpp:113-189`) but measure **only** the
CPU-side `preprocess()` call — no GL context is opened, so the mandatory VBO re-upload the real
`render()` would perform on that same dirty frame is never charged. `BM_WaveformVboUpload`
(`waveformrenderbenchmark.cpp:256-361`) measures the GPU upload in isolation — a fixed-size synthetic
buffer uploaded repeatedly, decoupled from any scrub position or CPU rebuild. **No benchmark today drives
the combined, continuous-dirty per-frame cost (CPU rebuild + mandatory GPU re-upload) that a real scrub
or seek gesture produces.**

## Who feels it
A DJ actively scrubbing or seeking a loaded waveform (jog wheel drag, needle-drop click, a fast preview
scrub across a track) on an M4 MacBook, especially with multiple decks/overview waveforms visible: this
is the regime where the render thread does the **most** work per frame (full CPU rebuild + full VBO
re-upload, back to back, every vsync), and it is the regime the existing optimization dossier explicitly
did not measure or improve.

## What "done" means (the bet)
1. **The problem is real** — `EVD-0002`'s own "not measured" caveat (point 1) plus the code path cited
   above (`waveformrendererrgb.cpp:127`, `basegeometrynode.cpp:110-125`): a combined-regime benchmark
   does not exist, so there is no number to know whether this regime is a bottleneck at all.
2. **The approach works** — wave 1 builds the missing benchmark and captures a pinned baseline
   (`EVD-0003`); wave 2 is a targeted optimization of the mandatory re-upload path (candidate: replace
   the orphan-`glBufferData` + `glBufferSubData` pair at `basegeometrynode.cpp:118-123` with a
   driver-friendlier update strategy for the "always dirty, same size" case — e.g. explicit unsynchronized
   mapping — decided in `02-ARCHITECTURE` once `EVD-0003` shows whether the upload or the CPU rebuild
   dominates this regime).
3. **The gates catch failure** — the extended `waveformrenderbenchmark.cpp` case
   (p99/max vs `EVD-0003`, zero frames over the 120 Hz budget) plus `ctest -R 'Waveform|Engine'`.

## Non-goals
- Re-litigating or reopening the steady-state (idle/unchanged-frame) VBO win — that is
  `2026-07-17-gudjon-MTL--waveform-zero-copy-vbo` / `PS-MTL-02`, already closed on that scope.
- Adopting the SceneGraph + Metal RHI backend (gated on offscreen-render-on-Metal, per `EVD-0001`).
- Any change to the audio engine or `process()` path — this is entirely render-thread scope.
- Claiming an end-to-end GUI/composited frame-time number — headless measurement is the CPU rebuild +
  GL upload cost; visual/end-to-end verification (if a change lands) needs a human, same limit as
  `EVD-0002`.

## Inheritance
- `P-22` zero-copy-gpu-waveform, `AP-12` gpu-cpu-copy-in-render-hot-path — the same pattern/antipattern
  pair the sibling dossier resolved for steady-state; this dossier addresses the regime where the copy
  is *unavoidable* every frame, so the lever is the cost of that copy, not skipping it.
- `P-21` metal-offload-must-not-gate-audio, `P-23` render-on-display-clock-not-audio-clock — this stays
  render-thread only; `P-02` RT-safety is preserved by construction (no touch to `src/engine/`).
- `P-03`/`P-18`/`P-25` — benchmark-as-contract, p99/max not mean, pin the baseline commit + M4 core
  config.
- Baseline dossier `2026-07-17-gudjon-MTL--waveform-render-baseline` (`EVD-0001`, sealed) and sibling
  `2026-07-17-gudjon-MTL--waveform-zero-copy-vbo` (`EVD-0002`, open/unsealed) — both direct inputs;
  `ADR-002` (TRUE HARD FORK) authorizes changing the render code in place.
