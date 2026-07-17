---
id: PS-MTL-03
type: problem-statement
title: "No benchmark or measured cost for the continuous-dirty (active-scrub/seek) waveform re-upload regime"
status: open              # open | resolved | superseded | wont-fix
severity: MUST            # MUST | SHOULD | MAY
ears_class: event-driven  # ubiquitous | state-driven | event-driven | optional | unwanted | complex
dossier: 2026-07-17-gudjon-MTL--waveform-scrub-regime
prefix: MTL
resolves: [P-22, P-03, P-18, P-25]
risks: [AP-12, AP-02]
related: [PS-MTL-01, PS-MTL-02]
acceptance:
  - "src/test/waveformrenderbenchmark.cpp gains a benchmark that drives ONE combined scrub frame end-to-end: allshader::WaveformRendererRGB::preprocess() (CPU vertex rebuild) followed by the persistent-VBO dirty re-upload path in rendergraph::BaseGeometryNode::render() (src/rendergraph/opengl/backend/basegeometrynode.cpp:110-125, glBufferData orphan + glBufferSubData) against a live offscreen GL context, sweeping scrub positions the same way runScrub() does (src/test/waveformrenderbenchmark.cpp:113-189) so every iteration is dirty (matching src/waveform/renderers/allshader/waveformrendererrgb.cpp:126-127, which calls markDirtyGeometry() unconditionally on every preprocessInner() call) -- reporting p50/p90/p99/max per combined frame, recorded as the pinned EVD-0003 baseline (commit SHA + M4 core config, per P-25)."
  - "Any wave-2 optimization of that re-upload path does not regress the combined-frame p99 vs the pinned EVD-0003 baseline, and max stays under the 120Hz frame budget (8333us) at the reference scene (1920x200 Retina deck, DPR 2.0, default zoom) -- zero frames over budget -- with ctest -R 'Waveform|Engine' 100% green (no correctness regression)."
verified_against_code: "2026-07-17 / HEAD 5a8f962 (src/rendergraph/opengl/backend/basegeometrynode.cpp:110, src/waveform/renderers/allshader/waveformrendererrgb.cpp:126, src/test/waveformrenderbenchmark.cpp:113 and :256 all opened at HEAD)"
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# PS-MTL-03 — the active-scrubbing/seek waveform re-upload regime is unmeasured and unoptimized

**EARS statement (event-driven):**
> When the displayed waveform window changes every frame (active scrubbing, a seek/needle-drop, or a
> fast preview scrub), the rendergraph_gl backend shall complete the CPU vertex rebuild and the mandatory
> persistent-VBO re-upload for that frame within a bounded p99/max, with zero frames exceeding the
> 120 Hz frame budget, and without regressing the correctness gate.

*(event-driven: "When X …" — the trigger is the continuous per-frame dirty state produced by scrubbing,
distinct from the steady-state "unchanged frame" trigger `PS-MTL-02` covers.)*

## Context
The persistent-VBO change (`PS-MTL-02`, merged at HEAD) makes `rendergraph::BaseGeometryNode::render()`
skip the upload when the geometry is **not** dirty (`src/rendergraph/opengl/backend/basegeometrynode.cpp:110`
`if (m_geometryDirty || vertexBytes != m_vboByteSize)`). But every `allshader` renderer's
`preprocessInner()` marks the geometry dirty **unconditionally** on every call it makes — e.g.
`src/waveform/renderers/allshader/waveformrendererrgb.cpp:126-127`:
```
geometry().allocate(reserved);
markDirtyGeometry();
```
During active scrubbing the displayed window (`m_firstDisplayedPosition`/`m_lastDisplayedPosition`)
moves every frame, so `preprocessInner()` reruns and re-marks dirty every frame, so `render()`'s dirty
branch (`src/rendergraph/opengl/backend/basegeometrynode.cpp:110-123`) — the orphaning `glBufferData` + `glBufferSubData` pair, or a
full reallocating `glBufferData` on a size change — executes on **every** frame in this regime. This is
exactly the regime `EVD-0002` named and explicitly did not measure:

