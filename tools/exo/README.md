# tools/exo — experience ontology helpers

Offline Layer B tooling. **No RT engine, no network required** for ranking/import.

| Tool | Purpose |
|---|---|
| `spotify_uri_import.py` | Paste Spotify URIs → prep-only song ontology stubs |
| `check_fixtures.py` | Structural + policy checks on EXO fixtures |
| `copilot_why_next.py` | Explainable next-track proposal (Predict → Ask → Explain) |

```bash
just exo-fixtures-check
just exo-spotify-import
just exo-copilot-why          # hybrid + copies JSON → res/qml/CoPilot/fixture_why_next.json
just exo-copilot-why-mirror   # dogfood session-mirror + same QML fixture copy
# Then: Migx Settings → Co-Pilot (dogfood)
```

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
