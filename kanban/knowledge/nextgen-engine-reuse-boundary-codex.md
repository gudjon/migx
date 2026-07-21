---
id: nextgen-engine-reuse-boundary-codex
type: knowledge
title: "NextGen engine reuse boundary — Codex verifier map"
status: active
owner: gudjon
authored_by: codex-cli
authored_kind: agent
created: "2026-07-21"
lastUpdated: "2026-07-21"
defers_to:
  - kanban/knowledge/nextgen-shadow-app-proposal.md
  - kanban/knowledge/nextgen-agent-dj-shadow-product.md
  - kanban/knowledge/ui-framework-migration-map.md
  - kanban/runbooks/ai-ui-migration-loop.md
  - kanban/knowledge/ui-non-modal-error-ux.md
  - kanban/architecture/ddd/bounded-contexts/arch-qml-ui.md
related:
  - ADR-007
  - initiative-ui-modernization
  - arch-control-messaging
  - arch-engine-realtime
---

# NextGen engine reuse boundary

## Verdict

NextGen should start as an **in-process QML shell** that reuses the existing `CoreServices`, player
manager, sound manager, library, analysis, ControlObject bus, and QML proxy layer. The clean seam is
not IPC yet. The clean seam is:

```text
NextGen QML root
  -> QmlApplication-like bootstrap
  -> typed Qml*Proxy / QmlControlProxy
  -> ControlObject bus and CoreServices
  -> existing engine, soundio, library, waveform/rendergraph
```

Do not fork the engine, create a second control plane, or let NextGen call engine internals directly.
The first extractable seam is a **shell-selectable QML application bootstrap**: the app can choose a
NextGen QML root without loading `MixxxMainWindow`, legacy skin XML, or `src/widget` surfaces.

## Current boot seam

`src/main.cpp` already has two UI paths:

| Path | Trigger | What it does |
|---|---|---|
| QML path | `args.isQml()` or a configured QML skin in developer mode | Creates `mixxx::qml::QmlApplication`, initializes `CoreServices`, loads a QML root |
| Legacy path | default | Creates `MixxxMainWindow`, loads the QWidget/skin stack, initializes OpenGL/windowing |

That means NextGen does not need to invent an engine host first. It needs a better selector and a
separate QML root or target that keeps the QML bootstrap but avoids legacy widgets as product chrome.

## Coupling risks

| Risk | Evidence in tree | Severing rule |
|---|---|---|
| `QmlApplication` still creates `DlgPreferences` as a QWidget singleton | `QmlApplication::QmlApplication` calls `makeDlgPreferences()` before QML load | Move preferences behind a NextGen-compatible non-modal/settings proxy before NextGen is promoted |
| Some QML types preserve legacy library styling and skin context | `qmllegacylibraryitem.cpp` references LateNight skin/QSS and `SkinContext` | Treat as migration debt; NextGen music management mode must not depend on LateNight skin parsing |
| `QmlApplication` has blocking `QMessageBox` paths | data-corruption gate and input warning lambdas | NextGen live shell must route recoverable errors to non-modal UX; modal startup gates are allowed only before live-set operation |
| Waveform path still has Metal/OpenGL work in flight | `QmlWaveformDisplay` hosts rendergraph/waveform code | Bake off waveform after the MTL path has an honest measured gate, or stub it for shell/module judges |
| ControlObject write ownership can be ambiguous when classic and NextGen both exist | shared `[Group],key` bus | NextGen is either the active UI writer for a module or read-only shadow observer; never dual-write a CO |
| Build target may accidentally pull legacy UI into the product shell | current `mixxx-lib` includes skin/widget sources broadly | ADR-007 should define "no product dependency on legacy skin/widget chrome"; physical CMake split can trail the first proof but must be tracked |

## Recommended first interface

Add a NextGen launch mode or target that selects:

```text
res/qml/NextGen/Main.qml
```

and registers only the QML proxies needed by the first modules. It may link the same libraries at
first, but the product boundary says NextGen modules may depend on:

- `QmlControlProxy` and typed `Qml*Proxy` objects
- `CoreServices` through the existing QML bootstrap only
- DESIGN.md generated `Theme.qml`
- FSL/EXO sidecars through typed models or fixtures

They may not depend on:

- `src/skin/legacy/**` as a runtime styling system
- `res/skins/**` as source-of-truth UI
- QWidget dialogs in a live performance path
- any direct engine calls from QML

## Judge shape

Minimum v0 judge for a NextGen module:

```text
1. launch: build/migx.app/Contents/MacOS/migx --version
2. theme: just theme-check
3. qml: qmllint/qmlformat for touched QML
4. CO trace: fixture-driven read/write round-trip for module-owned controls
5. visual: screenshot/pixel acceptance for the module, or an EVD note explaining why it is stubbed
6. live UX: no blocking modal reachable during live-set operation
7. regression: classic app path still builds/launches
```

For the first shell scaffold, a pass is: app launches a NextGen QML root, reads one deck/library
state, performs one explicit user-acknowledged load or CO write on a free deck, and exits without
modal errors or underruns.

## Feasibility

Feasible, with a staged split:

1. **Selector first:** choose `--new-ui`, `--nextgen`, a profile flag, or a sibling target that loads a
   NextGen root.
2. **Read first:** NextGen observes existing deck/library state through proxies and fixtures.
3. **Write second:** enable explicit user actions for a bounded module, with single-writer claims.
4. **Extract later:** only after module judges exist, physically remove legacy skin/widget dependencies
   from the NextGen target.

The first code seam Claude should inspect is `src/main.cpp` `runMixxx(...)` plus
`src/qml/qmlapplication.*`. The first product seam should be `mod-shell` plus a small QML root, not a
new audio engine.
