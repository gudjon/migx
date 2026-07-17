# Execution — phase plan

*Ordered waves. Wave 1 is baseline-only (a number to beat); Wave 2 is the SIMD change; Wave 3 verifies
the delta and re-confirms RT safety. Commit per wave; every commit builds.*

## Waves

| # | Wave | Deliverable | Verifiability gate |
|---|---|---|---|
| 1 | **Headless filter benchmark + `EVD-DSP-01`** | A `benchmark::benchmark` case (house style per `src/test/waveformrenderbenchmark.cpp`) driving `EngineFilterIIR::process()` over 1024-frame, 44.1kHz synthetic stereo buffers for `EngineFilterBiquad1Peaking` (SIZE=5) and one higher-order instantiation (SIZE=8); reports p50/p90/p99/max per buffer. Result recorded as `results/EVD-DSP-01` with commit SHA + M4 core config + arm64-native confirmation (`P-24`). | Bench builds and runs via `mixxx-test --benchmark`; two runs agree within a stated tolerance (reproducibility); `ctest --test-dir build -R Engine` green; `pre-commit run --files <changed>` clean. |
| 2 | **NEON/Accelerate(vDSP) rewrite of the steady-state path** | Replace the scalar `!m_doRamping` branch of `process()` with a NEON or Accelerate `vDSP_biquad`/`vDSP_deq22`-backed path; SIMD/vDSP setup (coefficient/delay-line layout) happens once at construction/`setCoefs`, never per buffer. Ramping branch untouched. | `ctest --test-dir build -R 'Engine|Effects'` green; a numerical-tolerance test (swept-frequency + impulse signal) shows SIMD output matches scalar `processSample()` output within the stated tolerance; `pre-commit` clean. |
| 3 | **Measure the delta + RT-safety guard** | Re-run the Wave 1 benchmark against the Wave 2 code; record the p99/max delta vs `EVD-DSP-01` in `results/`; re-confirm by inspection + a targeted allocation check that no `new`/`malloc`/lock was added anywhere on the `process()` call path. | p99 does not regress vs `EVD-DSP-01` (`P-18`, never the mean — `AP-11`); zero underruns implied by p99/max staying at or below baseline; no allocation/lock added (`P-02`/`AP-02`); `ctest -R 'Engine|Effects'` green. |

## Gate definitions (the `02-VERIFIABILITY-GATES` detail)
- **Wave 1 gate:** `build/mixxx-test --benchmark --benchmark_filter=BM_EngineFilterIIR` → reports
  p50/p90/p99/max for both instantiations; `ctest --test-dir build -R Engine` → green.
- **Wave 2 gate:** `ctest --test-dir build -R 'Engine|Effects'` → green; the numerical-tolerance test
  → passes (no sample exceeds the stated tolerance).
- **Wave 3 gate:** Wave-1 benchmark re-run → p99 ≤ `EVD-DSP-01` p99 for both instantiations; manual/
  grep-assisted RT-safety review of the diff on `process()` and any new SIMD helper → clean.

## House-physics guardrails (apply to every wave — MG-6)
- No allocation / no lock added anywhere reachable from `process()` (`P-02`/`AP-02`); SIMD/vDSP scratch
  state is constructed once, at `EngineFilterIIR` construction or `setCoefs`/`setCoefs2` time.
- Cross-thread handoff (if any new state crosses off the RT thread) stays lock-free (`P-16`).
- `EngineFilterIIR`'s Qt affinity (may emit, never receive) is unchanged — no GUI touch introduced.
- `pre-commit run --files <changed>` clean (clang-format/tidy) every wave; every commit builds
  (bisectability).

## Rollback
Wave 1 is additive (test/bench tree only) — revert its commit to back out. Wave 2's rewrite lands
behind the same `process()` entry point with the scalar path intact in `processSample()` until the
tolerance/perf gates pass; if Wave 2 fails its gate, revert the Wave 2 commit — `EVD-DSP-01` and the
bench survive untouched as the number the next attempt measures against.

## Loop discipline (when running unattended)
Decide at forks with confidence ≥ 0.4 or flag-and-skip; never stop to ask unless irreversible or a
value judgment. Record decisions in `../JOURNAL.md`. Always leave the loop closed.
