---
id: spotify-octave-step0-contract
type: task
title: "Freeze Octave-style Spotify contract (no dual-stream in core)"
status: done
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
parent_dossier: 2026-07-17-gudjon-EXO--experience-ontology-spike
depends_on: []
authored_by: grok-signal
authored_kind: agent
triggered_by: "Octave concept doc + spotify-octave-style-doable-steps"
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  In/out scope written and pointed from EXO + knowledge notes; dual Spotify multi-deck
  and DRM rip/cache explicitly out of core.
---

# Spotify Step 0 — contract (done)

SSoT for the stepwise plan: `kanban/knowledge/spotify-octave-style-doable-steps.md`  
Landscape (partner reality): `kanban/knowledge/spotify-dj-integration-landscape-2026.md`

## In scope (core / EXO)

1. **Metadata identity** — Spotify URIs / ISRC on ontology + FSL later  
2. **Hybrid crates** — local files + Spotify-id tracks in one session graph  
3. **Prep station** — cues/notes/order as **local session state** on any source  
4. **Agent reasoning** — EXO transitions over hybrid sets (no RT, no stream decode)  
5. **Later (not this task)** — sequential listen via official player surface; OAuth metadata sync  

## Out of scope (core — never “just ship”)

1. Dual-deck / overlap mix of two Spotify streams via public APIs  
2. Offline full-track Spotify locker / re-host / rip  
3. Stems or recording of Spotify audio in core  
4. Reverse-engineering partner (djay/Serato/rekordbox) stream SDKs  
5. Grey-zone circumvention modules as a v1 dependency  

## Product rule

If the user tries two Spotify tracks on decks A/B → offer **sequence Automix / prep**,  
not silent illegal dual stream. True multi-deck remains **local / open audio**.

## Verified

- Contract mirrored in EXO fixtures Wave “Spotify hybrid” (schema + session-hybrid).  
- Follow-ons: `spotify-octave-step2-metadata-oauth` (open), prep UI after fixtures.  
