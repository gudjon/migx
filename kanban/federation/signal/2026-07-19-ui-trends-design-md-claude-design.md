---
id: signal-2026-07-19-ui-trends-design-md-claude-design
type: signal-brief
from: grok-signal
date: "2026-07-19"
relevance: actionable
topics: [design-md, shadcn, claude-design, qml, nextgen, agent-ui]
mapped_to:
  - nextgen-ui-industry-trends-agent-design
  - design-md-ui-modernization
  - nextgen-ui-engine-scout
---

# Industry agent-UI trends vs Migx host choice

**SSoT:** `kanban/knowledge/nextgen-ui-industry-trends-agent-design.md`

## Split

- **Agent industry stack:** DESIGN.md + shadcn/Tailwind + Claude Design → Claude Code (web-first).  
- **Migx Surface A:** still **QML design system** (bind + Metal).  
- **Fit:** steal *process* (tokens, primitives-as-owned-source, Claude Design prototypes); do not steal *host* for decks.

## Claude Design role

Bootstrap aesthetic + design system from mood/layout studies → freeze DESIGN.md → Theme.qml → implement modules in QML. Optional later: same tokens → shadcn Surface B island for co-pilot.

## Preference for us

1. Process: DESIGN.md + Claude Design + anti-slop skill  
2. Host A: QML  
3. Host B (later): shadcn island  
4. Slint optional bake-off; SwiftUI shell no  
