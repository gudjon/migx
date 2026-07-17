# Problem

Migx forks Mixxx's EQ/filter DSP as-is: portable, scalar C++ written for cross-platform correctness,
not for Apple Silicon. `initiative-apple-silicon`'s DSP row calls this out by name: "Find the scalar
hot loops (resampling, EQ, analysis); measure what vDSP buys, allocation-free (P-02)." This dossier
opens that workstream at its most-used hot loop: the IIR EQ filter.

## What's wrong today
`EngineFilterIIR<SIZE, PASS>::process()` (`src/engine/filters/enginefilteriir.h:239-244`) processes
audio one sample at a time, scalar, via `processSample()` — a distinct hand-written difference-equation
specialization per `(SIZE, PASS)` (biquad order-2/5, Bessel/Butterworth order-4/8/16 — specializations
run from `enginefilteriir.h:326` to `:652`). It runs on the RT audio callback thread, once per stereo
sample pair, for every buffer, for every deck with an EQ or Filter effect enabled — and no benchmark
exists today that measures its per-buffer cost, on any hardware, in any repeatable form. There is
nothing to compare a NEON/Accelerate rewrite against.

## Who feels it
Every DJ using the EQ or Filter knob on any deck — this runs continuously while playing, not just on
interaction. On an M4 the un-vectorized L/R channel processing and the fully scalar per-tap arithmetic
leave the NEON units and Accelerate's `vDSP_biquad`/`vDSP_deq22` cascade primitives unused; headroom
that could go to lower buffer-time tails (fewer underrun risks at small buffer sizes) or more headroom
for other per-buffer work (more decks, more effects) is left on the table.

## What "done" means (the bet)
This dossier is a bet with three parts (MG-1/MG-5):
1. **The problem is real** — a pinned headless baseline (`EVD-DSP-01`) showing the scalar per-buffer
   p50/p90/p99/max cost of `process()` for at least a biquad and a higher-order instantiation on M4.
2. **The approach works** — a NEON/Accelerate(vDSP) rewrite of the steady-state path measurably beats
   or matches `EVD-DSP-01`'s p99, allocation-free, with output numerically equivalent to the scalar
   path within a stated tolerance.
3. **The gates catch failure** — the benchmark delta (p99/max, never mean, `P-18`/`AP-11`) plus a
   numerical-tolerance test plus `ctest -R 'Engine|Effects'` all fail loudly if the SIMD path regresses
   speed, changes the sound, or violates RT safety (`P-02`/`AP-02`).

## Non-goals
- The ramping/crossfade branch of `process()` (a separate, rarer-hot cross-fade path).
- The fidlib coefficient-design call (`setCoefs`/`setCoefs2`) — that runs off the RT thread on
  parameter change, not per buffer.
- Resampling or analysis DSP (also named in the initiative's DSP row) — separate follow-on dossiers
  once this one establishes the benchmark/tolerance pattern to reuse.
- Any change to which filter topology an effect chooses, or to effect-level behavior.

## Inheritance
Builds on the benchmark-house-style precedent set by `MTL`'s baseline dossier
(`kanban/planning/2026-07-17-gudjon-MTL--waveform-render-baseline/`) — same `p50/p90/p99/max` +
`EVD-*` pinning discipline (`P-03`, `P-18`, `P-25`), same "baseline-only first wave" shape. Differs in
one structural way worth naming: MTL's bench had to skip its GL half headlessly (`EVD-0003`'s scrub
bench needs an offscreen surface); this DSP bench is pure CPU, so it gets a *complete* p50..max
distribution with no environment-dependent skip path. RT-safety guardrails inherited from
`src/engine/AGENTS.md` and `P-02`/`P-16`/`P-06`.
