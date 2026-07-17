---
id: dossier-DSP
slug: 2026-07-17-gudjon-DSP--iir-eq-filter-simd
type: dossier
prefix: DSP
title: "Baseline + SIMD the EngineFilterIIR EQ hot loop on Apple Silicon (M4)"
classification: none
phase: foundation
sealed: false
status_note: "Scaffolded — PS-DSP-01 written against src/engine/filters/enginefilteriir.h:239 at HEAD; no code changed yet. Wave 1 (headless benchmark + EVD-DSP-01) is the next action."
completion-criteria:
  - "A headless, allocation-free benchmark of EngineFilterIIR::process() reports p50/p90/p99/max per 1024-frame stereo buffer, recorded as pinned EVD-DSP-01 (commit SHA + M4 core config)."
  - "A NEON/Accelerate(vDSP) rewrite of the steady-state path does not regress p99 vs EVD-DSP-01, is bit-tolerance-verified against the scalar output, and adds no allocation/lock to process() (P-02)."
  - "ctest --test-dir build -R 'Engine|Effects' stays green through every wave."
facilitator: gudjon
initiative: initiative-apple-silicon
authored_by: claude-code
authored_kind: mixed
triggered_by: "initiative-apple-silicon Scope→dossiers table (DSP row) — the second Apple-Silicon perf lane, opened after MTL's baseline precedent"
created: "2026-07-17"
lastUpdated: "2026-07-17"
last_audited: "2026-07-17"
---

# Baseline + SIMD the EngineFilterIIR EQ hot loop — agent routing

The card above is this dossier's identity. This opens the `DSP` workstream of
`initiative-apple-silicon`: unlike `MTL` (which had to skip its GL half headlessly, see
`kanban/planning/2026-07-17-gudjon-MTL--waveform-render-baseline/`), this is **pure CPU** — the whole
benchmark, baseline, and optimization delta run in the headless `mixxx-test` binary with no GL/GPU
context required.

## Routing by intent

| You want to… | Go to |
|---|---|
| Understand why this bet exists | `00-FOUNDATION/PROBLEM.md` |
| See the checkable spec | `00-FOUNDATION/PS-DSP-01.md` (EARS + `acceptance:`) |
| See prior art / upstream scan | `01-RESEARCH/00-RESEARCH.md` |
| See the chosen design + patterns cited | `02-ARCHITECTURE/00-ARCHITECTURE.md` |
| See the ordered plan + gates | `90-EXECUTION/00-PHASE-PLAN.md` |
| Score / seal the bet | `91-LOOP-CLOSURE/00-LOOP-CLOSURE.md` |
| Catch up on what happened | `JOURNAL.md` |

## The closed loop this dossier is (MG-1)

- **Trigger** — `initiative-apple-silicon`'s DSP row: "Find the scalar hot loops (resampling, EQ,
  analysis); measure what vDSP buys, allocation-free." `EngineFilterIIR::process()`
  (`src/engine/filters/enginefilteriir.h:239-244`) is that scalar hot loop for EQ: a per-sample IIR
  difference equation run on every audio buffer, for every deck with an EQ effect enabled.
- **Capture** — a new headless benchmark drives `process()` over realistic 1024-frame stereo buffers
  at 44.1 kHz and reports p50/p90/p99/max per buffer, recorded as pinned `EVD-DSP-01` (commit SHA + M4
  core config + macOS build, per `P-25`).
- **Intelligence** — the measured delta: scalar `EVD-DSP-01` vs a NEON/Accelerate(vDSP) rewrite's
  p99/max, plus a numerical-tolerance check that the SIMD path's output matches the scalar path within
  a stated bound (a faster filter that changes the sound is a regression, not a win).
- **Adjustment** — the merged allocation-free SIMD path, gated on p99 non-regression + tolerance +
  `ctest -R 'Engine|Effects'` green; re-closes on the next benchmark run against this pinned baseline.

## Owning context
`arch-engine-realtime` (`src/engine/`, DDD card
`kanban/architecture/ddd/bounded-contexts/arch-engine-realtime.md`). `EngineFilterIIR::process()` runs
on the RT audio callback thread — every wave here respects `P-02`/`AP-02` (no allocation/lock added),
`P-16` (lock-free), and `P-06` (single ControlObject writer, unaffected by this filter-internals change).
