---
id: signal-2026-07-19-nextgen-agent-dj-shadow-fleet-discussion
type: signal-brief
from: grok-signal
date: "2026-07-19"
relevance: actionable
topics: [nextgen, agent-dj, strangler, shadow, ui, design-md, federation]
mapped_to:
  - nextgen-agent-dj-shadow-product
  - ui-framework-migration-map
  - ADR-004
method: "Owner thesis + deep X by domain + ADR/UI map; fleet discussion open"
---

# Fleet discussion: NextGen Agent DJ as shadow product

**SSoT:** `kanban/knowledge/nextgen-agent-dj-shadow-product.md`

## Thesis
Ship a **ghost/shadow** Agent DJ surface (module-by-module, DESIGN.md, agent-native) while classic Migx stays production. Shared engine + CO bus; NextGen owns only the presentation shell.

## X (by domain) — short
| Domain | Field | Default |
|---|---|---|
| Migration | Strangler / shadow / canary | Module flags, not big-bang |
| Agents | CLAUDE.md + skills + worktrees + modular evals | MODULE.md + claims |
| UI stack | Native/Qt vs Electron; hybrid WebKit | QML host; no Electron decks |
| Design | DESIGN.md = agent UI brain | Tokens before mass UI |
| GPU | Metal-close when graphics are the product | Waveforms under MTL |
| AI product | AI inside native shells | Co-pilot as QML module |

## Recommended packaging
**Option A:** cmake target / binary `migx-agent` (or AgentDJ) in monorepo, shared libs.

## Discussion questions
See §6 of knowledge doc — Claude: scaffold feasibility; Codex: judge + claims; Owner: A/B/C/D + first module.

## Non-goals
Engine rewrite; Electron dual-deck; day-1 LateNight parity; SwiftUI v1 without ADR reopen.
