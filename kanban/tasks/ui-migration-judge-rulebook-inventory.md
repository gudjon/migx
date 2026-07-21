---
id: ui-migration-judge-rulebook-inventory
type: task
title: "Build the UI migration judge, rulebook, and module inventory"
status: open
owner: gudjon
priority: high
initiative: initiative-ui-modernization
parent_dossier: null
depends_on:
  - ADR-004
  - ui-framework-migration-map
  - design-md-ui-modernization
  - ai-code-migration-methodology
  - ui-non-modal-error-ux
  - nextgen-engine-reuse-boundary-codex
  - nextgen-music-management-mode
authored_by: codex-cli
authored_kind: agent
triggered_by: "2026-07-19 owner request: make the next UI framework migration systematic and agent-friendly"
created: "2026-07-19"
lastUpdated: "2026-07-19"
acceptance: |
  A UI migration rulebook exists; a generated inventory maps QML, legacy skin/widget, proxy, CO, and
  theme-token edges into module IDs; at least one small module has a MODULE contract and a passing
  mechanical judge; the NextGen shadow-shell and music-management mode have explicit module
  contracts; no broad port begins before these artifacts exist.
---

# UI Migration Judge / Rulebook / Inventory

Migx should port UI components into the QML-primary, DESIGN.md-driven framework one bounded module at
a time. The next undertaking is not "rewrite the UI"; it is to build the migration harness that lets
Claude, Codex, and Grok move components safely.

## Required Artifacts

| Artifact | Purpose | Candidate path |
|---|---|---|
| Migration rulebook | Canonical QML binding/theme/RT-safety rules for agents | `kanban/architecture/ui-migration-RULEBOOK.md` |
| Module inventory | Mechanical list of `.qml`, legacy skin/widget, proxy, CO, token, and dependency edges | `kanban/architecture/ui-migration-inventory.json` |
| Gap inventory | Skin-only, QWidget-only, no-QML-twin, no-judge, and no-token gaps | `kanban/architecture/ui-migration-GAPS.md` |
| Judge harness | Commands that prove behavior/visual/CO parity for each migrated module | `tools/ui/` or focused gtests |
| First module contract | One small stress-test module with `MODULE.md` and passing judge | preferably `mod-eq`, `mod-vu`, or `mod-tempo` |
| Music-mode contract | Full-screen next-queue mode with tags/playlists/signal chips and no-network live judge | `mod-music-management-mode` |

## First Batch

1. Inventory `res/qml/`, `src/qml/`, `res/skins/`, `src/skin/legacy/`, and `src/widget/`.
2. Assign initial module IDs using `kanban/knowledge/ui-framework-migration-map.md`.
3. Write the one-page rulebook before editing component code.
4. Choose a tiny CO-bound module and run one disposable stress-test.
5. Draft `mod-music-management-mode` as the first product-mode contract, even if its first code uses
   fixtures.
6. Keep or discard the code based on the judge; keep the improved rulebook either way.

## Guardrails

- Cite `P-06`, `P-20`, `P-21`, `P-23`, and `ADR-004`; do not restate house physics.
- Do not introduce React/Electron/Rive as a primary shell unless ADR-004 is amended.
- Do not move files just to make the inventory neat; first migrate in place, then reorganize.
- Every module needs a judge command. `qmllint` alone is not behavioral parity.
- External/community music signals are cached fixture or sidecar data in judges; no live network call
  belongs in the club hot path.
- Full-screen music mode is not a modal dialog. It must preserve deck state and return to performance
  mode with one action.

## Verification Floor

```bash
just theme-check
build/migx.app/Contents/MacOS/migx --version
build/mixxx-test --gtest_filter='TrackDAOTest.*:EngineBufferTest.*'
./kanban/scripts/migx-fed audit --strict
```

Add `qmllint`, screenshot/pixel, or CO parity commands as soon as the first stress-test module exists.
