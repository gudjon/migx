---
id: layer-b-copilot-qml-chrome
type: task
title: "QML chrome for offline co-pilot why-next (Layer B visible)"
status: done
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

# Layer B co-pilot chrome (done — dogfood)

## Landed

| Piece | Path |
|---|---|
| Settings category | `res/qml/Settings/CoPilot.qml` |
| Wired in | `res/qml/Settings.qml` → **Co-Pilot (dogfood)** |
| Fixture for QML | `res/qml/CoPilot/fixture_why_next.json` (copied by `just exo-copilot-why`) |
| Offline ranker | `tools/exo/copilot_why_next.py` |

## UX

- Current song + source badge (`LCL`/`SP`) + Camelot  
- Proposal + relation + score + multi_deck flag  
- Why bullets (Explain)  
- **Ack / Reject / Reset** — UI status only (no CO write)  
- Reload fixture + Open JSON…  

## Verify

```bash
just exo-copilot-why   # refresh JSON + QML fixture
# Launch Migx → Settings → Co-Pilot (dogfood)
```

## Still out of scope

Engine load path, Spotify stream, dual multi-deck SP, Layer C LLM.
