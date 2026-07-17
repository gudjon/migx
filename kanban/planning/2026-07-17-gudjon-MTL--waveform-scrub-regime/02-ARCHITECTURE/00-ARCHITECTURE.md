# Architecture

*Written at scaffold time as the planned shape; wave 1's `EVD-0003` result decides the specific wave-2
lever (see `01-RESEARCH`'s Options table) — this section states the design skeleton and the decision
gate, not a premature commitment to one lever.*

## The design
1. **Wave 1 (measurement):** add a benchmark case to `src/test/waveformrenderbenchmark.cpp` that, per
   iteration, (a) advances the scrub position exactly as `runScrub()` does
   (`waveformrenderbenchmark.cpp:113-189`), (b) calls the real renderer's `preprocess()` to rebuild the
   vertex buffer, then (c) performs the same dirty-path GL upload `BaseGeometryNode::render()` would
   perform (`basegeometrynode.cpp:110-125`) against a live offscreen GL context (reusing the context/VBO
   setup pattern from `BM_WaveformVboUpload`, `waveformrenderbenchmark.cpp:261-296`). Reports combined
   per-frame p50/p90/p99/max. This is pure measurement — no production code changes.
2. **Wave 2 (optimization):** once `EVD-0003` shows which half (CPU rebuild vs GPU upload) dominates and
   whether the frame budget is actually at risk, apply the indicated lever from `01-RESEARCH`'s options
   table inside `src/rendergraph/opengl/backend/basegeometrynode.cpp`'s dirty branch (or, if the data
   says the regime is already comfortably under budget, close the dossier as "measured, no change
   justified" — an honest halt is a valid outcome, not a forced win, per the dossier-lifecycle rule
   against green-over-red).
3. **Wave 3 (verification):** re-run the wave-1 benchmark against the wave-2 change, compare to
   `EVD-0003`, and re-run the correctness + RT-safety gates.

## Touched subsystems & the RT/GPU boundary
- `src/rendergraph/opengl/backend/basegeometrynode.{h,cpp}` — the dirty re-upload path (wave 2, if a
  code change is indicated).
- `src/test/waveformrenderbenchmark.cpp` — new benchmark case (wave 1), test-tree only.
- **Not touched:** `src/engine/` (the RT audio path), `src/soundio/`, any `process*()` implementation.
  This dossier's entire scope is the render thread, which runs on the display clock, never the audio
  clock (`P-23`); GPU submission never gates the audio callback (`P-21`). No allocation/lock is added to
  any RT path (`P-02`) — the change, if any, is entirely GL-buffer bookkeeping inside `render()`, which
  already runs off the audio thread today.

## Patterns & decisions cited
| ID | How this design uses it |
|---|---|
| `P-22` | The target invariant (waveform data stays in GPU buffers across frames) — this dossier extends its coverage to the continuously-dirty case, where the *cost of the required update*, not skipping it, is the lever. |
| `AP-12` | The antipattern being bounded: a per-frame GPU↔CPU copy in the render hot path. Here it is *structurally unavoidable* (content changes every frame), so the mitigation is minimizing the copy's cost, not eliminating it. |
| `P-21` / `P-23` | The RT/GPU boundary guardrail — render stays off the audio deadline and on the display clock; unchanged by this dossier. |
| `P-03` / `P-18` / `P-25` | Benchmark-as-contract, p99/max not mean, pinned baseline commit — governs `EVD-0003` and the wave-3 delta. |
| `ADR-002` | Authorizes changing fork render code in place (TRUE HARD FORK posture). |

## Data journey
Per scrub frame: engine-published `VisualPlayPositionData` (read, not written, by the render thread) →
`WaveformWidgetRenderer` computes the displayed window → `allshader::WaveformRendererRGB::preprocess()`
rebuilds the CPU-side vertex array (`geometry().vertexDataAs<...>()`) and calls `markDirtyGeometry()`
unconditionally (`waveformrendererrgb.cpp:126-127`) → `BaseGeometryNode::render()` sees the dirty flag,
re-uploads that exact buffer to the persistent VBO (`basegeometrynode.cpp:110-125`), binds it via
`setAttributeBuffer`, and issues `glDrawArrays`. In this regime steps 2 and 3 both execute, back to back,
every vsync, per deck — the combined cost this dossier measures and, if warranted, reduces.

## Risks
- `AP-02` (a "faster on average" change that regresses house physics) — guarded by keeping the change
  entirely inside the render thread and re-running `ctest -R Engine` unchanged at every wave.
- `AP-01` (green-over-red closure) — guarded by the architecture decision gate above: if `EVD-0003` shows
  no real headroom problem, the honest close is "measured, no change justified," not a fabricated win.
- Unsynchronized/mapped-buffer variants (if chosen in wave 2) carry a correctness risk if the mapping
  overlaps an in-flight GPU read — mitigated by keeping `ctest -R Waveform` as a hard gate on every wave.

## Verifiability
The wave-1 benchmark IS the proof mechanism: it becomes the `90-EXECUTION` gate for both wave 1
(reproducibility) and wave 3 (the delta), and its recorded `EVD-0003`/delta becomes the `91-LOOP-CLOSURE`
verdict input.
