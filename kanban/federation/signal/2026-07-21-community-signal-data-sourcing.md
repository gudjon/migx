---
id: signal-2026-07-21-community-signal-data-sourcing
type: signal-brief
from: grok-signal
date: "2026-07-21"
relevance: actionable
topics: [nextgen, community-signals, youtube, mixcloud, soundcloud, beatport, fsl, exo]
mapped_to:
  - nextgen-community-signal-data-sourcing
  - nextgen-modes-library-multideck
  - initiative-ai-djing-product
method: "Official API docs + field ToS/quota notes (YT Data API v3, SC, Mixcloud, Beatport v4, 1001TL)"
closes_mail: claude-code-grok-signal-2026-07-21-001-community-signal-data-sourcing-spike
---

# Community-signal data sources — feasibility brief

**SSoT:** `kanban/knowledge/nextgen-community-signal-data-sourcing.md`  
**Closes:** `claude-code-grok-signal-2026-07-21-001-community-signal-data-sourcing-spike`

## One-line

**YouTube views: yes (batch offline, cache video IDs).** **“N DJ sets on Mixcloud/SC/Beatport”: not as stated** — Beatport = charts; SC = track plays; Mixcloud = crawl sections only. **True set heat ≈ 1001Tracklists-class feed (partner/license);** v1 chips = YT + BP chart + SC plays + local history with honest labels.

## Answers to acceptance

| Ask | Result |
|---|---|
| (a) YT play counts per track | **Feasible** — `videos.list` + `statistics.viewCount`; 50 IDs/1 unit; search expensive (100 units) |
| (b) DJ-set counts MC/SC/BP | **Not feasible as multi-API reverse index** — use setlist proxy (1001TL) for “sets”; BP chart + SC plays as alternate heat |
| ToS / rate | YT 10k units/day default; SC stream cap 15k/24h (metadata loose); Mixcloud Retry-After; 1001TL anti-scrape |
| Pipeline | Offline FSL/EXO sidecar; PREP enrich; never RT; match via ISRC/MBID then string; confidence gates chips |
| Matching | ISRC > MBID > BP id > videoId > fuzzy title/artist; no silent first-hit YT attach mid-set |

## Fleet ask

- **Claude:** EXO `community_signal` property + track-card chips (mock until enrich job).  
- **Owner:** license setlist data vs ship v1 without “N sets”.  
- **No new handoff** this wave (research closed in-mail).

## Non-goals

Live booth multi-scrape; ranking only on YT views; claiming unified MC+SC+BP set counts without a real index.
