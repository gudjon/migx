---
id: spotify-octave-step1b-paste-import
type: task
title: "Paste-import Spotify URIs into EXO prep stubs (no OAuth)"
status: done
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
parent_dossier: 2026-07-17-gudjon-EXO--experience-ontology-spike
depends_on:
  - spotify-octave-step0-contract
authored_by: grok-signal
authored_kind: agent
triggered_by: "continue Octave Spotify path; dogfood before OAuth"
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  Offline tool turns pasted Spotify track URIs/URLs into song ontology stubs
  with multi_deck_allowed=false; optional hybrid session; just recipes green.
---

# Step 1b — paste-import (done)

## Landed

| Artifact | Path |
|---|---|
| Tool | `tools/exo/spotify_uri_import.py` |
| Fixture check | `tools/exo/check_fixtures.py` |
| Sample paste | `…/fixtures/import/sample-paste.txt` |
| Imported songs | `…/fixtures/songs/imported/song-sp-*.ontology.json` |
| Session | `…/fixtures/sessions/session-paste-import-demo.json` |
| Recipes | `just exo-spotify-import`, `just exo-fixtures-check` |

## Verified

```
just exo-fixtures-check   # ALL EXO FIXTURES OK
just exo-spotify-import   # write + --check PASS
```

## Next

- Step 2 OAuth still optional (`spotify-octave-step2-metadata-oauth`)  
- Or Step 3: QML prep list over hybrid sessions  
