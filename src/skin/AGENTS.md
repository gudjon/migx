# AGENTS.md — skin/ (legacy QWidget skin engine; widgets in src/widget/)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-skin-widgets.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
The legacy QWidget user interface. `SkinLoader` picks a skin and `LegacySkinParser` walks its XML to
build a tree of `WWidget` subclasses — `WPushButton`, `WKnob`, `WSliderComposed`, `WOverview`,
`WWaveformViewer` — each bound to a `ControlObject` through a `ControlWidgetConnection`. GUI-thread Qt
code; it reads/writes the control bus and embeds the waveform viewers, but never touches the audio
thread. The Qt Quick replacement is `src/qml/`.

## Key files
- `skinloader.cpp/.h` — resolves and loads the active skin.
- `legacy/legacyskinparser.cpp/.h` — parses skin XML into the widget tree; `legacy/skincontext.cpp` —
  parse-time context/variable resolution.
- `../widget/wwidget.cpp`, `../widget/wbasewidget.cpp` — base skinnable widget.
- `../widget/wpushbutton.cpp`, `../widget/wknob.cpp`, `../widget/wslidercomposed.cpp` — control widgets.
- `../widget/wwaveformviewer.cpp`, `../widget/woverview.cpp` — embedded waveform / overview.
- `../widget/controlwidgetconnection.cpp` — binds a widget to a `ControlObject` value.

## Invariants you MUST respect
- **GUI-thread only, never the RT path:** widgets are QObjects on the GUI thread; they read controls via
  proxy and must never be touched from or block the audio callback. `P-20`, `AP-14`.
- **Every QObject gets a parent before its `parented_ptr` destructs:** the skin builds a Qt object tree;
  widget ownership follows the parent-tree rule. `P-19`, `AP-13`.
- **Widgets bind through `ControlWidgetConnection`, not rogue control writes:** a widget is a reader/UI
  writer of a `[Group],key`; it does not become a second authoritative writer. `P-06`, `AP-03`.
- **Waveform drawing is delegated:** `WWaveformViewer` hosts the render context; it does not drive
  drawing off the audio period. `P-21`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R "Skin|Widget"` (GoogleTest; `src/test/`). Skins also validate at load.
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Touching a widget from, or blocking, the audio callback (`P-20`, `AP-14`).
- Creating a widget QObject without a parent, or destructing before it has one (`AP-13`).
- Making a widget a second authoritative writer of a control another context owns (`AP-03`).

## Cross-references
Upstream: `src/control/AGENTS.md` (control bindings), `src/waveform/AGENTS.md` (embedded rendering).
Seam: `kanban/architecture/ddd/boundaries/engine-to-waveform.md`. Card:
`kanban/architecture/ddd/bounded-contexts/arch-skin-widgets.md`.
