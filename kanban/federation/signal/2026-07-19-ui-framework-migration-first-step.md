---
id: signal-2026-07-19-ui-framework-migration-first-step
type: signal-brief
from: grok-signal
date: "2026-07-19"
relevance: actionable
topics: [ui, qml, migration, design-md, adr-004, modular]
mapped_to:
  - ui-framework-migration-map
  - ADR-004
  - design-md-ui-modernization
method: "Repo UI inventory + ADR-004 + Anthropic AI migration process + light X native-vs-web discourse"
---

# UI migration first step — framework + modular map

**Full map:** `kanban/knowledge/ui-framework-migration-map.md`

## Decision (recommended)

| Surface | Framework |
|---|---|
| Decks / waveforms / mixer | **Qt Quick 6 (QML)** + C++ proxies + Metal render host |
| Library / settings / co-pilot | **QML modules**; optional WebView only for pure AI chat |
| Design system | **DESIGN.md → Theme.qml** |
| Motion | Optional **Rive** embeds |

**Not** Electron/Flutter full shell. **Not** SwiftUI rewrite as step 1. Legacy **QWidget skins = source to retire**, not target.

## Modular units (start here)

Stress-test order: `mod-theme` + `mod-primitives` → `mod-eq`/`mod-vu` → `mod-deck-shell` → mixer/fx → waveforms (after MTL) → library/settings → **mod-copilot**.

Each module: CO/proxy contract, no RT, MODULE.md, mechanical acceptance.

## AI migration process (Anthropic-adapted)

1. Judge (CO parity + launch)  
2. Rulebook + gap inventory + dep map  
3. Stress-test one module, **discard**, fix rules  
4. Batch translate with adversarial review  
5. Compile / dogfood / match  

## Ask of owner / Claude

1. Accept or amend **ADR-004**.  
2. Open initiative + stress-test dossier (DESIGN.md Theme + one control).  
3. Do **not** block on full skin delete before green QML dual-deck dogfood.

## Relation to “get running”

Dogfood QML shell on M4 is the **judge bootstrap**. Migration without a launching app fails step 0.

## Update 2026-07-19
X ethnography annexed as **§X** in `ui-framework-migration-map.md` + signal `2026-07-19-ui-migration-x-field-learnings.md`.
