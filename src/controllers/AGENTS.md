# AGENTS.md — controllers/ (MIDI/HID/bulk hardware bound to controls via scripts)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-controllers-mapping.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
Hardware in, controls out. `ControllerManager` enumerates and opens each `Controller` (MIDI, HID, USB
bulk); input events run through a declarative `LegacyControllerMapping` and its JavaScript, and the
script reaches the rest of Migx **only** by writing `ControlObject`s. The QJSEngine and the I/O threads
are worker/GUI — never the audio callback. Mappings live in data (`res/controllers/`), not C++.

## Key files
- `controllermanager.cpp/.h` — enumerates/opens controllers; owns the polling thread.
- `controller.cpp/.h` — abstract device: receive events, send output.
- `midi/midicontroller.cpp`, `hid/hidcontroller.cpp`, `bulk/bulkcontroller.cpp` — per-transport bindings.
- `scripting/legacy/controllerscriptenginelegacy.cpp` — the mapping QJSEngine.
- `legacycontrollermapping.cpp`, `legacycontrollermappingfilehandler.cpp` — parsed declarative mapping.
- `softtakeover.cpp` — prevents value jumps when a knob re-engages.

## Invariants you MUST respect
- **Mappings are declarative data:** device→control behaviour lives in `res/controllers/` XML+JS, not
  compiled `if` chains; no hard-coded tuning/mapping constants in C++. `P-29`, `AP-15`.
- **Scripts reach the engine only via ControlObject:** a mapping script never calls engine internals
  directly — it writes `[Group],key` controls, governed by the single-writer rule. `P-30`.
- **Never on the RT thread:** device I/O and the QJSEngine run on worker/GUI threads; values reach the
  RT engine through the lock-free control bus, never a synchronous callback. `P-17`, `P-20`.
- **Single writer:** a script must not become a second authoritative writer of a control the engine or a
  player already owns. `P-06`, `AP-03`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R Controller` (GoogleTest; e.g. controller-engine/mapping tests in
  `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Hard-coding a device mapping or tuning value in C++ instead of the `res/controllers/` data (`AP-15`).
- Reaching engine internals from a script instead of writing a `ControlObject` (`P-30`).
- Doing device I/O or running the QJSEngine on the audio callback, or adding a rogue second writer.

## Cross-references
Upstream/downstream: `src/control/AGENTS.md` (the `ControlObject` bus scripts read and write).
Mappings: `res/controllers/`. Card: `kanban/architecture/ddd/bounded-contexts/arch-controllers-mapping.md`.
