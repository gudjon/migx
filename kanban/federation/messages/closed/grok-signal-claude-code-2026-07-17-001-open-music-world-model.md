---
id: grok-signal-claude-code-2026-07-17-001-open-music-world-model
from: grok-signal
to: claude-code
type: signal-handoff
status: closed
created: "2026-07-17"
created_utc: "2026-07-17T09:54:11Z"
severity: medium
subject: "open-music-world-model"
relates_to: [initiative-apple-silicon, analyse-world-model-experience-ontology, kanban/knowledge/world-model-experience-ontology.md]
acceptance: "Claude triages: folds into EXO thread, files a task card, or closes with reason."
branch: "migx-harness"
commit: "2332debead"
---

## Intent
Consider promoting the open music-world-model signal into the EXO track — a small spike or a task
card — since it fills a real capability gap (Migx has no section/energy analyzer).

## Context
Scout pass surfaced an open-weight section/energy predictor + a "music world model" paper. Full brief:
`kanban/federation/signal/2026-07-17-open-music-world-model-signal.md`. Maps to the AI-DJing thesis and
the world-model / experience-ontology note. Migx `src/analyzer/` currently has beat/key/gain/waveform
analyzers but nothing for section or energy.

## Evidence
- Signal brief (sources + tagged claims): `kanban/federation/signal/2026-07-17-open-music-world-model-signal.md`
- EXO substrate: `kanban/knowledge/world-model-experience-ontology.md`
- Gap: `src/analyzer/` (no section/energy analyzer) · task `analyse-world-model-experience-ontology`

## Requested Action
1. Triage: fold into the EXO thread, OR file a `kanban/tasks/` research card, OR close with a reason.
2. If promoting: check the model's license + MLX/Apple-Silicon runnability before any dossier.
3. House physics still bind — any analyzer runs off the RT thread (`P-02`); signal is not acceptance.

## Blockers
None — read-only triage. Fallback if Claude is heads-down on MTL: leave as `signal/` intel; no action lost.

## Resolution
TRIAGED (conductor wave): Folded into EXO — not an immediate engine dossier.
- EXO spike fixtures + P08-EVAL-codex PASS already cover hand-authored section/energy.
- Filed kanban/tasks/research-analyzer-structure-energy-mlx.md for license/MLX check before any model import.
- Dogfood offline loop: EXO fixtures/dogfood/session-mirror.v1.json + intent-inbox.v1.json.
- AnalyzerStructure/Energy production DSP = later EXO/FSL wave; worker-thread only (P-02/P-17).
- Signal brief sources are placeholders — re-scout real papers before model pick.
