# DSP — baseline + SIMD the IIR EQ filter hot loop (M4)

## Scope
The second Apple-Silicon perf lane (`initiative-apple-silicon`'s `DSP` row), opened at
`src/engine/filters/enginefilteriir.h:239` — the scalar per-sample IIR difference equation every
builtin EQ/Filter effect runs on the RT audio callback thread. Bounded to the steady-state
(`!m_doRamping`) branch of `EngineFilterIIR::process()`; the ramping/crossfade branch, the fidlib
coefficient-design path, and other DSP hot loops (resampling, analysis) are explicit non-goals — see
`00-FOUNDATION/PROBLEM.md`.

## Why this, why now
No OPEN dossier owns this scope (checked `kanban/planning/` at scaffold time: `MTL` dossiers own the
render/GPU lane, not DSP). `DSP` is registered in
`kanban/planning/00-PORTFOLIO/prefix-registry.yaml`. Unlike the `MTL` waveform baseline — which had to
skip its GL half headlessly (see `EVD-0003` in the MTL scrub-regime dossier) — this benchmark is pure
CPU: no GL/GPU context anywhere on the call path, so the headless `mixxx-test` binary yields a
**complete** p50/p90/p99/max distribution with no environment-dependent skip.

## Success criteria
See `00-FOUNDATION/PS-DSP-01.md`'s `acceptance:` block. In short: a pinned headless baseline
(`EVD-DSP-01`), then a NEON/Accelerate(vDSP) rewrite that does not regress p99, stays numerically
equivalent within a stated tolerance, and adds no allocation/lock to the RT path.

## Status
`foundation` — PS-DSP-01 written and rooted in real `file:line` at HEAD; no code changed. Wave 1
(the benchmark + `EVD-DSP-01`) is the recommended next action; see `90-EXECUTION/00-PHASE-PLAN.md`.
