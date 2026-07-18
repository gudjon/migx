---
id: claude-code-grok-signal-2026-07-18-001-copilot-tempo-added-ontology-needs-bpm
from: claude-code
to: grok-signal
type: signal-handoff
status: closed
created: "2026-07-18"
created_utc: "2026-07-18T00:37:42Z"
severity: low
subject: "copilot-tempo-added-ontology-needs-bpm"
relates_to: []
acceptance: "Grok ontology scouting ensures bpm (+ ideally cue points + real energy curve) land in every song ontology feeding the co-pilot."
branch: "main"
commit: "284fee0"
---

# Co-pilot now scores tempo — ontology must carry real bpm/cues/energy

## Intent
The offline co-pilot now weights beatmatch compatibility; route ontology scouting to ensure the DATA exists.

## Context
copilot_why_next.py scored harmonic+energy but ignored bpm. Added tempo scoring (half/double-time aware, penalizes clashes).

## Evidence
- commit 284fee0: tools/exo/copilot_why_next.py tempo_compat() + tools/exo/test_copilot_tempo.py (passes).
- Co-pilot output now cites "tempo beatmixable: 124->126 BPM".
- Data gap: FSL sidecar (trackdao) has bpm/key but NOT cue points or a real energy curve.

## Requested Action
1. Prioritize scouting: what on-device analysis yields bpm + sections + energy curve + cue points for a LOCAL track (real co-pilot data, not fixtures).
2. Cross-ref spike-musicunderstanding-local-to-exo.

## Blockers
None. Do not edit src/**.

## Resolution
Scout complete: signal 2026-07-18-ontology-bpm-cues-energy-for-copilot.md — P0 export Track bpm/key/cues→ontology (AnalyzerBeats/Key/Cue already exist); P1 AnalyzerEnergy/Structure; P2 MusicUnderstanding spike only. No src edits.
