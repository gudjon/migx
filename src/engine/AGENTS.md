# AGENTS.md — engine/ (real-time audio processing graph)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-engine-realtime.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
The per-buffer audio processing graph. Pulls decoded samples, applies rate/scratch/keylock scaling,
mixes channels (gain, EQ, crossfader), and produces the master/headphone buffers the sound device
consumes. Everything reachable from `process*()` runs on the **real-time audio callback thread**.

## Key files
- `enginemixer.cpp` — top of the process graph; master/headphone mix.
- `enginebuffer.cpp` — per-deck playback: rate, scratch, keylock, slip.
- `channels/` — `EngineChannel` nodes (deck / sampler / mic / aux).
- `sync/enginesync.cpp` — master-clock / beat-sync authority (single master).
- `bufferscalers/` — time-stretch / pitch (RubberBand, Soundtouch).
- `cachingreader/`, `readaheadmanager.cpp` — sample supply ahead of playback.
- `engineworker*.cpp` — off-RT-thread work dispatch.
- `effects/` — carved out to the effects context (see `src/effects/`).

## Invariants you MUST respect
- **RT thread (hard):** anything reachable from `process()` runs on the audio callback — **no**
  `new`/`malloc`/`std::vector` growth, **no** mutex, **no** file/network I/O, **no** blocking. Cross-thread
  out = lock-free ring buffer (`util/fifo.h`), atomic double-buffer, or `ControlObject`. `P-02`, `P-16`.
- **Object lifetime off this thread:** construct/destroy on the GUI/worker thread; hand to the RT
  thread by pointer swap. Never `new`/`delete`/smart-ptr destruct on the callback. `P-17`.
- **Qt affinity:** may *emit* Qt signals; must never *receive* a signal synchronously or mutate a GUI
  QObject on the audio thread; no `Qt::DirectConnection` across the RT boundary. `P-20`, `AP-14`.
- **ControlObject single writer:** each `[Group],key` has one authoritative writer. `P-06`, `AP-03`.
- **Perf changes (the M4 north-star) need a benchmark contract** with p99/max + zero underruns, not a
  mean. `P-03`, `P-18`, `AP-11`.

## Build / test entry points
- Build the app/lib: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R Engine` (GoogleTest; engine tests live in `src/test/`, e.g.
  `enginebuffer_test`, `enginesync_test`). Or run the `mixxx-test` binary under a debugger.
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Any allocation, lock, or blocking call on a `process()`-reachable path.
- Adding a second writer to an existing ControlObject.
- Letting GPU/other-thread latency gate the audio deadline (`AP-02`, and see `arch-waveform-render`).

## Cross-references
Upstream: `src/control/AGENTS.md` (the ControlObject seam), `src/soundio/AGENTS.md` (callback origin),
`src/sources/` (decode). Downstream: `src/soundio/`, `src/waveform/`, `src/vinylcontrol/`.
