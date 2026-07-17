# Waveform zero-copy VBO — dossier front page

**Prefix:** MTL · **Initiative:** initiative-apple-silicon · **Facilitator:** gudjon · **Phase:** execution
(mergeable-pending-GUI) · **Baseline:** `EVD-0001` (baseline dossier)

## Scope
The FIRST optimization fed by the waveform-render baseline dossier. Replace the `rendergraph_gl` GL
backend's per-draw **client-memory** vertex bind (`basegeometrynode.cpp:89-102` — `setAttributeArray` →
`glDrawArrays` copies the whole vertex buffer CPU→GPU every draw, `AP-12`) with a **persistent VBO**:
upload once, re-upload only when the geometry is marked dirty, draw from GPU memory. An unchanged frame
does **zero** upload (`P-22` zero-copy). This is copy-map **lever 1**; lever 2 (SceneGraph + Metal RHI)
is out of scope.

## Success criteria
1. GL backend draws from a persistent VBO; unchanged frame → zero CPU→GPU upload. ✅ (by construction)
2. Eliminated per-frame upload cost measured > 0 vs EVD-0001. ✅ `EVD-0002`: ~6.5µs floor / ~7µs p50 for
   the 450 KB reference-scene buffer, per deck.
3. No correctness regression: `ctest -R 'Waveform|Engine'` green; `BM_Waveform` CPU rebuild unchanged. ✅
   165/165 tests pass; RGB rebuild p50 39.3µs (matches EVD-0001).
4. Visual correctness + end-to-end frame time verified in the GUI. ⚠️ **NOT DONE — needs a human.**

## Current status
**Implemented, builds green, unit-tested, benchmarked. MERGEABLE-PENDING-GUI-CHECK.** The working tree
holds the change (4 files); **not committed** — the facilitator reviews + commits. Headless measurement
cannot see the actual pixels or the composited frame, so a human must confirm the waveform still draws
correctly (scrub, zoom, pause, multi-deck, split-stereo) before merge.

### Files changed (working tree, HEAD `e099d24ac8`)
- `src/rendergraph/opengl/backend/basegeometrynode.h` — VBO state + dirty flag + destructor.
- `src/rendergraph/opengl/backend/basegeometrynode.cpp` — persistent-VBO upload/draw in `render()`.
- `src/rendergraph/opengl/geometrynode.cpp` — `markDirtyGeometry()` drives the dirty flag (was a no-op).
- `src/test/waveformrenderbenchmark.cpp` — `BM_WaveformVboUpload` (offscreen GL upload bench).

## Map
`00-FOUNDATION/PROBLEM.md` · `00-FOUNDATION/PS-MTL-02.md` · `90-EXECUTION/00-PHASE-PLAN.md` ·
`results/EVD-0002.md` · `JOURNAL.md`. Seal at `91-LOOP-CLOSURE/` after GUI verification.
