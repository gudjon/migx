# AGENTS.md — effects/ (the effect graph, split across the RT boundary)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-effects-chain.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
The effect graph. The **GUI side** here (`src/effects/`) owns the object model — `EffectsManager`, the
`EffectChain`/`EffectSlot` tree, backends and presets. The **RT side** (`src/engine/effects/`) is what
the engine runs per buffer. State crosses the two through `EffectsMessenger`, a lock-free queue — never
a shared lock. Anything reachable from `EngineEffect::process()` runs on the audio callback thread.

## Key files
- `effectsmanager.cpp/.h` — GUI-side root; owns chains, backends, presets, messenger.
- `effectchain.cpp`, `effectslot.cpp`, `effectparameter.cpp` — the GUI-side chain/slot/param model.
- `effectsmessenger.cpp` — the GUI→RT lock-free message queue (the boundary).
- `backends/effectsbackendmanager.cpp`, `backends/builtin/`, `backends/lv2/`, `backends/audiounit/` —
  effect providers (`audiounit/*.mm` is macOS Obj-C++).
- `presets/effectchainpresetmanager.cpp` — chain preset save/restore.
- `chains/` — `standardeffectchain.cpp`, `quickeffectchain.cpp`, `equalizereffectchain.cpp`, etc.
- RT side (see `src/engine/effects/`): `engineeffectsmanager.cpp`, `engineeffect.cpp`, `engineeffectchain.cpp`.

## Invariants you MUST respect
- **RT thread (hard):** `EngineEffect::process()`-reachable code — **no** alloc/`new`/`std::vector`
  growth, **no** mutex, **no** I/O, **no** blocking. A slow effect is an audible underrun. `P-02`, `AP-11`.
- **State crosses via the messenger, not a lock:** GUI edits reach the RT graph as `EffectsMessenger`
  messages over a lock-free queue; the RT side never dereferences a GUI `EffectSlot`. `P-16`.
- **Object lifetime off the RT thread:** effects are loaded/constructed/destroyed on the GUI thread and
  handed over by pointer — never `new`/`delete` an effect on the callback. `P-17`.
- **Single writer per parameter control:** each effect-parameter `[Group],key` has one authoritative
  writer; others read via `ControlProxy`. `P-06`, `AP-03`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R "Effect|EngineEffect"` (GoogleTest; tests in `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Any allocation, lock, or blocking call on an `EngineEffect::process()`-reachable path (`AP-02`).
- Dereferencing a GUI `EffectSlot`/`EffectChain` from the RT side instead of going through the messenger.
- Constructing/destroying an effect on the callback, or adding a second writer to a parameter control.

## Cross-references
Upstream: `src/control/AGENTS.md` (parameter controls), `src/engine/AGENTS.md` (the graph that runs the
RT side). Card: `kanban/architecture/ddd/bounded-contexts/arch-effects-chain.md`.