> "Active scrubbing/playback rebuilds + marks dirty every frame, so the VBO still uploads every frame
> there; the win in that regime is the (driver-dependent, likely modest but ≥0) difference between an
> explicit orphaned DYNAMIC_DRAW upload and the old implicit client-array copy — not isolated here."
> (`kanban/planning/2026-07-17-gudjon-MTL--waveform-zero-copy-vbo/results/EVD-0002.md`, "What is NOT
> measured", point 1)

**The benchmark coverage gap, concretely:**
- `BM_WaveformRGBPreprocess` / `BM_WaveformFilteredPreprocess`
  (`src/test/waveformrenderbenchmark.cpp:191-219`, driven by `runScrub()` at
  `src/test/waveformrenderbenchmark.cpp:113-189`) already sweep scrub positions across
  `kScrubSteps = 512` steps (`src/test/waveformrenderbenchmark.cpp:57`) — but they call only
  `renderer.preprocess()`. No GL context is opened; the mandatory VBO re-upload the real `render()` call
  would perform on that same dirty frame is never charged.
- `BM_WaveformVboUpload` (`src/test/waveformrenderbenchmark.cpp:256-361`) opens an offscreen GL context
  and times exactly one upload shape (`glBufferData` orphan + `glBufferSubData` of a **fixed-size**
  synthetic buffer, `rgbFrameByteSize()` at `src/test/waveformrenderbenchmark.cpp:250-254`) repeated
  `->Iterations(4000)` times — it is decoupled from any scrub position sweep and from the CPU rebuild
  that precedes it in the real path.
- **No existing benchmark drives both halves together** (CPU rebuild that produces the vertex data, then
  the GPU re-upload of exactly that data) for a continuously-dirty scrub sweep. So there is currently no
  number for the regime a DJ is in while actively scrubbing or seeking — the regime with the most
  per-frame render-thread work.

- **Baseline inputs available to build on:** `EVD-0001` (CPU rebuild alone, clean-host enrichment:
  RGB p50 ~31.5µs / p99 ~35µs / floor ~29µs) and `EVD-0002` (GPU upload alone, ~6.5µs floor / ~7µs p50 for
  the 450 KB reference-scene buffer under `cocoa` QPA). Neither was measured together, nor across a real
  scrub sweep with a live GL context.

## Acceptance contract (how the loop closes)
- **Benchmark / test:**
  - New case in `src/test/waveformrenderbenchmark.cpp` (wave 1) — modeled on `runScrub()`
    (`src/test/waveformrenderbenchmark.cpp:113-189`) but, per iteration, opens/reuses a live offscreen GL context
    (as `BM_WaveformVboUpload` does, `src/test/waveformrenderbenchmark.cpp:261-278`), drives
    `allshader::WaveformRendererRGB::preprocess()` at the next scrub position, then performs the
    `BaseGeometryNode`-equivalent dirty re-upload of the resulting `geometry().vertexData()` into a real
    VBO. Reports p50/p90/p99/max per combined frame. Recorded in `results/EVD-0003.md`. If no GL context
    can be created in the run environment (as `offscreen` QPA cannot on macOS, `BM_WaveformVboUpload`'s
    existing honest-skip behavior), the bench must `SkipWithError` rather than fabricate a number — same
    honesty rule as `EVD-0002`.
  - `build/mixxx-test --benchmark --benchmark_filter=BM_Waveform` — the existing CPU-only benches must
    stay unchanged (non-regression check on the rebuild itself).
  - `ctest --test-dir build -R 'Waveform|Engine'` — correctness gate, must stay 100% green.
- **Baseline:** `EVD-0003` (wave 1 output) — the first pinned number for this regime; commit SHA + M4
  core config + Qt version recorded per `P-25`.
- **Threshold:** post-optimization (wave 2) combined-frame p99 ≤ `EVD-0003`'s pinned p99 (no regression);
  max stays under the 120 Hz frame budget (8333µs) at the reference scene — zero frames over budget;
  `ctest -R 'Waveform|Engine'` unchanged at 100%.
- **Guard:** the entire change stays in `src/rendergraph/opengl/backend/` and/or
  `src/waveform/renderers/allshader/` (render thread only) — no allocation/lock added to `src/engine/` or
  any `process()` path (`P-02`); GPU work stays off the audio deadline (`P-21`). Verified by diff-scope
  review and `ctest -R Engine` staying green (no behavioral change to the audio engine tests).

## Out of scope
- The steady-state (unchanged-frame, zero-upload) win — already closed by `PS-MTL-02` / `EVD-0002`.
- Making the CPU vertex rebuild itself faster/SIMD — a separate lever (`EVD-0001`'s copy-map), only
  in scope here if `EVD-0003` shows the CPU half, not the upload half, dominates this regime (a wave-2
  architecture decision, not assumed up front).
- SceneGraph/Metal RHI adoption — gated on offscreen-render-on-Metal (`EVD-0001`).
- End-to-end GUI/composited frame time and visual correctness — needs a human, same limit as `EVD-0002`.
