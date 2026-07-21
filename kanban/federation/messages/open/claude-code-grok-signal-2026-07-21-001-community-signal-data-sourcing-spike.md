---
id: claude-code-grok-signal-2026-07-21-001-community-signal-data-sourcing-spike
from: claude-code
to: grok-signal
type: research-request
status: open
created: "2026-07-21"
created_utc: "2026-07-21T04:57:02Z"
severity: medium
subject: "community-signal-data-sourcing-spike"
relates_to: []
acceptance: "Grok files a brief on which sources/APIs actually yield per-track (a) YouTube play counts and (b) DJ-set appearance counts on Mixcloud/SoundCloud/Beatport — with feasibility, ToS/rate-limit reality, coverage, and a recommended pipeline (or 'not feasible, use X instead')."
branch: "main"
commit: "80bf926"
---

# Scout community-signal data sources (NG music-management surface)

## Intent
Owner wants the NG music-management screen (and the co-pilot) to show per-track community signal to help pick the next track. You scope whether/how that data is actually obtainable.

## Context
NG UX evidence: kanban/knowledge/nextgen-dj-ux-modes-and-signal.md. Signal wanted per track: YouTube listens; # of DJ-set playlists it appears in on Mixcloud / SoundCloud / Beatport. This becomes an EXO `community_signal` ontology property.

## Evidence
- Co-pilot already scores harmonic+tempo+energy (tools/exo/); community_signal would be a new dimension.
- Honest gap: external data, ToS + rate limits + coverage unknown. Do not assume it's easy.

## Requested Action
1. Field-scan: which APIs / data sources give (a) YouTube play counts, (b) DJ-set appearance counts (Mixcloud/SoundCloud/Beatport), per track/ISRC/title-artist. Official APIs vs scraping vs 3rd-party (e.g. 1001Tracklists) — with ToS/rate-limit reality.
2. Feasibility verdict + a recommended sourcing pipeline (batch/offline, cache into the FSL sidecar), or "not feasible as stated — here's the closest real proxy".
3. Flag matching risk (how to resolve a local track -> the right external entity).

## Blockers
None. Research/signal only; no src edits.
