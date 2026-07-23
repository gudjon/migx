---
id: nextgen-ui-architecture
type: architecture
title: "NextGen UI architecture — a layered, token-driven, agent-optimized QML design system"
status: active
owner: gudjon
created: "2026-07-23"
lastUpdated: "2026-07-23"
related:
  - ADR-007-nextgen-shadow-ui-qml
  - ADR-004-ui-stack-qml-vs-rive-vs-react
  - ai-code-migration-methodology
  - ui-non-modal-error-ux
  - nextgen-dj-ux-modes-and-signal
  - res/design/DESIGN.md
---

# NextGen UI architecture

The NextGen UI is a **layered, token-driven QML design system** built so an agent (Claude/Codex/Grok)
can add, edit, and verify **one bounded module at a time**, and so *every* visual value traces to
`DESIGN.md`. This is the structure the module port follows (`ai-code-migration-methodology`).

## The layers (one-way dependency; each is a directory)
```
res/design/DESIGN.md            ← SSoT: tokens (color, type, space, radius, motion)
        │ gen_theme_from_design.py (lint-gated: just theme-check)
        ▼
res/qml/Theme/Theme.qml         ← generated token singleton (imported as `Theme`)
        ▼
res/qml/nextgen/primitives/     ← NgButton, NgLabel, NgPanel, NgTab … (token-only, no engine)
        ▼
res/qml/nextgen/components/     ← DeckStrip, TrackRow, ModeBar, SignalChips … (primitives + a ViewModel)
        ▼
res/qml/nextgen/modes/          ← PerformMode, ArrangeMode, LibraryMode (compose components)
        ▼
res/qml/nextgen/main.qml        ← the shell: owns the active mode, hosts the modes
```
A layer may only import layers **below** it. No upward or sideways-hidden dependencies. No import of
`src/skin/legacy` or `src/widget` (ADR-007).

## The six invariants (what makes it agent-optimized)
1. **Tokens are the only source of visual values.** No hex/size/font literal in any primitive/component/
   mode — everything reads `Theme.*` (generated from `DESIGN.md`). Enforced by `just theme-check` +
   `just ng-ui-lint` over `res/qml/nextgen/**` (below `Theme.qml`).
2. **Views are dumb; a thin ViewModel binds the engine.** QML renders + emits *intent*; a per-component
   ViewModel binds `ControlObject`s via typed `Qml*Proxy`/`QmlControlProxy` over the `[Group],key` bus.
   **No business logic in QML, no engine call except through a proxy** (ADR-007, P-06 one-writer).
3. **A module is a bounded, self-contained unit.** One directory + a `MODULE.md` contract: purpose,
   tokens used, CO/proxy bindings, every state (incl. loading/empty/error/disconnected), and its judge
   command. Agents work one module; collisions are structurally rare.
4. **Every module runs in a fixture mode.** A component renders headless against a **mock ViewModel**
   (fixture JSON) with no live engine — so the judge (pixel via the headless-CGL harness + CO-trace +
   non-modal check) runs in CI without a club rig. This is the "build the judge first" prerequisite.
5. **Non-modal, always.** No component may raise a blocking modal reachable during a set; recoverable
   errors route to the shared non-modal surface (`ui-non-modal-error-ux`). A blocking dialog is a judge
   failure.
6. **State ownership is explicit.** The engine owns playback (CO); the shell owns the active mode;
   modules are stateless views over proxies. **Switching modes never disturbs playback.**

## Naming & file conventions (agent-legibility)
- One component per file, `PascalCase.qml`; the file name is the type name.
- Explicit typed properties; no deep `parent.parent` chains; no anonymous magic.
- A component pairs with an optional `<Name>Model.qml` (the ViewModel) and a `fixtures/<name>.json`.
- Each module dir carries `MODULE.md` (the contract) — the unit an agent + the judge consume.

## Design tokens beyond color (modern system)
`DESIGN.md` is extended for NextGen to hold not just colors but **spacing scale, radii, typography
scale, and motion (durations/easing)** — so layout and interaction are also token-governed, not
per-component guesses. Mode identity colors (`modePerform/modeArrange/modeLibrary`) live here too.

## Build order (unchanged, now layered)
`Theme/tokens → primitives → components → modes → deck-shell (first product module) → music-management
mode → library → co-pilot → waveform (post-Metal unpin)`. Each lands behind its `MODULE.md` judge.

## Why this is "100% agent-optimized"
Every module is a small, declarative, token-only, fixture-runnable, judge-verified directory with a
written contract. An agent never needs global context to move one piece; the compiler + theme-check +
the per-module judge are the referees (mechanical verification, `ai-code-migration-methodology`). The
human sets DESIGN.md + the mode UX; the agents fill the layers.
