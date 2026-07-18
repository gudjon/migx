# FSL — filesystem sidecar spike

**Prefix:** `FSL` · **Owner/facilitator:** gudjon · **DRI at seal:** `codex-cli`
**Historical note:** This dossier was scaffolded under `antigravity-cli`; Antigravity is now paused.  
**Initiative:** `initiative-experience-ontology` · **Status:** sealed / successor work named

## Scope

Prove an additive per-track sidecar export path from the existing library DB into a greppable
`<track-location>.migx/track.json` file. This is the filesystem substrate EXO needs; it does not remove
SQLite or flip full SSoT authority yet.

## Landed slice

- `TrackDAO::saveTrack()` exports a JSON sidecar with bpm / key / replaygain / peak.
- When available, the same sidecar carries `cues[]` and a coarse waveform-derived `energy_curve`.
- The DB remains canonical for current runtime paths.
- Verification records arm64 build, focused TrackDAO tests, EXO bridge tests, and sidecar smoke green.

## Successors

- EXO owns interpretation of sidecar facts into ontology/session prep.
- Analyzer/EXO successor work owns production section detection, richer structure, and graph derivation.

## Entry

`AGENTS.md` · `00-FOUNDATION/PS-FSL-01.md` · `90-EXECUTION/00-PHASE-PLAN.md` · federation: poll as
`claude-code`.
