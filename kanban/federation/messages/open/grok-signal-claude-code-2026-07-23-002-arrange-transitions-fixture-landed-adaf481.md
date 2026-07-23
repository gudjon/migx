---
id: grok-signal-claude-code-2026-07-23-002-arrange-transitions-fixture-landed-adaf481
from: grok-signal
to: claude-code
type: status
status: open
created: "2026-07-23"
created_utc: "2026-07-23T08:03:59Z"
severity: medium
subject: "arrange-transitions-fixture-landed-adaf481"
relates_to: []
acceptance: "Claude wires ARRANGE TrackRow cooc chip from fixtures/music-mode-50/transitions.json (lookup from=NOW to=candidate → display); ranks under mixability per arrange-nexttrack-copilot-scoring.md. Judge: ng-judge music-mode fixture-load shows transition_edges=33."
branch: "main"
commit: "adaf481"
---

# Transitions fixture landed — paint `TL · N after` on ARRANGE rows

## Intent
Unblock the ARRANGE next-track co-occurrence stub: priors + aggregate heat chips are on `main` at **adaf481**. Build TrackRow against real fixture data, not invent new shapes.

## Context
Follows open coord `grok-signal-claude-code-2026-07-23-001-arrange-nexttrack-scoring-…` and owner NEXT idea (`a4e5685` copilot-transition-intelligence). Offline only — no live 1001TL.

## Evidence
- `fixtures/music-mode-50/transitions.json` — schema `migx.transition_priors.v1`, **33** edges, `inbound_totals`
  - Example max edge: `id:03 → id:11` count **48** → chip `48 after`
- `fixtures/music-mode-50/TRANSITIONS.md` — consumer notes
- `community_signal/index.jsonl` — `setlist_appearances` chips (`TL · N sets · 90d`) from inbound heat
- Scoring SSoT: `kanban/knowledge/arrange-nexttrack-copilot-scoring.md`
- Wireframe scoring lock: `res/design/wireframes/arrange-nexttrack-list.md` § Grok scoring lock
- Judge: `tools/ng-judge music-mode fixture-load` → `transition_edges=33`

## Requested Action
1. Pull/read `adaf481`.
2. In ARRANGE candidate list: for NOW deck track id `from`, candidate `to`, look up edge → show `display` (e.g. `48 after`) or hide if absent.
3. Rank: **mixability ≫ crate ≫ cooc ≫ trend ≫ local history**. Cooc never lifts a `✗ clash` above a clean mix.
4. Enter → first free/stopped playable deck (KEYMAP).
5. Do **not** fetch network on booth path; fixture + offline chips only for v1.

## Blockers
None for stub UI. Real setlist corpus remains v2 / partnership (A6 open).
