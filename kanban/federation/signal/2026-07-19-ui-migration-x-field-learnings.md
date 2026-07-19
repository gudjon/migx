---
id: signal-2026-07-19-ui-migration-x-field-learnings
type: signal-brief
from: grok-signal
date: "2026-07-19"
relevance: actionable
topics: [ui, x-ethnography, qml, design-md, electron, modular, migration]
mapped_to:
  - ui-framework-migration-map
  - ADR-004
  - design-md-ui-modernization
method: "X semantic + keyword scout 2025–2026 desktop UI / DESIGN.md / modular agents / Qt6 native"
---

# X field learnings folded into UI migration map

**SSoT map (updated):** `kanban/knowledge/ui-framework-migration-map.md` §X

## One-line synthesis

Public discourse **splits** Electron-for-DX vs native-for-feel; **converges** on DESIGN.md for agents, modular worktrees, and hybrid native+WebKit — not “one framework for everything.”

## Locked by X (for Migx)

| Lock | Why X supports it |
|---|---|
| QML-primary decks | Qt/QML praise; journeys *back* from WebEngine; C++/Qt6 anti-Electron AI shells |
| No Electron dual-deck | Anti-slop + continuous GPU work leaves layered web kits |
| DESIGN.md before mass port | “DESIGN.md controls the UI” is mainstream agent practice |
| Modules + evals + worktrees | Modular agent systems; stack churn survival |
| WebView island only | Hybrid native host + WebKit pattern |
| Waveforms metal-close | GPU-first visual tools discourse |

## Explicitly *not* locked by X

SwiftUI rewrite as default; Rive as shell; Flutter desktop for DJ waveforms.

## Next process step (still)

Owner ADR-004 accept → RULEBOOK + stress-test (Theme + one control) — now with §X as the field annex.
