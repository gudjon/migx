# Research

## Upstream (Mixxx) changelog scan
Upstream Mixxx does not track a persistent-VBO GL backend for the QWidget waveform path at all — Migx's
`PS-MTL-02` change (persistent VBO, dirty-tracked upload) is a Migx-only fork addition
(`ADR-002`, TRUE HARD FORK). There is therefore no upstream prior art for a *combined-regime* (scrub +
mandatory re-upload) benchmark or optimization either; this is fork-original ground, same as the sibling
dossier.

## Prior art
- **Apple Silicon / unified memory:** CPU and GPU share physical RAM (`P-22`'s rationale). The
  `glBufferData`(orphan)+`glBufferSubData` pair used by the current dirty path
  (`basegeometrynode.cpp:118-123`) is the OpenGL-classic "orphan to avoid a stall" idiom; on Apple's
  OpenGL-on-Metal translation layer its actual cost (vs, say, `glMapBufferRange` with
  `GL_MAP_INVALIDATE_BUFFER_BIT | GL_MAP_UNSYNCHRONIZED_BIT`, or a small ring of N VBOs cycled per frame
  to let the driver pipeline uploads without an implicit orphan) is not established — that is exactly
  what `EVD-0003` needs to answer before wave 2 picks a lever.
- **Mixxx/Qt ecosystem:** the QML/SceneGraph waveform backend (`src/rendergraph/scenegraph/`) already
  goes through Qt's own `QSGGeometryNode` buffer management, which historically uses a similar
  orphan-on-dirty strategy; it is out of scope here (only the `rendergraph_gl` / QWidget-skin backend is
  touched, consistent with `PS-MTL-02`'s scope).

## Options considered
| Option | Pros | Cons | Verdict |
|---|---|---|---|
| Measure only, no wave-2 change (treat this as a second baseline dossier) | Lowest risk; matches "baseline first" doctrine | Doesn't close the loop with an `Adjustment` beat if the number turns out to matter | Rejected as the *only* wave — kept as the honest fallback if `EVD-0003` shows the regime is already cheap relative to the frame budget (see PROBLEM.md non-goals) |
| `glMapBufferRange` (unsynchronized, invalidate) instead of orphan+SubData | Avoids the implicit full-buffer orphan; driver-recommended modern path | Requires care: unsynchronized maps need the caller to guarantee no overlap with in-flight GPU reads — needs correctness verification (`ctest -R Waveform`) | Leading candidate for wave 2, pending `EVD-0003` showing the upload (not the CPU rebuild) dominates this regime |
| Small ring of N persistent VBOs cycled per frame | Removes orphan-stall risk entirely; well-understood pattern | More GL state (N buffer names, lifetime management in `~BaseGeometryNode()`); higher blast radius | Secondary candidate if the ring's added complexity is justified by `EVD-0003`'s numbers |
| Optimize the CPU rebuild instead (SIMD/incremental) | May dominate if `EVD-0003` shows CPU > GPU cost in this regime | Separate lever already flagged in `EVD-0001`'s copy-map as a distinct PS; conflates two problems in one dossier | Deferred — only pulled in if `EVD-0003` data says so (kept honest per architecture-decision-authority: decide from evidence, don't assume) |

## Baseline measurement (the trigger/capture for MG-1)
Not yet captured — this dossier's wave 1 IS the baseline capture. `EVD-0003` will record: the exact
benchmark command, the M4 core config (10-core, 4P+6E, matching `EVD-0001`/`EVD-0002`'s host), the Qt
version, whether the run is on a quiescent host (per `EVD-0001`'s enrichment lesson — measure floor/p50
on a quiescent host, flag p99/max as load-sensitive if the host is not quiescent), and the pinned commit
SHA. Every later wave-2 delta measures against this number, never a moving `main` (`AP-09`).

## Open questions
1. Does the combined regime's cost come predominantly from the CPU rebuild (`EVD-0001`'s ~31-39µs) or
   the GPU re-upload (`EVD-0002`'s ~6.5-7µs, in isolation) once both are forced to run back-to-back on
   the same frame with a live GL context? `EVD-0003` answers this and picks the wave-2 lever.
2. Does the *reference scene* frame budget (60Hz = 16667µs, 120Hz = 8333µs) leave meaningful headroom
   once both costs are summed, or is this regime already comfortably under budget (in which case wave 2
   may be "no change justified, mergeable-as-measurement-only" — an honest halt, not a forced win)?
3. Multi-deck scaling: does N decks scrubbing simultaneously multiply this per-deck cost roughly
   linearly (expected, since each deck is an independent `BaseGeometryNode`), and if so at what deck
   count does the combined regime start contending with the frame budget? Flagged for a follow-on
   dossier if `EVD-0003` shows headroom is tight even at N=1.
