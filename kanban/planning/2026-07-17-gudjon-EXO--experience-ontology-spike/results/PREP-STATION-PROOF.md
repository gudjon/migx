# PREP-STATION-PROOF — hybrid local + Spotify URI (Step 1)

**Date:** 2026-07-17  
**Fixture:** `fixtures/sessions/session-hybrid-prep-demo.json`  
**Contract:** `kanban/tasks/spotify-octave-step0-contract.md`  
**Plan:** `kanban/knowledge/spotify-octave-style-doable-steps.md`

## Claim

An agent can **prepare and sequence** a 4-track hybrid set that includes a
**Spotify-URI-only** row using ontology files alone — without stream decode,
without dual Spotify decks, without RT engine.

## Planned order

| # | song_id | source | Camelot | multi_deck |
|---|---------|--------|---------|------------|
| 1 | song-01-deep-intro | local | 8A | yes |
| 2 | song-02-peak | local | 9A | yes |
| 3 | song-04-spotify-uri-only | spotify | 10A | **no** |
| 4 | song-03-cool-down | local | 7A | yes |

## Agent reasoning (offline)

1. **song-01 → song-02** — Same as PS-EXO-01: 8A→9A Camelot-adjacent, energy lift.
   Both `engine_multi_deck` → true dual-deck allowed.

2. **song-02 → song-04** — 9A→10A is Camelot +1 on the minor ring (compatible).
   Energy: local peak outro ~0.28 → SP intro 0.4 → SP drop 0.85 (bridge after peak).
   **Playback policy:** edge is `sequence-only` + harmonic label for ranking —
   product must **not** load song-04 on deck B while song-02 is still dual-mixing
   as if both were local files under a Spotify dual-stream fantasy.
   Practical handoff: finish local peak, then sequential Spotify play (future Step 4)
   or prep-only for now.

3. **song-04 → song-03** — Cool-down after SP bridge. 10A→7A is **not** strict
   Camelot-adjacent; edge uses `next-energy` + `sequence-only` only (honest labeling).
   Resume full engine multi-deck on local cool-down.

## Prep state (session-local, no audio)

| song | cues | role |
|------|------|------|
| song-01 | mix-in @0, phrase-2 @64 | opener |
| song-02 | drop @96 | peak |
| song-04 | intro-end @64, drop @128 | bridge (SP URI) |
| song-03 | mix-in @0 | closer |

## Explicit non-claims

- No Spotify audio bytes in-repo  
- No dual Spotify stream  
- URI `spotify:track:EXO00000000000000000004` is a **fixture identity**, not a live catalog claim  
- Key/energy on song-04 are **hand-authored stubs** (same class as local demo songs)

## Acceptance (Step 1)

- [x] Schema accepts `external_ids.spotify_uri`, `source`, `playback`  
- [x] Hybrid session + prep cues  
- [x] Policy `spotify_multi_deck: false`  
- [x] Agent transition narrative cites harmonic + energy + sequence constraints  
- [ ] OAuth metadata sync (Step 2 — separate task)  
- [ ] Official sequential player (Step 4 — later)  
