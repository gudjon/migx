---
id: grok-signal-claude-code-2026-07-23-001-arrange-nexttrack-scoring-answers-and-cooccurren
from: grok-signal
to: claude-code
type: coord
status: open
created: "2026-07-23"
created_utc: "2026-07-23T07:57:34Z"
severity: medium
subject: "arrange-nexttrack-scoring-answers-and-cooccurren"
relates_to: []
acceptance: "Claude builds ARRANGE v1 per arrange-nexttrack-copilot-scoring.md: crate-scoped QML mixability rank + hero why; chips offline stubs only; Enter free-deck; KEYMAP compliant."
branch: "main"
commit: "b44ab13"
---

## Intent
Unblock Claude's ARRANGE next-track-list draft: lock the four open design questions and encode the owner idea (NEXT from DJ-playlist co-occurrence + similar + trend) as layered scoring policy.

## Context
Claude holds `res/design/wireframes/arrange-nexttrack-list.md` for review. Owner idea: co-pilot pick after processing tons of DJ playlists (same/similar song transitions) and trending tracks.

## Evidence
- `kanban/knowledge/arrange-nexttrack-copilot-scoring.md` (this brief)
- `tools/exo/copilot_why_next.py` — port Camelot/tempo/energy reasons
- `nextgen-community-signal-data-sourcing.md` — offline chips; setlist cooc is v2 feed
- `res/design/KEYMAP.md` — ⌘2 ARRANGE; Enter free deck; no bare 1–0 for modes
- Judge floor: no-network ARRANGE

## Requested Action
1. Treat open Qs as answered per scoring brief §1 (crate source, QML mixability v1, mixability before chips, Enter→free deck).
2. Implement first slice: TrackRow + hero NEXT + QML mixability rank; stub `TL · N after` from fixture transitions if easy.
3. Do not block on live YT/Mixcloud; co-occurrence/trend are offline layers with capped weights under mixability.
4. Cite KEYMAP for any new shortcut.

## Blockers
None for v1 mixability slice. Real setlist corpus remains owner/partnership for v2.
