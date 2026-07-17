# AGENTS.md — qml/ (new Qt Quick UI and its C++ proxies; QML in res/qml/)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-qml-ui.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
The new Qt Quick user interface. `QmlApplication` boots the QML engine and registers C++ proxy objects —
`QmlControlProxy` (a `[Group],key` binding), `QmlPlayerProxy`, `QmlEffectsManagerProxy`, `QmlLibraryProxy`,
`QmlWaveformDisplay` — that the `.qml` files in `res/qml/` (`Deck.qml`, `Mixer.qml`, `EffectUnit.qml`,
the `Library` and `Theme` modules) bind against. GUI-thread Qt Quick code; it renders through the Qt
scene graph and reaches the engine only through the control bus and proxies.

## Key files
- `qmlapplication.cpp/.h` — boots the QML engine; registers proxies/types.
- `qmlcontrolproxy.cpp/.h` — QML-facing `[Group],key` control binding.
- `qmlplayerproxy.cpp`, `qmlplayermanagerproxy.cpp` — deck/player state for QML.
- `qmleffectsmanagerproxy.cpp`, `qmllibraryproxy.cpp`, `qmlconfigproxy.cpp` — effects/library/config access.
- `qmlwaveformdisplay.cpp`, `qmlwaveformoverview.cpp` — Qt Quick waveform items.
- `qml_owned_ptr.h` — QML/C++ ownership helper. QML: `../../res/qml/main.qml`, `Deck.qml`, `Mixer.qml`, …

## Invariants you MUST respect
- **GUI-thread only:** proxies are QObjects on the GUI/QML thread; they read the control bus and must
  never be touched from or block the audio callback. `P-20`, `AP-14`.
- **Reach the engine only via ControlObject / proxies:** QML binds `QmlControlProxy` and the typed
  proxies; it never calls engine internals or becomes a rogue second writer of a control. `P-06`, `P-30`, `AP-03`.
- **QObject ownership rule holds through QML:** C++-owned proxy/model objects handed to QML follow the
  parent/`qml_owned_ptr` ownership contract. `P-19`, `AP-13`.
- **Rendering runs on the scene graph, not the audio clock:** `QmlWaveformDisplay` draws via
  `src/rendergraph/` on the display clock; it never gates or is gated by the audio deadline. `P-21`, `P-23`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R Qml` (GoogleTest; `src/test/`). QML also validates at engine load.
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Touching a proxy from, or blocking, the audio callback (`P-20`, `AP-14`).
- Reaching engine internals from a proxy/QML instead of a `ControlObject`/typed proxy (`P-30`).
- Handing a C++ object to QML without a defined ownership (parent / `qml_owned_ptr`) contract (`AP-13`).

## Cross-references
Upstream: `src/control/AGENTS.md` (control bus), `src/waveform/AGENTS.md` + `src/rendergraph/AGENTS.md`
(rendering). Seam: `kanban/architecture/ddd/boundaries/engine-to-waveform.md`. Card:
`kanban/architecture/ddd/bounded-contexts/arch-qml-ui.md`.
