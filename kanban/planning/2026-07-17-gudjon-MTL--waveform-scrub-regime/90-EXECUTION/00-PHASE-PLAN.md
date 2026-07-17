# Execution — phase plan

*Ordered phases (waves). Each wave ends at a verifiability gate — a check that must pass before the
next wave starts. Waves are executed under `/loop`; commit per wave.*

## Waves

| # | Wave | Deliverable | Verifiability gate |
|---|---|---|---|
| 1 | Extend the benchmark to the combined scrub regime + capture baseline | New case in `src/test/waveformrenderbenchmark.cpp` driving `preprocess()` + the real dirty-VBO re-upload together, per scrub position (continuous-dirty, live offscreen GL context); `results/EVD-0003.md` recorded (commit SHA + M4 core config + p50/p90/p99/max, quiescent-host per `EVD-0001`'s lesson) | Bench builds + runs, reports p50/p90/p99/max, reproducible within ~5% floor/p50 across 2 runs on a quiescent host (or the load-sensitivity honestly flagged, per `EVD-0001`'s precedent); `ctest --test-dir build -R 'Waveform\|Engine'` 100% green; if no GL context is available the bench `SkipWithError`s honestly (no fabricated number) |
| 2 | Implement the indicated optimization | The wave-2 lever `01-RESEARCH`'s options table + `EVD-0003`'s data indicate (or an honest halt, see below), inside `src/rendergraph/opengl/backend/basegeometrynode.cpp`'s dirty branch | `cmake --build build --target mixxx-test --parallel $(sysctl -n hw.ncpu)` green |
| 3 | Verify the delta + guard RT-thread impact | Re-run the wave-1 benchmark; compare combined p99/max to `EVD-0003`; confirm `ctest -R 'Waveform\|Engine'` unchanged; confirm the diff touches only `src/rendergraph/opengl/backend/` and/or `src/waveform/renderers/allshader/` (no `src/engine/` / `process()` touch) | p99 ≤ `EVD-0003`'s pinned p99 (no regression); max stays under the 120Hz frame budget (8333µs) at the reference scene, zero frames over budget; `ctest -R 'Waveform\|Engine'` 100% green; `git diff --stat` scoped to the render path only |

## Gate definitions (the `02-VERIFIABILITY-GATES` detail)
- **Wave 1 gate:** `build/mixxx-test --benchmark --benchmark_filter=BM_WaveformScrub...` (name TBD at
  implementation) → reports p50/p90/p99/max, recorded in `EVD-0003`; `ctest --test-dir build -R
  'Waveform|Engine'` → `100% tests passed`.
- **Wave 2 gate:** `cmake --build build --target mixxx-test --parallel $(sysctl -n hw.ncpu)` → exit 0.
- **Wave 3 gate:** the same benchmark re-run → combined p99 ≤ EVD-0003 pinned p99, max < 8333µs, zero
  frames over budget; `ctest --test-dir build -R 'Waveform|Engine'` → unchanged 100%; `pre-commit run
  --files <changed>` clean.

## House-physics guardrails (apply to every wave — MG-6)
- No allocation / no lock added on the RT audio thread — this dossier does not touch `src/engine/` or
  any `process*()` implementation at any wave; verified by diff-scope review each wave.
- Qt object ownership via `parented_ptr`/`make_parented` if any new Qt-owned object is introduced
  (unlikely — GL buffer names are not Qt objects); no leaks (VBO/context lifetime managed exactly as
  the sibling dossier's `~BaseGeometryNode()` pattern).
- `pre-commit run --files <changed>` clean (clang-format/tidy, qmllint, cmake lint) before each commit.
- Every commit builds (bisectability).

## Rollback
Wave 1 touches only `src/test/waveformrenderbenchmark.cpp` (additive, test-tree only) — revert that file
to back out. Wave 2 (if a code change lands) touches only
`src/rendergraph/opengl/backend/basegeometrynode.{h,cpp}` — revert to the pinned HEAD commit recorded in
`EVD-0003`'s `verified_against_code` to back out; no schema/state/API surface changes.

## Loop discipline (when running unattended)
Decide at forks with confidence ≥ 0.4 or flag-and-skip; never stop to ask unless irreversible or a value
judgment. The wave-2 lever choice is a fork resolved from `EVD-0003`'s data (see `02-ARCHITECTURE`'s
decision gate) — record that decision in `JOURNAL.md`, including the honest-halt outcome if the data
shows no change is justified. Always leave the loop closed.
