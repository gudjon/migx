---
id: runbook-ai-ui-migration-loop
type: runbook
title: "AI-assisted UI migration loop — QML modules, DESIGN.md, mechanical judges"
status: active
owner: gudjon
created: "2026-07-19"
lastUpdated: "2026-07-19"
defers_to:
  - kanban/knowledge/ai-code-migration-methodology.md
  - kanban/knowledge/ui-framework-migration-map.md
  - kanban/knowledge/design-md-ui-modernization.md
  - kanban/knowledge/ui-non-modal-error-ux.md
  - kanban/architecture/decisions/ADR-004-ui-stack-qml-vs-rive-vs-react.md
  - kanban/architecture/ddd/bounded-contexts/arch-qml-ui.md
  - res/design/DESIGN.md
  - https://claude.com/blog/ai-code-migration
---

# AI-Assisted UI Migration Loop

This is the operating loop for moving Migx UI toward an agent-friendly QML-primary shell without a
rewrite cliff. It adapts the large-codebase migration pattern from Anthropic's Claude Code migration
writeup: improve the migration process first, then run many small translation batches through a judge.

The target is not a vague "new framework." The current strategy is a **NextGen Agent DJ shadow
shell**: a ghost version of the product that can run beside the current app path, absorb one module at
a time, and eventually become the primary shell only after its judges prove parity and better UX.

The current framework posture is:

- **Surface A:** QML/Qt Quick 6 + C++ proxies + SceneGraph/RHI/Metal path.
- **Surface B:** QML modules first; optional arm's-length web only for non-real-time AI/account/docs.
- **Design system:** `res/design/DESIGN.md` → generated `res/qml/Theme/Theme.qml`.
- **Never migrate:** engine, ControlObject bus, analyzers, library database, or audio deadline logic.

## Closed Loop

| Beat | UI migration meaning | Stable artifact |
|---|---|---|
| Trigger | A component/module is selected for migration | `kanban/tasks/ui-migration-judge-rulebook-inventory.md` or a dossier `PS-*` |
| Capture | Current behavior, CO keys, theme tokens, screenshots/logs, dependency edges | `MODULE.md`, inventory CSV/JSON, EVD notes |
| Intelligence | Judge compares migrated module against old behavior | `qmllint`, `theme-check`, CO parity, screenshot/pixel gate, focused gtest |
| Adjustment | Component lands or rulebook changes; batch queue updates | source diff + updated module contract |

No component is "ported" until the judge exists. A pretty new QML file with no parity check is an open
loop.

## Shadow-Shell Rule

The NextGen Agent DJ shell is a **shadow** until it earns promotion:

- It may read the same sidecars, ControlObjects, theme tokens, and model proxies as the current UI.
- It may propose AI-DJing actions through Layer B intent/ack flows.
- It must not become a second writer for any ControlObject.
- It must not replace a legacy/live-set path until CO parity, pixel/visual acceptance, non-modal error
  behavior, and dogfood launch are green.
- It may ship behind `--new-ui`, a profile flag, or a dedicated QML root; the selected mechanism belongs
  in the first NextGen dossier, not in ad hoc component diffs.

## Per-Module Contract

Before an agent ports a UI component, create or update a module contract with this minimum shape:

```yaml
id: mod-eq
surface: A
source_paths: [res/qml/EqColumn.qml, res/qml/EqKnob.qml]
legacy_paths: []
proxies: [QmlControlProxy]
controls_read: []
controls_write: []
theme_tokens: []
rt_safety: gui_only
judge:
  - just theme-check
  - build/mixxx-test --gtest_filter='<focused-filter>'
  - no blocking modal reachable during live-set operation
  - '<optional visual or CO parity command>'
unknowns: []
```

Keep the contract close to the migrated module when the physical layout exists; until then, store the
inventory in the migration dossier or generated inventory output. The contract is the unit an agent can
understand, own, and verify.

## Batch Order

1. `mod-theme` and `mod-primitives`: prove DESIGN.md → Theme and shared controls.
2. `mod-music-management-mode`: full-screen arrangement/search/next-queue mode with fixture signal
   chips and load-to-free-deck judge.
3. `mod-eq`, `mod-vu`, `mod-tempo`: small CO-bound widgets with fast judges.
4. `mod-deck-shell` and `mod-hotcue`: vertical deck slice without depending on full waveform Metal.
5. `mod-mixer` and `mod-fx`: larger but bounded by existing proxies.
6. `mod-waveform-*`: only after the MTL/OpenGL-pin work has a measured path.
7. `mod-library`, `mod-settings`, `mod-copilot`: Surface B modules and AI chrome.
8. Legacy skin retirement: delete only after parity and dogfood gates pass.

## Agent Rules

- Use `res/design/DESIGN.md` for tokens; do not hardcode a new color when a token exists.
- Reach engine state only through `QmlControlProxy` or typed `Qml*Proxy` objects.
- UI objects stay GUI-thread only; never add an RT-thread dependency to satisfy UI state.
- Prefer a small module batch with a strong judge over a broad visual rewrite.
- Stress-test one module, discard bad attempts, and improve the rulebook before parallelizing.
- Record unknowns as `TODO(ui-port):` with a module id and a judge gap; do not hide them in prose.
- Route recoverable live-set errors to a non-modal surface; a migrated component that can raise a
  blocking modal mid-set is not done.
- For music-management mode, external/community signals must be cached sidecar/fixture inputs in the
  live judge. Network failure is a badge or empty state, not a blocker.

## First Judge Commands

Use these as the initial floor while the stronger visual/CO judges are being built:

```bash
just theme-check
build/migx.app/Contents/MacOS/migx --version
build/mixxx-test --gtest_filter='TrackDAOTest.*:EngineBufferTest.*'
```

For UI-specific work, add at least one of:

```bash
pre-commit run qmllint --all-files --hook-stage manual
pre-commit run qmlformat --all-files --hook-stage manual
```

If a broader `ctest` filter selects unrelated controller or track tests, fall back to a focused gtest
filter and record the reason in the dossier.

## Escalation

Open a dossier when a module migration needs design decisions, source movement, proxy changes, or
visual acceptance. Keep flat tasks only for judge/rulebook/inventory setup or one-file cleanups.
