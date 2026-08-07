---
id: spotify-octave-step0-contract
type: task
title: "Freeze Octave-style Spotify contract (metadata + prep first)"
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
lastUpdated: "2026-08-07"
acceptance: |
  In/out scope written and pointed from EXO + knowledge notes; dual Spotify multi-deck
  via public APIs deferred; wave-1 is metadata + prep + local multi-deck.
---

# Spotify Step 0 — contract (done)

SSoT for the stepwise plan: `kanban/knowledge/spotify-octave-style-doable-steps.md`  
Landscape: `kanban/knowledge/spotify-dj-integration-landscape-2026.md`

## In scope (core / EXO / CLI)

1. **Metadata identity** — Spotify URIs / ISRC on ontology + FSL later  
2. **Hybrid crates** — local files + Spotify-id tracks in one session graph  
3. **Prep station** — cues/notes/order as **local session state** on any source  
4. **Agent reasoning** — EXO transitions over hybrid sets (no RT)  
5. **Later** — sequential listen via official player surface; OAuth metadata sync (CLI wave-1 landed much of this)

## Deferred / harder (not wave-1 acceptance)

1. Dual-deck overlap of two Spotify catalog streams via public APIs alone  
2. Offline re-host of catalog streams as a core dependency  
3. Stems / record of stream audio without a supported SDK feature  
4. Reverse-engineering closed partner stream clients  

## Product rule

If the user tries two Spotify catalog tracks on decks A/B → offer **sequence Automix / prep** until
a supported dual-stream path exists. True multi-deck remains **local / open audio** for wave 1.

## Verified

- Contract mirrored in EXO fixtures Wave “Spotify hybrid” (schema + session-hybrid).  
- Follow-ons: CLI OAuth + playlist mirrors; prep UI after fixtures.  
