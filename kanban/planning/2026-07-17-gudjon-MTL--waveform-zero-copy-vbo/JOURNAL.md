# Journal

*Round-by-round narrative. Git holds chronology; this holds the "why we turned here."*

## 2026-07-17 — Wave 1-3 (implement + measure, single loop)
- **Did:** Implemented the persistent VBO in the `rendergraph_gl` backend
  (`basegeometrynode.{h,cpp}`): lazy `glGenBuffers`; upload via `glBufferData`(orphan)+`glBufferSubData`
  **only when dirty or size-changed**; bind attributes with `setAttributeBuffer` (byte offset into VBO)
  instead of `setAttributeArray` (client pointer); unbind after draw; destructor frees the buffer only
  with a current context. Wired `GeometryNode::markDirtyGeometry()` (was a no-op) to set the dirty flag.
  Added `BM_WaveformVboUpload` to the bench. Built green (`mixxx-test`, arm64 RelWithDebInfo).
- **Measured:**
  - Correctness — `ctest -R 'Waveform|Engine'` **165/165 pass** (incl. offscreen `ControllerRendering`).
  - CPU non-regression — `BM_WaveformRGBPreprocess` p50 39.3µs, floor 28.1µs = **unchanged vs EVD-0001**
    (change is in `render()`, which the `preprocess()`-only bench doesn't touch).
  - The win — `BM_WaveformVboUpload` (`cocoa` GL): one 450 KB per-frame upload = **~6.5µs floor / ~7µs
    p50** render-thread cost. That is the cost the VBO **eliminates for every unchanged frame** (zero
    upload; draws from GPU memory). Recorded as `EVD-0002`.
- **Decided:**
  - Dirty-tracking is safe because every geometry-mutating renderer already calls `markDirtyGeometry()`
    (audited 12/12) — the SAME `DirtyGeometry` contract the scenegraph backend already relies on. So the
    GL backend now *matches* the scenegraph contract rather than inventing a new one. (confidence high)
  - Attempted the offscreen-GL measurement the baseline had DEFERRED (Phase B). `offscreen` QPA can't
    create a GL context on macOS (`createPlatformOpenGLContext` unsupported) → measured under `cocoa`
    (reversible, confidence ≥ 0.4). The bench SkipsWithError honestly under `offscreen`.
  - Timed the CPU-submission cost (no in-loop `glFinish`) not upload+sync latency — `glFinish` inflated
    p50 to ~230µs (sync round-trip), which misrepresents render-thread occupancy; the honest
    render-thread number is ~7µs.
- **Honest limits (P-01):** active scrubbing still uploads every frame (win there = explicit-orphan vs
  implicit client-copy, not isolated); end-to-end frame time + **visual correctness** need the GUI and
  are **not** measured headless. State = **mergeable-pending-GUI-check**. Nothing committed.
- **Next:** human GUI verification (scrub/zoom/pause/multi-deck/split-stereo look correct) → then seal
  at `91-LOOP-CLOSURE` `met`/`partial` with EVD-0002 cited; consider promoting the "GL backend now
  honors DirtyGeometry like scenegraph" learning into an in-code annotation / P-22 note.
