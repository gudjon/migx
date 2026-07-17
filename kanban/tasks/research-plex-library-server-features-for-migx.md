---
id: research-plex-library-server-features-for-migx
type: task
title: "Research Plex (and peers) features that fit Migx — known servers, libraries, music"
status: done
owner: gudjon
priority: medium
initiative: initiative-ai-djing-product
parent_dossier: ""
depends_on: []
authored_by: grok-signal
authored_kind: agent
queued_by: gudjon
queued_at: "2026-07-18"
completed: "2026-07-18"
evidence: "kanban/knowledge/plex-library-server-fit-for-migx.md"
triggered_by: "User request 2026-07-18 — queue research: Plex features that could fit Migx (connect to known servers for libraries)"
created: "2026-07-18"
lastUpdated: "2026-07-18"
related:
  - analyse-world-model-experience-ontology
  - spotify-octave-step2-metadata-oauth
  - analyse-filesystem-driven-architecture
acceptance: |
  A kanban/knowledge note (plex-library-server-fit-for-migx.md or similar) that:
  1. Inventories Plex product surfaces relevant to DJs: Media Server discovery, connect to
     known/shared servers, music libraries, Plexamp, remote vs LAN, playlists/collections,
     metadata agents, API/integrations, multi-user shares.
  2. Maps each feature to Migx layers (A instrument / B agent seams / C intelligence) and
     domains (arch-library-db, EXO hybrid crates, FSL sidecars, co-pilot).
  3. Explicitly separates: library **browse/index** vs **decode/playback** rights (same lesson
     as Spotify: identity + prep without illegal multi-deck stream).
  4. Compares peer options at high level (Jellyfin, Emby, Navidrome, Apple Music/MusicKit,
     local folders) for "connect to known servers".
  5. Recommends 0–3 doable next steps (e.g. read-only library import via Plex API → EXO songs
     as source:plex, no RT path) with out-of-scope list (Plex as second RT deck without rights).
  6. Cites primary docs/APIs; no green-over-red claims.
loop_queue: true
scout_topics:
  - Plex Media Server discovery (local network + account-linked servers)
  - Connect to known/shared servers for music libraries
  - Plexamp / music-specific clients
  - Open/documented PMS API + metadata providers
  - Remote access vs LAN-only (2025–26 Remote Watch Pass; music often exempt)
  - Playlists, collections, ratings → EXO session/crate graph
---

# Research Plex library/server features for Migx

## Intent
Learn what **Plex** (and close self-hosted peers) offer that could fit Migx — especially
**connecting into known servers for libraries** — without confusing catalog/browse with
multi-deck PCM rights.

## Why it fits our relations
- **Layer A library:** expand crate beyond local disk (network library source).  
- **Layer B EXO:** hybrid crates already have `source: local | spotify | hybrid`; a `source: plex`
  (or generic `media_server`) identity maps cleanly to sequence/prep.  
- **Cursor analog:** external workspace / index — Plex is a household media index many DJs already run.

## Seed (pre-research, 2026-07-18)

| Plex surface | First-pass Migx fit |
|---|---|
| Discover / list **known Media Servers** (account + LAN) | “Add library server” prefs UX |
| Music libraries + metadata | Import tracks → library DB + optional EXO ontology |
| Plexamp (music client) | UX patterns for server-backed music, not copy product |
| Documented **PMS API** / custom metadata agents | Read-only connector (worker thread) |
| Playlists / collections / ratings | Session `order` / crate edges |
| Remote vs LAN (video now often paywalled; **music remote often free**) | Prefer LAN for gigs; remote = prep |
| Multi-user shares | Optional later; privacy ADR-005 |

**Out of scope until rights clear:** using Plex decode as a second RT multi-deck stream without
ToS/partner analysis (Spotify lesson).

## Deliverable path
`kanban/knowledge/plex-library-server-fit-for-migx.md`  
Optional federation signal when findings are actionable for Claude.

## Loop instruction (grok-signal)
On Mode A waves, if inbox empty and Metal scout quiet: **advance this task** one section until
acceptance is met or blocked on API doc access.
