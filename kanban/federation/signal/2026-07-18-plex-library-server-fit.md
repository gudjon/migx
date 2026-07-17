---
id: signal-2026-07-18-plex-library-server-fit
type: signal-brief
from: grok-signal
date: "2026-07-18"
relevance: actionable
topics: [plex, library, media-server, exo, hybrid-crate, navidrome]
mapped_to:
  - kanban/knowledge/plex-library-server-fit-for-migx.md
  - kanban/tasks/research-plex-library-server-features-for-migx.md
  - BaseExternalLibraryFeature
  - world-model-experience-ontology
---

# Signal — Plex/known-server libraries fit Migx

Full note: `kanban/knowledge/plex-library-server-fit-for-migx.md`.

## Bottom line
Plex is a strong **household music index**: connect to **known servers** (account + LAN), browse
**Music** sections, import playlists — same pattern as iTunes/Serato external library features.

## Do
1. Prefs: add known PMS (token / host).  
2. `LibraryFeature` subclass (worker HTTP only).  
3. Resolve to **file path** when NAS mounted → normal engine load.  
4. EXO `source: plex` for hybrid crates; stream-only → sequence/prep.  
5. Design generic enough for **OpenSubsonic/Navidrome** later.

## Don't
Dual-deck pure HTTP streams; RT network; depend on Sonic Analysis; video/Live TV.

## Next implementer
Claude: Step 1–2 spike when free. Codex: RT/token audit.
