---
id: initiative-ai-djing-product
type: initiative
status: active
title: "AI-DJing product — Cursor-for-music (MIT operating model)"
owner: gudjon
dossier: []
depends_on: []
blocks: []
pm_overlay:
  hypothesis: >
    If Migx forks Mixxx for instrument depth, builds under an MIT-equivalent product model
    (proprietary app + in-process Intelligence like Cursor), houses the product under agora later,
    and keeps Apple Silicon audio trust, then it can achieve Cursor-like differentiation in AI-DJing
    without rebuilding a DAW.
  primary_metric: >
    (1) co-pilot produces a verified next-track/transition proposal from session+ontology;
    (2) zero audio underruns under dual-deck + co-pilot on M4;
    (3) freemium/Pro path defined for proprietary Intelligence.
  guardrail: >
    No RT-safety regression (P-02); no second CO writer (P-06); upstream attribution preserved.
  validation: >
    EXO spike; MTL EVD baselines; ADR-003/005 boundary checklist on AI features.
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/Strategy-Current.md
  - kanban/architecture/decisions/ADR-005-open-core-plus-proprietary-intelligence.md
  - kanban/architecture/decisions/ADR-003-licensing-and-openness.md
related:
  - initiative-apple-silicon
  - ADR-002
  - ADR-004
---

# Initiative — AI-DJing product (Cursor strategy)

Strategy SSoT: [`kanban/Strategy-Current.md`](../Strategy-Current.md).  
MIT operating model: [ADR-003](../architecture/decisions/ADR-003-licensing-and-openness.md).  
Stack: [ADR-005](../architecture/decisions/ADR-005-open-core-plus-proprietary-intelligence.md).

## Problem
Building a DJ app from zero wastes the instrument. A weak plugin next to another DAW lacks depth of
permission. We take the **Cursor path**: fork the base, ship a **proprietary product**, embed AI.

## Workstreams

| Stream | Outcome | Seeds |
|---|---|---|
| **S0 Repo home** | Public early; later [agora](https://github.com/orgs/agora) | git posture runbook |
| **S1 Performance trust** | M4 p99/underrun floor | `initiative-apple-silicon`, MTL |
| **S2 World model** | Song/session ontology | EXO, FSL |
| **S3 Agent seams (B)** | Session mirror + intents | EXO, control bus |
| **S4 Product UI** | QML-primary | ADR-004 |
| **S5 Intelligence (C)** | Multi-model co-pilot (in-process OK) | ADR-005 |
| **S6 Growth** | Freemium, privacy mode | product notes |

## Closed loop
Trigger: next-track / transition / cue plan mid-session → Capture: session + ontology → Intelligence:
Layer C → Adjustment: intents applied; measure accept rate + underruns.

## Non-goals
- Rebuild engine from scratch  
- Electron-as-product  
- Forcing AI out-of-process for copyleft reasons (superseded)  
- Blocking S1 on S5  

## Status
`active` strategy umbrella. Dossiers open under registered prefixes as streams start.
