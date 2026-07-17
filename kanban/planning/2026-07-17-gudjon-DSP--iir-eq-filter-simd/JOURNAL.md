# Journal

*Round-by-round narrative during execution. Git holds the exact chronology; this holds the "why we
turned here" that a diff can't. Append newest-last. Keep entries short.*

## 2026-07-17 — scaffold
- **Did:** Opened the `DSP` dossier from `_template`. Root claim confirmed at HEAD (`deda627b1b`):
  `EngineFilterIIR::process()` steady-state loop at `src/engine/filters/enginefilteriir.h:239-244`,
  wired into the builtin EQ/Filter effects via `EngineFilterBiquad1*`/`Bessel4*`/`Bessel8*`/
  `Butterworth4*`/`Butterworth8*` (all `src/engine/filters/enginefilter*.h`).
- **Measured:** nothing yet — no benchmark exists. Wave 1 creates it.
- **Decided:** no OPEN dossier owns this scope (checked `kanban/planning/`); scaffolded new rather than
  folding in. Confidence: high (grep confirmed zero existing `EngineFilterIIR` references in
  `src/test/`).
- **Next:** Wave 1 — write the headless `BM_EngineFilterIIR*` benchmark and capture `EVD-DSP-01`.

## 2026-07-17 — Wave 1 done, Wave 2 NO-GO (evidence-based halt)
Aggregate full-EQ-chain measured (BM_EngineFilterFullEqChain): worst case 4 decks x every band = ~0.55% of the RT buffer. Vectorizing saves ~0.3% absolute — not worth a SIMD rewrite on the RT path. Wave 2 halted; render (MTL) is the better AS bet. See results/EVD-DSP-01. Successor if DSP revisited: profile resampler/analysis, not EQ IIR.
