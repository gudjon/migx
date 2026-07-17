# tools/exo — experience ontology helpers

## `spotify_uri_import.py`

Paste Spotify track URIs/URLs into EXO song ontology stubs.

- **No network** — does not call Spotify APIs  
- **No playback** — `playback.mode=prep_only`, `multi_deck_allowed=false`  
- **Identity SSoT** — `external_ids.spotify_uri`  

```bash
# Write song stubs + a hybrid prep session from a paste file
just exo-spotify-import

# Or explicitly:
python3 tools/exo/spotify_uri_import.py \
  --paste kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/import/sample-paste.txt \
  --out-dir kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/songs/imported \
  --session-out kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/sessions/session-paste-import-demo.json \
  --session-id session-paste-import-demo

# Re-check written files
python3 tools/exo/spotify_uri_import.py \
  --paste …/sample-paste.txt \
  --out-dir …/fixtures/songs/imported \
  --check
```

Contract: `kanban/tasks/spotify-octave-step0-contract.md`  
Plan: `kanban/knowledge/spotify-octave-style-doable-steps.md`
