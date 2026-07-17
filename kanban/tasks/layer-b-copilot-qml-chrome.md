---
id: layer-b-copilot-qml-chrome
type: task
title: "QML chrome for offline co-pilot why-next (Layer B visible)"
status: open
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
parent_dossier: 2026-07-17-gudjon-EXO--experience-ontology-spike
depends_on:
  - spotify-octave-step0-contract
authored_by: grok-signal
authored_kind: agent
triggered_by: "X deep alignment — elevate Layer B visibility"
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  QML (or DeveloperTools) panel shows current song, proposed next, and
  reason bullets from COPILOT-WHY-NEXT.json / intent-inbox; human Ack/Reject
  only. No engine load until explicit future CO path. Theme tokens only.
---

# Layer B co-pilot chrome (open)

Offline path already works:

```bash
just exo-copilot-why
# → results/COPILOT-WHY-NEXT.md + dogfood/intent-inbox.v1.json
```

## Scope

- Read-only QML surface (or Settings/Developer panel) bound to fixture paths or a tiny local file watcher
- Display: current · proposal · reasons · source badge (`LCL` / `SP`)
- Buttons: **Ack** / **Reject** (update intent status in JSON only for dogfood)
- DESIGN.md / Theme tokens — no ad-hoc hex

## Non-goals

- Loading Spotify streams to decks  
- Dual multi-deck for `source=spotify`  
- RT JSON parse  
- Full Layer C LLM (ranking is deterministic offline for now)

## Refs

- `tools/exo/copilot_why_next.py`  
- `kanban/federation/signal/2026-07-17-deep-x-community-alignment.md`  
- EXO dogfood README  
