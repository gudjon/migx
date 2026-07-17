---
id: headless-gl-testing-cgl
type: knowledge
title: "Headless OpenGL for benchmarks/tests via CGL (no window server / GUI)"
status: active
owner: gudjon
created: "2026-07-18"
lastUpdated: "2026-07-18"
source: "src/test/waveformrenderbenchmark.cpp HeadlessGLContext; EVD-0003 (MTL scrub dossier)"
---

# Headless GL testing via CGL

**Problem it removes:** GL-dependent benchmarks/tests (`BM_WaveformVboUpload`, `BM_WaveformScrubFrame`)
used to *skip* in the CLI `mixxx-test` binary — Qt's **offscreen QPA yields no GL context**, and
`QT_QPA_PLATFORM=cocoa` from a headless/agent process hangs trying to attach to the window server. That
left the GL half of `EVD-0003` and the VBO win "GUI-blocked" — a recurring caveat.

**The fix:** create the context directly with **CGL (Core OpenGL)** instead of going through Qt's QPA.
CGL makes a real GL context with **no window-server surface**, so it runs fully headless. On this box it
binds the **real M4 GPU** (`glGetString(GL_RENDERER)` → `Apple M4`, `2.1 Metal - 90.5` — OpenGL over
Metal), so the numbers are hardware-representative, not a software fallback.

Reference impl: `HeadlessGLContext` in `src/test/waveformrenderbenchmark.cpp` —
`CGLChoosePixelFormat` (accelerated, `kCGLOGLPVersion_Legacy`; software fallback) → `CGLCreateContext`
→ `CGLSetCurrentContext`; then raw `glGenBuffers`/`glBufferData`/`glBufferSubData` from `<OpenGL/gl.h>`
(no `QOpenGLFunctions`). Guard with `#ifdef __APPLE__` + `GL_SILENCE_DEPRECATION` (Migx is macOS-only,
ADR-006; the OpenGL framework is deprecated-but-present, and `-Werror` needs the silence macro).

**Caveats:** the legacy 2.1 profile is enough for VBO upload/draw timing but not modern shaders; p99/max
carry GL-driver async jitter (no per-iteration `glFinish` — it measures render-thread occupancy), so
report p50/p90 as robust (see EVD-0003). Reuse this for any future render/GL benchmark or test that
would otherwise skip headless.
