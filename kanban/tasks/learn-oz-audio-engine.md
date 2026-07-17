---
id: learn-oz-audio-engine
type: task
title: "Analyse the oz-platform audio engine for transferable learnings for Migx"
status: done
owner: gudjon
priority: medium
initiative: initiative-apple-silicon
parent_dossier: ""
depends_on: []
authored_by: claude-code
authored_kind: agent
triggered_by: "gudjon request 2026-07-17 — analyse learning from the Audio Engine in /Users/gudjon/code/oz-platform for Migx"
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  A findings note (kanban/knowledge/oz-audio-engine-learnings.md) that:
  - surveys the audio engine / audio-stack work in /Users/gudjon/code/oz-platform (start:
    kanban/initiatives/initiative-audio-stack-2026-q3.md, then any audio DSP/pipeline/latency code and
    its dossiers/patterns),
  - extracts what is TRANSFERABLE to Migx's real-time audio engine (arch-engine-realtime, arch-audio-io):
    e.g. RT-safety techniques, lock-free buffer handling, low-latency device handling, SIMD/Accelerate
    DSP, resampling, clock/sync, testing/benchmark approaches, CoreAudio specifics on Apple Silicon,
  - for each learning: what it is, why it helps Migx, which Migx subsystem/pattern it maps to (or a new
    pattern candidate), and whether it seeds a dossier (DSP/ASI),
  - explicitly separates transferable engineering technique from oz-domain-specific (robotics/CV) parts.
---

# Learn from the oz-platform audio engine

Mine `/Users/gudjon/code/oz-platform` audio work for what helps Migx's RT audio engine + Apple-Silicon
DSP push ([[initiative-apple-silicon]]). Distill-don't-clone (same discipline as the harness itself):
take the transferable technique, drop oz robotics domain. Start from
`oz-platform/kanban/initiatives/initiative-audio-stack-2026-q3.md` and follow it to the code/dossiers.
Cross-reference against our patterns (P-02/P-16/P-17/P-18) and DDD (arch-engine-realtime, arch-audio-io).
Research input, not implementation.
