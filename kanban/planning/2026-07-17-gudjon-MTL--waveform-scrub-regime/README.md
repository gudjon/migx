# Waveform scrub-regime optimization — dossier front page

**Prefix:** MTL · **Initiative:** initiative-apple-silicon · **Facilitator:** gudjon · **Phase:** foundation
(scaffolded, not yet executed)

## Scope
The waveform GL backend's persistent VBO (`src/rendergraph/opengl/backend/basegeometrynode.cpp`,
`PS-MTL-02`, merged) skips re-upload when a frame is unchanged — the **steady-state** win, measured in
`EVD-0002`. This dossier owns the distinct, complementary regime `EVD-0002` explicitly flagged as
unmeasured: **active scrubbing / a seek**, where every `allshader` renderer's `preprocessInner()` marks
the geometry dirty on every call (`src/waveform/renderers/allshader/waveformrendererrgb.cpp:126-127`), so
the VBO re-uploads on **every** frame. No benchmark today drives the CPU rebuild and the mandatory GPU
re-upload together for this regime (`src/test/waveformrenderbenchmark.cpp` splits them into separate,
unconnected benches — see `00-FOUNDATION/PS-MTL-03.md`).

## Success criteria
1. A combined-regime benchmark exists in `src/test/waveformrenderbenchmark.cpp` and a pinned `EVD-0003`
   baseline is captured (commit SHA + M4 core config).
2. A wave-2 optimization (chosen from `EVD-0003`'s data, per `02-ARCHITECTURE`'s decision gate) does not
   regress combined p99 vs `EVD-0003` and keeps max under the 120 Hz frame budget (8333µs) — zero frames
   over budget — or the dossier honestly halts if the data shows no headroom problem exists.
3. `ctest -R 'Waveform|Engine'` stays 100% green throughout; no touch to `src/engine/` or any `process()`
   path (RT-safety preserved by construction).

## Current status
**Scaffolded (scoping only) — no implementation, no build run.** `00-FOUNDATION/PS-MTL-03.md` is the
checkable spec; `90-EXECUTION/00-PHASE-PLAN.md` names wave 1 (benchmark + baseline) as the recommended
next action.

## Non-overlap with the sibling VBO dossier
`2026-07-17-gudjon-MTL--waveform-zero-copy-vbo` (open, unsealed) owns steady-state only; this dossier is
scoped to the continuously-dirty scrub/seek regime and does not reopen or duplicate that work.

## Map
`00-FOUNDATION/PROBLEM.md` · `00-FOUNDATION/PS-MTL-03.md` · `01-RESEARCH/00-RESEARCH.md` ·
`02-ARCHITECTURE/00-ARCHITECTURE.md` · `90-EXECUTION/00-PHASE-PLAN.md` · `JOURNAL.md`. Seal at
`91-LOOP-CLOSURE/` after wave 3.
