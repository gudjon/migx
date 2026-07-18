# JOURNAL — EXO

## 2026-07-17
- Scaffolded; prefix EXO registered.
- DRI: antigravity-cli. Camelot already in keyutils — no DSP rewrite.
- FSL export can follow; hand-author fixtures first to unblock graph proof.

## 2026-07-17 (long harness execution — gudjon/agent)
- Schemas: fixtures/schema/migx.song-ontology.v1.json + session v1
- Three hand-authored songs (8A / 9A / 7A) + session-3track-demo.json
- results/TRANSITION-PROOF.md: after song-01 prefer song-02 (8A→9A energy up)
- P-08: request independent eval from codex-cli (federation mail)
- All fixture JSON parses clean under python json.load

## 2026-07-17 (fleet conductor + codex drain)
- `migx-fleet-conductor.py` + `migx-codex-drain.py` live; `just fleet` / `just fleet-drain`
- P-08 automated eval: **PASS** → `results/P08-EVAL-codex.md`
- Fixed session edge song-02→song-03: relation `next-energy` only (not false harmonic label)

## 2026-07-17 (music-WM signal triage)
- Closed grok signal-handoff: folded into EXO as **post-spike research**
- Task: `kanban/tasks/research-analyzer-structure-energy-mlx.md` (license + MLX before model import)
- Dogfood offline co-pilot fixtures: `fixtures/dogfood/` (session-mirror + intent-inbox)
- Production AnalyzerStructure/Energy remains later; hand-author fixtures stay valid v1 path

## 2026-07-17 (codex-cli independent evaluation)
- P-08 verdict: PASS for requested transition `song-01-deep-intro` (8A) -> `song-02-peak` (9A).
- Reason: Camelot-adjacent minor-ring move plus coherent low-outro -> moderate-intro -> high-peak energy lift.
- Gap noted: session edge vocabulary should not label `song-02` -> `song-03` as strict harmonic compatibility
  when the note says `9A -> 7A` is not adjacent.

## 2026-07-17 (Octave-style Spotify Steps 0–1 — grok)
- Contract: `kanban/tasks/spotify-octave-step0-contract.md` (done) — dual SP stream out of core
- Schema: song `source` / `external_ids` / `playback`; session `prep` / `policy` / `sequence-only`
- Fixture: `song-04-spotify-uri-only` + `session-hybrid-prep-demo` (local×2 → SP → local closer)
- Proof: `results/PREP-STATION-PROOF.md`
- Follow-on task open: `spotify-octave-step2-metadata-oauth`
- Validate: python structural checks ALL FIXTURES PASS (no network)

## 2026-07-17 (Step 1b paste-import — grok)
- Tool: `tools/exo/spotify_uri_import.py` (URI/URL → prep-only ontology; multi_deck=false)
- Check: `tools/exo/check_fixtures.py` + `just exo-fixtures-check` / `just exo-spotify-import`
- Sample: `fixtures/import/sample-paste.txt` → `songs/imported/` + `session-paste-import-demo.json`
- Task: `kanban/tasks/spotify-octave-step1b-paste-import.md` (done)
- Still no network / no OAuth / no playback

## 2026-07-17 (Layer B co-pilot why-next — grok)
- X deep alignment: elevate “co-pilot where you work” → offline Explain path
- Tool: `tools/exo/copilot_why_next.py` + `just exo-copilot-why` / `exo-copilot-why-mirror`
- Hybrid after song-02-peak → song-04 Spotify URI (sequence-only, score 102, 9A→10A)
- Artifacts: `results/COPILOT-WHY-NEXT.md` + dogfood `intent-inbox.v1.json` (proposed)

## 2026-07-17 (Layer B QML chrome — grok)
- Settings → **Co-Pilot (dogfood)**: `res/qml/Settings/CoPilot.qml` + wire in Settings.qml
- Fixture: `res/qml/CoPilot/fixture_why_next.json` synced by `just exo-copilot-why`
- Ack/Reject UI-only; Theme tokens; no CO / RT
- Task `layer-b-copilot-qml-chrome` → done

## 2026-07-18 — co-pilot runs on REAL sidecar data + tempo demotes un-mixable
Added tools/exo/ontology_from_sidecar.py (FSL track.json -> song-ontology, robust key->Camelot for Camelot/OpenKey/Traditional). Ran real sidecar->ontology->co-pilot end-to-end on 4 realistic tracks: from 8A/126 house, prog-house Em/128 (9A) wins (81), and dnb Em/174 (9A, SAME harmonic compat) is demoted to last (37) by the tempo clash. Honest gap: sidecar has no cues/energy yet -> analyzer (spike-musicunderstanding-local-to-exo). Fixtures under fixtures/sidecars/.

## 2026-07-18 — FSL sidecar cues + waveform energy bridge (codex-cli)
TrackDAO::exportToSidecar now emits optional real-data fields when the Track has them:
`cues[]` with type/hotcue/label/color/position_frames/position_ms/position_beats, and
`energy_curve` downsampled from Waveform filtered all/low/mid/high bands. The EXO bridge maps
sidecar energy into song ontology `energy_curve` and maps sidecar cues into session-local
`prep.cue_points`; it still does not invent sections, phrases, cues, or energy when absent.

Verified:
- `cmake --build build --target mixxx-test --parallel 8`
- `build/mixxx-test --gtest_filter='TrackDAOTest.*'`
- `just exo-tool-tests`
- `just exo-sidecar-ontology`
- `git diff --check`
- `./kanban/scripts/migx-fed audit --strict`
