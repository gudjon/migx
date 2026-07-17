# Research

*Prior art and the current-reality map for the M4 waveform render path. Grounded in code at HEAD
(2026-07-17). Baseline numbers themselves are captured during execution (`90-EXECUTION`), not here.*

## The render path today (code map)
- **`src/waveform/waveformwidgetfactory.cpp`** — chooses the waveform widget/renderer *type* at
  runtime (GL, Qt-painter, and the modern **`renderers/allshader/`** path built on `src/rendergraph/`).
- **`src/rendergraph/`** — a rendering abstraction with two backends: **`opengl/`** (legacy) and
  **`scenegraph/`** (Qt Quick SceneGraph, which drives **QRhi** → Metal on macOS). `README` + `common/`
  hold the shared node/material model.
- **`src/waveform/visualplayposition.h`** — the engine→render tap: a lock-free
  `ControlValueAtomic<VisualPlayPositionData>` written by `EngineBuffer`, read at draw time (`P-16`).
- **`src/waveform/guitick.cpp` + `vsyncthread.cpp`** — the display-clock tick that drives redraw,
  decoupled from the audio buffer period (`P-23`).

## The key finding (the lead for the whole MTL workstream)
**`src/coreservices.cpp:826` calls `QQuickWindow::setGraphicsApi(QSGRendererInterface::OpenGL)`** — Migx
**forces the Qt SceneGraph/QML backend to OpenGL**. On Apple Silicon, OpenGL is deprecated and runs on a
compatibility/emulation layer, so the modern `allshader`/scenegraph waveform path is **not** going
through Metal today. This is almost certainly the largest single Apple-Silicon rendering opportunity —
but it is an *optimization* for a later MTL dossier; **this dossier only measures the current
(OpenGL-forced) baseline** so that switch has a number to beat.

## Open questions for execution
1. What is the current waveform redraw frame-time distribution (p50/p99/max) + dropped-frame count on
   this M4, under a realistic scrubbing scene, with the default `allshader` renderer?
2. Confirm the backend actually in use at runtime (OpenGL, per the `setGraphicsApi` call) and the Qt
   version.
3. Where on the render path do per-frame CPU↔GPU copies happen (`AP-12`) — texture uploads of waveform
   data, mark/label geometry rebuilds? (Input a future zero-copy MTL dossier needs — `P-22`.)

## Benchmark prior art (reuse, don't invent — `P-03`)
`benchmark::benchmark` is already linked and used in the test tree — e.g. `src/test/sampleutiltest.cpp`,
`ringdelaybuffer_test.cpp`, `engineeffectsdelay_test.cpp`, `movinginterquartilemean_test.cpp`. The
waveform-render benchmark should follow those patterns and run via `ctest`/the bench binary. Frame-time
measurement may need a headless/offscreen render loop driving the renderer over N frames.

## Upstream (Mixxx)
The `allshader` + `rendergraph` refactor is upstream Mixxx's own modernization of the waveform stack;
track its direction (`fork_delta`) rather than diverging gratuitously. The `setGraphicsApi(OpenGL)` pin
is worth checking against upstream intent — it may be a portability default we can safely override on
macOS. Upstream is independently porting renderers off OpenGL onto RHI/SceneGraph (issues #14990,
#13385, #14407, #11761 — see `kanban/knowledge/upstream-issues-m4-features.md`); **pull those rather
than re-implement.**

## Execution-surface findings (prep round, 2026-07-17 — grounded at file:line)

The concrete map for execution. **The backend is chosen at COMPILE time**, which reframes the target:
- `CMakeLists.txt:5363-5384` — `mixxx-lib` (QWidget skins, the default) always links **`rendergraph_gl`**
  (custom QOpenGL backend); `mixxx-qml-lib` links `rendergraph_sg` (real QtQuick SceneGraph) only `if(QML)`.
- `src/coreservices.cpp:823-827` — forces `QQuickWindow::setGraphicsApi(OpenGL)` (comment pins *why*:
  offscreen/controller-preview rendering currently depends on GL). So Metal RHI is never selected, even
  for the QML path.
- **The default renderer to benchmark:** `WaveformWidgetFactory` → `AllShader` backend
  (`waveformwidgetfactory.cpp:1345-1357`, RGB type default `:417`) → `allshader::WaveformWidget::render()`
  (`src/waveform/widgets/allshader/waveformwidget.cpp:142-165`). Frame entry: `WaveformWidgetFactory::render()`
  → `renderSelf()` (`:817-889`). Display clock: `vsyncthread.cpp` (`ST_PLL` on Apple, `:11-17`).
- **The real per-frame cost + the `AP-12`/`P-22` violation (the optimization target):**
  `Engine::preprocess()` (`src/rendergraph/opengl/engine.cpp:71-77`) runs every vsync and rebuilds the
  ENTIRE vertex buffer via scalar CPU loops in `waveformrenderer{filtered,rgb,hsv}.cpp preprocessInner()`
  (e.g. `waveformrendererfiltered.cpp:36-201`), then `basegeometrynode.cpp:83-102` binds **client-side
  memory** (`setAttributeArray(... geometry.vertexDataAs<float>() ...)`) → `glDrawArrays` copies the whole
  CPU buffer to the GPU **every frame** — no VBOs. The SceneGraph backend (`scenegraph/backend/basegeometrynode.h`,
  `= QSGGeometryNode`) already uses GPU buffers. Mark/label textures are cached, not per-frame
  (`waveformrendermark.cpp:551-599`).
- **Benchmark harness:** google-benchmark macros live inside gtest `.cpp` (`src/test/sampleutiltest.cpp:469-515`
  pattern), built into `mixxx-test`, run via `mixxx-test --benchmark [--benchmark_filter=BM_x]`
  (`CMakeLists.txt:3076-3086`, `src/test/main.cpp:1-41`; offscreen QPA is already the default). **No
  waveform render-bench exists** — Wave 2 builds one, modeled on the offscreen `QQuickRenderControl`
  harness in `src/test/controllerrenderingengine_test.cpp` driving `allshader::WaveformWidget` with a
  synthetic `Waveform`.

**Implication for scope:** the baseline should measure the **`rendergraph_gl` (QWidget default) path**,
because that is the one lacking GPU buffers — the biggest, most measurable Apple-Silicon win (zero-copy
VBOs + Metal). The optimization dossier that follows has two levers: (1) VBOs in the GL backend, and/or
(2) adopting the SceneGraph backend + letting Qt pick Metal (removing the forced-GL line, contingent on
the controller-preview dependency it guards).

**DSP dossier candidates surfaced (feed a future `DSP` dossier, not this one):** the recursive IIR biquad
`enginefilteriir.h:238-243` (loop-carried dependency → cannot autovectorize → the prime hand-NEON target;
2 channels = 2 lanes), `EngineBufferScaleLinear::do_scale()` (`enginebufferscalelinear.cpp:253-345`, RT
hot loop), and `SampleUtil` (`util/sample.cpp:15-30`) relying on autovectorization with alignment keyed
off `__AVX__` (meaningless on arm64 — untuned for NEON). #15192 (Soundtouch keylock CPU) and #8719
(PortAudio callback syscall audit) from the upstream survey belong there too.
