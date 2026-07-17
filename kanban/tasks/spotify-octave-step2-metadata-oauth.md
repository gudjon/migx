---
id: spotify-octave-step2-metadata-oauth
type: task
title: "Spotify OAuth + metadata-only playlist sync (no playback)"
status: open
owner: gudjon
priority: medium
initiative: initiative-ai-djing-product
parent_dossier: 2026-07-17-gudjon-EXO--experience-ontology-spike
depends_on:
  - spotify-octave-step0-contract
authored_by: grok-signal
authored_kind: agent
triggered_by: "spotify-octave-style-doable-steps Step 2"
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  Optional Dev Mode Spotify app: user can OAuth and see playlists as source=spotify
  rows (URI + title/artist metadata). No load-to-deck stream. Tokens in keychain.
  Disconnect purges tokens. Worker-thread only (no RT). Document 5-user Dev Mode wall.
---

# Step 2 — metadata OAuth (not started)

Depends on Step 0 contract + Step 1 fixtures (done under EXO).

## Scope

- PKCE OAuth; secure token storage  
- Sync Liked + user playlists → ontology-friendly rows (`external_ids.spotify_uri`)  
- QML or library list browse only  
- **No** Web Playback / dual deck / offline locker  

## Non-goals

Playback of any kind; extended quota public launch.

## Refs

- `kanban/knowledge/spotify-octave-style-doable-steps.md`  
- Spotify Developer Policy §III.7 (mix ban)  
