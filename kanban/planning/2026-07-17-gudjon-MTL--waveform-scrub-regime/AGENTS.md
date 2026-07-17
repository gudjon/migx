---
id: dossier-MTL-waveform-scrub-regime
slug: 2026-07-17-gudjon-MTL--waveform-scrub-regime
type: dossier
prefix: MTL
title: "Optimize the active-scrubbing/seek waveform render regime (the continuous-dirty VBO path)"
classification: A          # agent-scaffolded
phase: foundation           # scaffold | foundation | research | architecture | execution | sealed
sealed: false               # true only after 91-LOOP-CLOSURE is scored
status_note: "Scaffolded (scoping only, no implementation). PS-MTL-03 written; wave 1 (extend the benchmark to a combined CPU-rebuild + mandatory-VBO-reupload scrub regime, capture EVD-0003) is the recommended next action."
completion-criteria:
  - "A benchmark exists that drives the continuous-dirty scrubbing regime end-to-end (CPU vertex rebuild + the mandatory persistent-VBO re-upload every frame) and reports p50/p90/p99/max."
  - "A pinned EVD-0003 baseline recorded (commit SHA + M4 core config, per P-25)."
  - "An optimization lands that does not regress the combined p99/max vs EVD-0003, with zero frames over the 120Hz budget and no RT-thread/house-physics regression."
facilitator: gudjon
initiative: initiative-apple-silicon
authored_by: claude-code
authored_kind: mixed
triggered_by: "sibling dossier 2026-07-17-gudjon-MTL--waveform-zero-copy-vbo shipped the persistent VBO for STEADY-STATE (unchanged-frame, zero-upload) playback; its own EVD-0002 flagged (\"What is NOT measured\", point 1) that active scrubbing/playback marks geometry dirty every frame, so the VBO still re-uploads every frame there and that regime was never isolated or measured — this dossier owns exactly that gap"
created: "2026-07-17"
lastUpdated: "2026-07-17"
last_audited: "2026-07-17"
---

# Optimize the active-scrubbing/seek waveform render regime — agent routing

The card above is this dossier's identity. Below is routing-by-intent for an agent entering here.

## Routing by intent

| You want to… | Go to |
|---|---|
| Understand why this bet exists | `00-FOUNDATION/PROBLEM.md` |
| See the checkable spec | `00-FOUNDATION/PS-MTL-03.md` (EARS + `acceptance:`) |
| See prior art / the coverage-gap analysis | `01-RESEARCH/00-RESEARCH.md` |
| See the chosen design + patterns cited | `02-ARCHITECTURE/00-ARCHITECTURE.md` |
| See the ordered plan + gates | `90-EXECUTION/00-PHASE-PLAN.md` |
| Score / seal the bet | `91-LOOP-CLOSURE/00-LOOP-CLOSURE.md` |
| Catch up on what happened | `JOURNAL.md` |

## The closed loop this dossier is (MG-1)

- **Trigger** — `EVD-0002` (sibling VBO dossier) explicitly named the active-scrubbing regime as
  unmeasured: every scrub frame marks the geometry dirty (`waveformrendererrgb.cpp:127` calls
  `markDirtyGeometry()` unconditionally inside `preprocessInner()`), so the persistent VBO added by
  that dossier re-uploads on **every** frame in this regime — the win it proved was idle/steady-state
  only. No benchmark today drives the CPU rebuild and the mandatory dirty-VBO re-upload together.
- **Capture** — `PS-MTL-03`'s `acceptance:` block + a new combined-regime benchmark
  (`src/test/waveformrenderbenchmark.cpp`) reporting p50/p90/p99/max for one scrub frame
  (`preprocess()` + `basegeometrynode.cpp` render()'s dirty-path re-upload), recorded as the pinned
  `EVD-0003` baseline.
- **Intelligence** — the measured delta of the wave-2 optimization against `EVD-0003`: p99/max held or
  improved, zero frames over the 120 Hz budget, `ctest -R 'Waveform|Engine'` unchanged.
- **Adjustment** — the merged change in `src/rendergraph/opengl/backend/` and/or
  `src/waveform/renderers/allshader/`; re-closes on the next benchmark run against `EVD-0003`.

## Owning contexts
`arch-rendergraph` (`src/rendergraph/`) + `arch-waveform-render` (`src/waveform/`). Render thread only —
GPU/render work stays off the audio deadline (`P-21`/`P-23`); this dossier does not touch `src/engine/`
or any `process()` path (`P-02`).

## Non-overlap with the sibling VBO dossier
`2026-07-17-gudjon-MTL--waveform-zero-copy-vbo` (open, unsealed) owns the **steady-state** regime: an
unchanged frame now does zero upload. This dossier owns the **complementary, distinct** regime: a
**continuously dirty** frame (active scrub/seek), where every frame *must* re-upload and the win (if
any) is in the cost of that mandatory re-upload path, not in skipping it. Do not fold work back into the
sibling — it is scoped to steady-state and its `PS-MTL-02` acceptance contract is already closed on that
scope.
