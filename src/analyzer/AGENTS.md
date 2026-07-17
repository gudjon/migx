# AGENTS.md — analyzer/ (off-thread beat/key/gain/waveform analysis)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-analyzer.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
Computes a track's derived musical data. `TrackAnalysisScheduler` queues tracks and `AnalyzerThread`
runs a chain of analyzers over the decoded samples — beats, key, gain/loudness, waveform, silence —
delegating heavy DSP to `plugins/` (Queen Mary, KeyFinder, SoundTouch). Pure **worker-thread** batch
work; results are written back into the `Track` and persisted by the library.

## Key files
- `trackanalysisscheduler.cpp/.h` — queues tracks, load-balances worker threads.
- `analyzerthread.cpp/.h` — one worker running the analyzer chain per track.
- `analyzerbeats.cpp`, `analyzerkey.cpp`, `analyzergain.cpp`, `analyzerebur128.cpp` — the analyzers.
- `analyzerwaveform.cpp` — waveform-summary generation; `analyzersilence.cpp` — silence trimming.
- `plugins/analyzerqueenmarybeats.cpp`, `plugins/analyzerkeyfinder.cpp`, `plugins/analyzersoundtouchbeats.cpp`
  — the DSP backends.

## Invariants you MUST respect
- **Worker-thread only:** analysis never touches the audio callback; it consumes decoded samples on its
  own threads and hands results back off the RT path. `P-17`.
- **Results flow into the canonical Track:** analyzers write beats/key/gain into the `Track` aggregate
  (via `BeatFactory`/`KeyFactory`), the source of truth — not a private side store. `P-07`.
- **Fail loud:** an analysis failure is surfaced/logged, not silently discarded as a zero-length/empty
  result that masquerades as success. `AP-16`.
- **A speedup must not change the result contract:** DSP perf work keeps the detected beatgrid/key stable
  (or is validated against a golden), not just faster. `AP-02`, `P-03`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R "Analyzer|Beat|Key"` (GoogleTest; `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Touching the audio callback or engine internals from an analyzer (`P-17`).
- Swallowing an analysis error into an empty-but-successful result (`AP-16`).
- Landing a DSP speedup that changes the detected beatgrid/key without a golden/benchmark (`AP-02`, `P-03`).

## Cross-references
Upstream: `src/sources/AGENTS.md` (decoded samples), `src/track/AGENTS.md` (the `Track` to fill).
Downstream: `src/track/AGENTS.md`, `src/library/AGENTS.md`, `src/waveform/AGENTS.md`. Card:
`kanban/architecture/ddd/bounded-contexts/arch-analyzer.md`.
