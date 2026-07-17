# Journal

*Round-by-round narrative during execution. Git holds the exact chronology; this holds the "why we
turned here" that a diff can't. Append newest-last. Keep entries short.*

## <YYYY-MM-DD> — <wave / round>
- **Did:** <what happened>
- **Measured:** <benchmark/test result, vs baseline>
- **Decided:** <any fork resolved, with the reasoning / confidence>
- **Next:** <the next step>

## 2026-07-17 — Wave 1 (confirm backend + baseline env)
- **Did:** Build green (RelWithDebInfo, arm64). Confirmed graphics backend = OpenGL forced at
  `coreservices.cpp:826`; code reason = offscreen rendering must work → Metal switch is gated on that.
  Captured M4 env into `results/EVD-0001.md` (M4 10-core, macOS 26.2, commit 2332debe, Qt6).
- **Measured:** n/a yet (Wave 2 writes the benchmark). Smoke: 20 SampleUtil tests pass; bench harness live.
- **Decided:** Baseline measures the `rendergraph_gl` allshader RGB path (the no-VBO hot path) — the
  `P-22`/`AP-12` target. Model the bench on `controllerrenderingengine_test.cpp` offscreen harness.
- **Next:** Wave 2 — implement the waveform-render frame-time benchmark, build, run, fill EVD-0001.

## 2026-07-17 — Wave 2+3 (benchmark + baseline captured, independently verified)
- **Did:** Implemented `src/test/waveformrenderbenchmark.cpp` (BM_WaveformRGBPreprocess / Filtered) driving
  the real allshader `preprocess()` vertex rebuild over a scripted scrubbing scene (synthetic ~264k-point
  Waveform, Retina deck). Wired into CMake BUILD_BENCH. Filled EVD-0001.
- **Measured:** RGB per-frame CPU vertex rebuild ~34-39µs floor / ~38-45µs p50; Filtered ~45-52µs floor.
  0/4000 dropped vs 60/120Hz. **Independently reproduced** (P-08, evaluator≠author): RGB min 33.7 p50 37.9
  p99 41.5µs on a lighter-load host — confirms the floor + tighter tails. Baseline is REAL + reproducible.
- **Decided:** Floor (min) is the trustworthy pinned number (p99/max load-sensitive — flagged honestly,
  P-01/P-03). Phase B (offscreen GPU frame-time) deferred per ≥0.4 fork rule — Phase A gives a real baseline;
  forcing the GL harness now would burn the wave on offscreen-context plumbing.
- **Next:** Wave 4 copy-map (per-frame CPU↔GPU copy sites, file:line) → the zero-copy/Metal dossier's input.
