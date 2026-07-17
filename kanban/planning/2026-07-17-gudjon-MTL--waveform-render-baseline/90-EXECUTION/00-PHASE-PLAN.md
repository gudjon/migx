# Execution — phase plan

*Ordered waves. This is a baseline dossier: the deliverable is a trustworthy number + a copy-map, not a
speedup. Commit per wave; every commit builds.*

## Waves

| # | Wave | Deliverable | Verifiability gate |
|---|---|---|---|
| 1 | **Confirm the backend + build native** | Verify the live graphics backend (expected OpenGL per `coreservices.cpp:826`) and that the build is arm64-native (`P-24`); record Qt version + M4 core config. | A short note in `results/` stating backend + arch + Qt, reproduced twice. |
| 2 | **Write the render benchmark** | A `benchmark::benchmark`/offscreen bench driving the `allshader` waveform renderer over N frames of a scripted scrubbing scene; reports p50/p99/max + dropped-frame count. | `pre-commit` clean; the bench builds and runs via `ctest`/bench binary; two runs agree within tolerance. |
| 3 | **Capture the baseline (`EVD-0001`)** | Run the bench on this M4, record `results/EVD-0001` with numbers + commit SHA + backend + core config. | `EVD-0001` exists with all fields; numbers reproducible. |
| 4 | **Map the CPU↔GPU copies** | Trace the render data journey at file:line; document every per-frame copy / geometry rebuild. | A copy-map in `results/` a future zero-copy dossier can act on. |

## Gate definitions
- **Wave 2 gate:** `ctest --test-dir build -R Waveform` (or the bench filter) runs green; p99/max reported.
- **Wave 3 gate:** re-run variance ≤ the stated tolerance (e.g. p99 within ±5% across two runs).

## House-physics guardrails (every wave — MG-6)
- The bench lives off the RT audio path; no allocation/lock added to `process()` anywhere (`P-02`).
- No per-frame CPU↔GPU round-trip introduced by the measurement (`AP-12`); render driven by the display
  clock, not the audio clock (`P-23`).
- `pre-commit run --files <changed>` clean; every commit builds (bisectability).

## Rollback
The bench is additive (test/bench tree only); backing out a wave = revert its commit. No product code
changes here.

## What this dossier hands off
`EVD-0001` (the baseline) + the copy-map become the inputs to the first *optimization* MTL dossier
(candidate: switch the macOS graphics backend off forced-OpenGL toward Metal/RHI — the `coreservices.cpp:826`
lead) and to a zero-copy waveform dossier (`P-22`). Those are separate bets, scored against this number.

## Loop discipline (unattended)
Decide at forks with confidence ≥ 0.4 or flag-and-skip; record in `../JOURNAL.md`; never stop to ask
unless irreversible or a value judgment. Leave the loop closed.
