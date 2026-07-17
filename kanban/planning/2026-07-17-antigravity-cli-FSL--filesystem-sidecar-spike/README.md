# FSL — filesystem sidecar spike

**Prefix:** `FSL` · **Owner/facilitator:** gudjon · **Current DRI agent:** `claude-code`  
**Historical note:** This dossier was scaffolded under `antigravity-cli`; Antigravity is now paused.  
**Initiative:** `initiative-experience-ontology` · **Status:** execution / hardening before seal

## Scope

Prove an additive per-track sidecar export path from the existing library DB into a greppable
`<track-location>.migx/track.json` file. This is the filesystem substrate EXO needs; it does not remove
SQLite or flip full SSoT authority yet.

## Landed slice

- `TrackDAO::saveTrack()` exports a JSON sidecar with bpm / key / replaygain / peak.
- The DB remains canonical for current runtime paths.
- Prior verifier note records arm64 build plus 95/95 library/track/dao tests green.

## Before seal

- Gate sidecar export to only-on-change; avoid redundant file I/O on every save.
- Add classified logging for export/open failures (`P-34`).
- Decide whether EXO `ontology.json` belongs in this dossier or a successor once analyzers exist.

## Entry

`AGENTS.md` · `00-FOUNDATION/PS-FSL-01.md` · `90-EXECUTION/00-PHASE-PLAN.md` · federation: poll as
`claude-code`.
