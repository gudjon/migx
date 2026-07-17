# Phase plan — EXO

## Wave 1 — schemas (verify: files validate as JSON)
- [x] Add `fixtures/schema/migx.song-ontology.v1.json`  
- [x] Add `fixtures/schema/migx.session-ontology.v1.json`  
- [x] Align with knowledge note §2b/§3  
- [x] Spotify identity fields: `source`, `external_ids.spotify_uri`, `playback`  
- [x] Session prep + hybrid policy (`sequence-only`, `spotify_multi_deck: false`)  

## Wave 2 — hand-author 3 tracks + session
- [x] Three song ontology JSON (Camelot, sections, energy samples — ear/stub OK)  
- [x] One session graph with order + edges  
- [x] song-04 Spotify-URI-only + `session-hybrid-prep-demo.json`  

## Wave 3 — transition proof
- [x] `results/TRANSITION-PROOF.md` — pick next after track 1 with reasons  
- [x] Request P-08 eval from `codex-cli` or Gudjon via federation  
- [x] `results/PREP-STATION-PROOF.md` — hybrid local+SP sequence constraints  

**Gate (Waves 1–3):** proof exists; P-08 PASS; hybrid Step 1 fixtures green  

## Wave 4 — Spotify Octave path (after Step 0 contract)
- [x] Step 0 contract task closed (`kanban/tasks/spotify-octave-step0-contract.md`)  
- [x] Step 1 URI/hybrid fixtures (this wave extension)  
- [x] Step 1b paste-import tool (`tools/exo/spotify_uri_import.py`, `just exo-spotify-import`)  
- [ ] Step 2 OAuth metadata (`kanban/tasks/spotify-octave-step2-metadata-oauth.md`) — optional after paste dogfood  
- [ ] Step 3 prep UI (QML) — list hybrid sessions + paste-import output  
- [ ] Step 4 sequential official player — only after prep UX proven  

**Gate Wave 4:** no dual Spotify stream in core; metadata/prep only until partner/official sequential lane  
**Verify:** `just exo-fixtures-check`
