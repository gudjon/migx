---
id: spike-musicunderstanding-local-to-exo
type: task
title: "Spike: OS-26 on-device audio analysis (MusicUnderstanding / Accelerate) → EXO ontology fields"
status: open
owner: gudjon
priority: medium
initiative: initiative-experience-ontology
parent_dossier: ""
depends_on: []
authored_by: claude-code
authored_kind: agent
triggered_by: "Harvest of apple-audio-frameworks-os26-wwdc25.md §3.7/§5 (MusicUnderstanding 'watch + spike') + owner signal 'massive opportunity to align with Apple Silicon audio frameworks'. Unblocked by ADR-006 macOS-26 floor (no availability guards)."
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  Time-boxed research spike (NON-RT, local files only) that answers, on macOS 26 + M4:
  - Is an OS-26 MusicUnderstanding / analysis API actually available to a third-party app for a
    LOCAL library file (readable PCM), and what fields does it yield (tempo, key, structure, energy,
    segments)? Record what's real vs marketing (§3.7 caveat: no Apple Music stream-PCM rights).
  - Compare its output + on-device cost (M4, Accelerate/vDSP) against Migx's own analyzers and the
    MLX/Demucs research path ([[research-analyzer-structure-energy-mlx]]) — philosophy + accuracy + latency.
  - Map the yielded fields to concrete EXO ontology edges/properties (structure, energy curve, harmonic
    journey) — the "session as graph" thesis. Output: a decision note (adopt / augment / skip) +, if
    adopt, an EXO analyzer task, NOT a dossier yet (compound-check first).
  House physics: analysis runs on WORKER threads → results cross to the engine only as ControlObject
  params via lock-free handoff (P-02/P-16); never on process*(). Local PCM only — MusicKit/Apple Music
  is rights-bound, treat like Spotify (prep/identity first, per the note §3.7).
---

# Spike: OS-26 on-device analysis → EXO

The offensive half of the Apple-audio-framework alignment ([[apple-audio-frameworks-os26-wwdc25]] §5:
"MusicUnderstanding — Watch + spike"). The macOS-26 floor (ADR-006) removes the availability-guard
question — if an OS-26 on-device music-analysis API exists for local files, Migx can use it flat-out to
populate the **experience ontology** (the AI-DJing differentiator: an agent that understands a *set*).

This is a **spike** (bounded investigation, honest adopt/skip verdict), not a build commitment — the
note flags real uncertainty (third-party API availability, local-PCM-only, speech/ambience ≠ dance
stems). Cross-check against Migx's own analyzers before adopting. Related: `arch-audio-io`,
[[research-analyzer-structure-energy-mlx]], initiative-experience-ontology.
