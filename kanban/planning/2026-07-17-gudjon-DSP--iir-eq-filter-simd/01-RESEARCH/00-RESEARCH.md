# Research

## Prior art in-repo
- `src/test/waveformrenderbenchmark.cpp` — the house benchmark style to mirror: fixed
  `benchmark::State` `Iterations`, a synthetic deterministic input (a seeded LCG, not real audio
  files), per-frame `p50/p90/p99/max` counters plus a `SetLabel` human-readable summary, and
  `benchmark::DoNotOptimize` to stop the compiler eliding the measured work. `EngineFilterIIR::process()`
  is the audio-DSP analogue of that renderer's `preprocess()` — a pure-CPU, allocation-free,
  per-iteration hot loop with a stable, repeatable synthetic input (a swept-frequency or
  pseudo-random sample stream rather than a scrubbing scene).
- `src/engine/filters/enginefilteriir.h` — the target itself. Confirmed at HEAD (`deda627b1b`):
  `process()` at line 239, the steady-state loop at 241-244, the ramping branch at 245-291,
  `processSample()` declared at line 294 with per-`(SIZE,PASS)` specializations from line 326
  (`SIZE=2, IIR_LP`) through line 652 (`SIZE=2, IIR_HP2`). No existing benchmark or perf test
  references this file (`grep -rn "EngineFilterIIR" src/test/` at scaffold time: no hits).
- Concrete instantiations actually wired into effects (confirmed by grep, not assumed):
  `EngineFilterBiquad1Peaking`/`Low`/`High`/`LowShelving`/`HighShelving`
  (`src/engine/filters/enginefilterbiquad1.h`) feed `parametriceqeffect.h`, `graphiceqeffect.h`,
  `filtereffect.h`, `biquadfullkilleqeffect.h`; `EngineFilterBessel4*`/`Bessel8*`
  (`enginefilterbessel4.h`/`enginefilterbessel8.h`) feed the Full Kill EQ's LV-mix isolator band;
  `EngineFilterButterworth4*`/`Butterworth8*` exist as a further crossfade/EQ family.

## Open questions for Wave 1/2 (to resolve during execution, not blocking scaffold)
- **vDSP fit:** Apple's Accelerate `vDSP_biquad`/`vDSP_deq22` operate on a cascade of *biquad* (order-2)
  sections with a fixed coefficient layout (`b0,b1,b2,a1,a2` per section, delay state `z[2]` per
  section). `EngineFilterIIR`'s own coefficient layout (from `fid_design_coef`, one flat `m_coef[]`
  array indexed per specialization) does not match vDSP's cascade layout directly — Wave 2 needs a
  one-time (construction/`setCoefs`-time) coefficient repack into vDSP's expected form, never a
  per-buffer repack (this is the `P-02` guardrail already named in the PS).
- **NEON alternative:** for orders that don't cleanly decompose into cascaded biquads (e.g. the
  `SIZE=5, IIR_BP` biquad-peaking form which mixes `fir`/`iir` terms non-uniformly, or the
  serially-dependent higher orders), a hand-written NEON path processing the L/R channel pair in
  parallel lanes (2 lanes = 2 channels) may be simpler to verify than forcing every topology through
  vDSP's biquad cascade. Wave 2 decides per-instantiation which route to take; both routes are valid
  under this PS's acceptance contract (p99 + tolerance + allocation-free), the PS does not mandate one.
- **Tolerance figure:** the exact numerical tolerance (this dossier's draft: 1e-6 relative) should be
  confirmed against fidlib's own precision characteristics during Wave 2, not asserted before the
  rewrite is drafted.

## Options considered (not yet decided — Wave 2 territory)
1. Accelerate `vDSP_biquad` cascade (best fit for the pure-biquad instantiations: SIZE=2 LP/BP/HP,
   SIZE=5 peaking/shelving).
2. Hand-written NEON intrinsics processing L+R in parallel SIMD lanes (best fit for the higher serial
   orders where cascade repacking is awkward).
3. A hybrid: vDSP for biquad-shaped filters, NEON L/R-parallel for the rest — likely the actual answer,
   to be confirmed once Wave 1's baseline shows which instantiations dominate real EQ/Filter usage.
