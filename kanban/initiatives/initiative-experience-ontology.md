---
id: initiative-experience-ontology
type: initiative
status: proposed
title: "Migx experience ontology + AI-DJing co-pilot (the differentiator)"
owner: gudjon
dossier:
  - kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike
depends_on: []
blocks: []
pm_overlay:
  hypothesis: "If a song and a DJ session are modelled as a timeline-based experience ontology + property graph (stored in per-track Song.migx/ sidecars), then an agent (Claude Code/Grok) can read and safely affect a live session — analyse cue points, suggest song order, propose harmonically- and energy-legal transitions — making Migx a Claude-Code-compatible DJ instrument (the AI-DJing differentiator)."
  primary_metric: "an independent agent reasons a phrase-aligned, harmonically-legal transition from the sidecar ontology alone (spike acceptance); later: co-pilot suggestion accept-rate"
  guardrail: "all live writes marshalled through ControlObject as single-writer (P-06/P-20), never on the RT thread; the agent never re-predicts engine phase"
  validation: "spike dossier: model 1 real song + a 3-track session; prove the agent-reasons-a-transition acceptance with an independent evaluator (P-08)"
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# Experience ontology + AI-DJing co-pilot

The flagship product differentiator (part of `initiative-ai-djing-product`). A thin lateral wrapper
(MG-5: dossiers do the work) over the EXO/FSL dossiers that make Migx's music **agent-native**.

## Problem
Classic DJ software puts every decision in the human's hands and locks metadata in an opaque DB. Migx's
difference: represent songs + sessions as a **flow of experience** an agent can reason about and shape.

## Hypothesis
See `pm_overlay`. Full analysis: `kanban/knowledge/world-model-experience-ontology.md` (the ontology
schemas, property graph, live co-pilot path) — which found Camelot harmonic-mixing math **already ships**
in `src/track/keyutils.h`; the real build gap is two worker-thread analyzers (`AnalyzerStructure` sections,
`AnalyzerEnergy` curve). Storage is decided: sidecar-as-SSoT (`kanban/knowledge/filesystem-driven-architecture.md`).

## Scope → dossiers (register prefixes when opened)
| Prefix | Dossier | First move |
|---|---|---|
| `FSL` | Filesystem sidecar spike | Additive DB→`Song.migx/` sidecar export behind a build+test gate (the storage substrate EXO needs). |
| `EXO` | Experience-ontology spike | Model 1 real song's timeline + a 3-track session as `ontology.json` + property graph; prove an agent reasons a legal transition (P-08). |
| `EXO` | Live co-pilot slice (wave 2) | Off-RT filesystem session-mirror (read) + intent-inbox reconciled via ControlObject (write) — the "Claude Code affects the live set" use case. |

## The closed loop (MG-1)
Trigger: an agent scout/co-pilot session. Capture: the sidecar ontology + a session mirror. Intelligence:
the agent reasons transitions/experience from the graph. Adjustment: a suggested cue/order lands via
ControlObject (human-approved), and the outcome enriches the ontology.

## Status
`active` (EXO fixtures and P-08 proof are green; FSL additive export exists but needs hardening before
seal). Analyzers remain stubbed/hand-authored for the spike; production Song.migx/ authority waits on
FSL hardening and the later co-pilot slice.
