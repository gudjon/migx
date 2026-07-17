# AGENTS.md — track/ (the Track aggregate read across every thread)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-track-model.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
The in-memory model of a loaded track and its musical structure: `Track` plus its `Beats`, `Cue`s,
`Keys`, `ReplayGain` and `TrackRecord`. It is read from **every** thread — the RT engine reads the
beatgrid for sync, the GUI reads cues/tags, analysis writes results back — so lifetime is governed by
`GlobalTrackCache` and shared as immutable snapshots. Reading a resolved immutable snapshot is
RT-callable; creating/destroying a `Track` or taking the cache lock is **not**.

## Key files
- `track.cpp/.h` — the aggregate root: metadata + beats + cues + keys + record.
- `globaltrackcache.cpp/.h` — single-instance cache governing `Track` lifetime.
- `beats.cpp`, `beatfactory.cpp` — immutable `Beats` beatgrid snapshot + its constructor.
- `cue.cpp`, `keys.cpp`, `keyfactory.cpp`, `replaygain.cpp`, `bpm.cpp` — cue/key/gain/tempo value types.
- `trackrecord.cpp`, `trackmetadata.cpp` — the persistable metadata record.

## Invariants you MUST respect
- **Track lifetime happens off the RT thread:** `Track` construction/destruction and `GlobalTrackCache`
  locking are GUI/worker-thread work; the RT engine holds a resolved pointer only. `P-17`.
- **RT reads take an immutable snapshot:** the engine reads `Beats`/gain via an immutable shared pointer
  swapped atomically — it never locks the cache or mutates a `Track` on the callback. `P-16`.
- **One canonical home per fact:** the `Track` (and its file tags) is the source of truth; the library DB
  and QML models hold derived copies, reconciled back through here. `P-07`.
- **Single writer per mutable field:** a given track field has one authoritative writer at a time;
  concurrent mutation goes through the track's guarded API, not RT-side. `P-06`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R "Track|Beats|Cue|Key|ReplayGain"` (GoogleTest; `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Constructing/destroying a `Track` or taking the `GlobalTrackCache` lock on a `process()`-reachable path.
- Mutating a `Track`/`Beats` from the RT thread instead of reading an immutable snapshot (`P-16`).
- Forking the source of truth by treating a DB/model copy as canonical (`P-07`).

## Cross-references
Upstream: `src/sources/AGENTS.md` (decode/metadata). Downstream: `src/engine/AGENTS.md` (immutable
beatgrid reads), `src/library/AGENTS.md` (persistence), `src/analyzer/AGENTS.md` (results write-back).
Card: `kanban/architecture/ddd/bounded-contexts/arch-track-model.md`.
