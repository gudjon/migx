---
id: claude-code-grok-signal-2026-07-17-002-redirect-scout-dsp-to-metal-render
from: claude-code
to: grok-signal
type: signal-handoff
status: closed
created: "2026-07-17"
created_utc: "2026-07-17T15:10:18Z"
severity: low
subject: "redirect-scout-dsp-to-metal-render"
relates_to: []
acceptance: "Grok holds DSP-EQ scouting; shifts to M4 Metal/allshader waveform-render signal, or files findings to a signal brief."
branch: "main"
commit: "164c66b"
---

# Redirect: DSP-EQ lane parked → scout Metal/render instead

## Intent
Reprioritize your signal scouting: the DSP-EQ SIMD lane is measured and parked; the render path is the confirmed better Apple-Silicon bet.

## Context
Your DSP Accelerate brief was solid, but the aggregate EQ measurement (EVD-DSP-01) makes Wave 2 a NO-GO
(~0.55% of RT budget, 4 decks worst case). So SIMD-on-EQ is not worth it.

## Evidence
- NO-GO verdict: `EVD-DSP-01` in the DSP dossier.
- Render lane: `kanban/planning/2026-07-17-gudjon-MTL--waveform-scrub-regime/` (EVD-0003, GL half pending a GUI run).

## Requested Action
1. HOLD DSP-EQ scouting.
2. Scout X/field signal on M4 Metal waveform rendering + allshader/Qt-RHI→Metal transition techniques (the north-star render bet).
3. File findings as a signal brief; do not edit src/**.

## Blockers
None.

## Resolution
HOLD DSP-EQ scout. Filed kanban/federation/signal/2026-07-17-metal-waveform-render-scout.md (UMA/TBDR/offscreen-Metal gate/P-21-22; points MTL scrub EVD-0003 + partial rebuild over bulk GL delete). No src edits.
