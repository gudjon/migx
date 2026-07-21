---
id: initiative-ui-modernization
type: initiative
status: active
title: "UI modernization + legacy retirement — QML-first, Metal render"
owner: gudjon
dossier:
  - kanban/planning/2026-07-17-gudjon-DUI--design-md-theme-qml-spike
tasks:
  - kanban/tasks/ui-migration-judge-rulebook-inventory.md
  - kanban/tasks/nextgen-music-management-mode.md
depends_on: []
blocks: []
pm_overlay:
  hypothesis: "If we retire the legacy QWidget skin stack (src/skin/legacy + src/widget) in favour of a QML-first UI and move the waveform render path to Metal/SceneGraph, then Migx has a modern, native, Apple-Silicon-fast UI that is also the foundation for the AI-DJing (DESIGN.md-driven, agent-legible) interface — with a smaller, cleaner codebase."
  primary_metric: "legacy LOC retired; QML feature-parity for the core deck/mixer surface; waveform render on Metal (no forced-OpenGL) beating the EVD-0001 baseline"
  guardrail: "each retirement/switch behind a build+test gate (ADR-002); no correctness or RT-safety regression; visual parity verified"
  validation: "per-dossier build+test + GUI verification; perf dossiers scored vs EVD-0001"
created: "2026-07-17"
lastUpdated: "2026-07-19"
---

# UI modernization + legacy retirement

The cleanup-that-is-also-product thread. As a true hard fork (ADR-002) Migx is free to retire legacy
subsystems; ADR-004 sets the direction: **QML-primary** for the real-time surface. Candidate inventory:
`kanban/tasks/prune-outdated-legacy-code.md`; UI-stack rationale: `ADR-004`.

## Problem
The biggest, most dated subsystem is the legacy QWidget/XML/QSS skin engine (`src/skin/legacy/` +
`src/widget/`, ~225 files) running beside the newer QML UI — dual-stack maintenance burden and off the
AI-DJing QML-first direction. And the default waveform path is stuck on forced-OpenGL (no Metal).

## Hypothesis
See `pm_overlay`. Retiring legacy + going QML/Metal is *the same work* as building the AI-DJing UI
(ties to `design-md-ui-modernization` — DESIGN.md tokens → `Theme.qml`).

## Scope → dossiers (register prefixes when opened; suggest `UIX`)
| Dossier | First move |
|---|---|
| AI UI migration harness | Build rulebook + module inventory + first mechanical judge before broad component ports. |
| Retire deprecated waveform renderers | Remove `src/waveform/renderers/deprecated/` + `widgets/deprecated/` (dead paths), build+test gate. |
| Waveform → Metal/SceneGraph | Solve offscreen-render-on-Metal (the `coreservices.cpp:826` blocker), adopt SceneGraph backend; scored vs `EVD-0001`. Overlaps the MTL optimization dossier. |
| QML deck/mixer parity | Bring the core performance surface to QML; then retire `src/skin/legacy` + most of `src/widget`. Biggest, sequenced last. |
| Qt6-only | Drop Qt5 compat shims. |

## The closed loop (MG-1)
Trigger: a retirement/switch dossier. Capture: build+test result + (for render) a benchmark vs EVD-0001.
Intelligence: parity/perf verdict. Adjustment: the legacy code deleted / the path switched, gated green.

## Status
`active`. DUI Theme.qml spike executed; the next migration step is the harness, not a rewrite:

1. **Judge / rulebook / inventory** — `kanban/tasks/ui-migration-judge-rulebook-inventory.md` and
   `kanban/runbooks/ai-ui-migration-loop.md`.
2. **NextGen music-management mode** — `kanban/tasks/nextgen-music-management-mode.md`; full-screen
   arrangement/next-queue mode with tags, playlist memberships, cached community signal chips, and
   load-to-free-deck judge.
3. **DUI** design tokens -> Theme.qml stays the design SSoT loop.
4. **Small QML module stress-test** (`mod-eq`, `mod-vu`, or `mod-tempo`) with CO parity before deck work.
5. Dead-code retirement only after parity gates prove the QML module path.
6. Metal render stays under MTL; waveform module migration waits for that measured path.
