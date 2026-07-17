---
id: PS-MTL-02
type: problem-statement
title: "Waveform GL backend re-copies the whole vertex buffer CPU→GPU every draw (no VBO)"
status: open              # open | resolved | superseded | wont-fix
severity: MUST            # MUST | SHOULD | MAY
ears_class: event-driven  # ubiquitous | state-driven | event-driven | optional | unwanted | complex
dossier: 2026-07-17-gudjon-MTL--waveform-zero-copy-vbo
prefix: MTL
resolves: [P-22]          # zero-copy-gpu-waveform
risks: [AP-12]            # gpu-cpu-copy-in-render-hot-path
related: [PS-MTL-01]      # the baseline dossier's PS (EVD-0001)
acceptance:
  - "The rendergraph_gl BaseGeometryNode draws from a persistent GL buffer object (VBO), not client memory: an unchanged frame (geometry not marked dirty) performs ZERO CPU→GPU vertex upload. Measured eliminated per-frame upload cost > 0 on a render benchmark (BM_WaveformVboUpload) vs the EVD-0001 baseline path."
  - "No correctness regression: ctest -R 'Waveform|Engine' stays 100% green; the CPU vertex-rebuild cost (BM_WaveformRGBPreprocess) is unchanged vs EVD-0001 (~39µs floor)."
verified_against_code: "2026-07-17 / HEAD e099d24ac8 (src/rendergraph/opengl/backend/basegeometrynode.cpp:83 opened at HEAD)"
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# PS-MTL-02 — persistent VBO for the waveform GL backend (kill the per-draw copy)

**EARS statement (event-driven):**
> When the rendergraph_gl backend draws a geometry node whose vertex data has **not** changed since the
> previous frame, the system shall draw it from a persistent GPU buffer **without** re-copying the vertex
> data from client memory to the GPU.

## Context
The default QWidget-skin waveform renderer (`allshader::WaveformWidget` on the `rendergraph_gl` backend)
draws every geometry node through `rendergraph::BaseGeometryNode::render()`
(`src/rendergraph/opengl/backend/basegeometrynode.cpp`). At HEAD that method binds **client memory**:

```
shader.setAttributeArray(location, geometry.vertexDataAs<float>() + off, tupleSize, sizeOfVertex);
...
glDrawArrays(mode, 0, geometry.vertexCount());
```

With a client-side attribute array bound (no VBO), the driver must copy the **entire** vertex buffer
CPU→GPU on **every** `glDrawArrays` — every vsync, per deck, whether or not the waveform changed
(`AP-12`, `COPY-MAP.md` step 2). On Apple's OpenGL-on-Metal this marshaling is pure overhead. The
common idle case — a loaded but paused deck, or a static display window — still redraws every vsync and
pays this copy for a buffer it already uploaded last frame.

- **Baseline:** `EVD-0001` (baseline dossier) — the CPU vertex rebuild that *feeds* this draw is
  ~39µs floor / ~45µs p50 per frame per deck; the per-draw GPU copy it feeds is the `P-22` target here.
- **Frame's vertex buffer at the reference scene** (1920×200 Retina deck, DPR 2.0, default zoom):
  ~23 046 vertices × 20 B = **~450 KB re-copied per frame per deck** on the old path.

## Acceptance contract (how the loop closes)
- **Benchmark / test:**
  - `build/mixxx-test --benchmark --benchmark_filter=BM_WaveformVboUpload` (needs a GL context;
    `QT_QPA_PLATFORM=cocoa`) — times the CPU-side per-frame upload the VBO path eliminates for an
    unchanged frame. Recorded in `results/EVD-0002.md`.
  - `build/mixxx-test --benchmark --benchmark_filter=BM_Waveform` — CPU rebuild must be unchanged vs
    EVD-0001 (the backend change must not touch the CPU preprocess).
  - `ctest --test-dir build -R 'Waveform|Engine'` — correctness gate.
- **Baseline:** `EVD-0001` (~39µs floor CPU rebuild; the ~450 KB/frame client-array copy it feeds).
- **Threshold:** unchanged frame → 0 uploads (structural); eliminated per-frame CPU upload cost
  measurably > 0 (EVD-0002 records ~6.5µs floor / ~7µs p50 for the 450 KB buffer); no correctness
  regression; CPU rebuild unchanged.
- **Guard:** render thread only — no allocation/lock added to the RT audio path (`P-02`); GPU work
  stays off the audio deadline (`P-21`). The VBO is created/updated/destroyed only with a current GL
  context on the render thread.

## Out of scope
- Making the CPU vertex rebuild itself incremental / SIMD / dirty-region (that is the *other* lever in
  `COPY-MAP.md` step 1 — a separate PS). This PS only removes the redundant GPU copy.
- Adopting the SceneGraph/Metal RHI backend (`COPY-MAP.md` lever 2) — gated on offscreen-render-on-Metal.
- End-to-end GPU frame-time (upload + shade + draw + composite) — needs the GUI; flagged for human
  verification, not claimed here.
