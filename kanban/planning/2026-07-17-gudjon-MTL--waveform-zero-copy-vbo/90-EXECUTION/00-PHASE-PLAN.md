# Execution — phase plan

*Ordered waves; each ends at a verifiability gate. Commit per wave (facilitator commits — this run left
the tree uncommitted for review).*

## Waves

| # | Wave | Deliverable | Verifiability gate |
|---|---|---|---|
| 1 | Implement persistent VBO | `basegeometrynode.{h,cpp}`: lazy GL buffer, dirty-tracked upload, `setAttributeBuffer` draw; `geometrynode.cpp` wires `markDirtyGeometry()` → dirty flag | `cmake --build build --target mixxx-test` green |
| 2 | Correctness gate | no behavioural regression in the render/engine tests | `ctest -R 'Waveform\|Engine'` 100% green (165/165) |
| 3 | Measure the win | `BM_WaveformVboUpload` GL upload bench + re-run `BM_Waveform`; record `EVD-0002` vs `EVD-0001` | CPU rebuild unchanged vs EVD-0001; eliminated upload cost measured > 0 |
| 4 | Honest state + seal | flag what needs GUI verification; score bet at `91-LOOP-CLOSURE` | mergeable-pending-GUI stated honestly (`P-01`); no green-over-red |

## Gate definitions
- **Wave 1 gate:** `cmake --build build --target mixxx-test --parallel 10` → exit 0. ✅ (only the ld
  alignment warning, pre-existing/unrelated).
- **Wave 2 gate:** `ctest --test-dir build -R 'Waveform|Engine' --output-on-failure` → `100% tests
  passed ... out of 165`. ✅ (includes `ControllerRenderingEngineTest`, which renders offscreen.)
- **Wave 3 gate:** `BM_WaveformRGBPreprocess` p50 within noise of EVD-0001 (~39µs floor). ✅ (p50 39.3µs).
  `BM_WaveformVboUpload` (`QT_QPA_PLATFORM=cocoa`) reports a per-frame upload cost > 0. ✅ (~6.5µs floor
  / ~7µs p50 for 450 KB). Under `offscreen` QPA the bench **skips honestly** (no GL context) — recorded.
- **Wave 4 gate:** the dossier states plainly that visual correctness + end-to-end frame time need human
  GUI verification before merge; no unmeasured win is claimed.

## House-physics guardrails (apply every wave — MG-6)
- **RT audio (`P-02`):** untouched. The change is entirely in the `rendergraph_gl` render path; no
  allocation/lock added to any `process()`/audio callback. The `pat-02-rt-no-alloc` / `pat-21` lines
  are respected: GPU buffer work stays on the render thread, off the audio deadline.
- **GL resource lifetime:** VBO created lazily in `render()` (context current), deleted in
  `~BaseGeometryNode()` only if `QOpenGLContext::currentContext()` (else the context teardown already
  reclaimed it) — no leak, no delete-without-context UB.
- **Abstraction respected:** the SceneGraph backend is untouched; the GL backend now honors the same
  `markDirtyGeometry()` (DirtyGeometry) contract the scenegraph backend already requires — the two
  backends become *more* consistent, not less.
- `pre-commit run --all-files` (clang-format/tidy) — to run at commit time by the facilitator.

## Rollback
Three files touched (`basegeometrynode.h`, `basegeometrynode.cpp`, `geometrynode.cpp`) + one bench file
(`waveformrenderbenchmark.cpp`). Revert those to HEAD `e099d24ac8` to back out; no schema/state/API
surface changed.

## Loop discipline
Fork resolved this run: attempted the offscreen-GL measurement rather than deferring it (baseline had
deferred Phase B). `offscreen` QPA can't make a GL context on macOS → measured under `cocoa` instead
(confidence ≥ 0.4, reversible). Recorded in JOURNAL.
