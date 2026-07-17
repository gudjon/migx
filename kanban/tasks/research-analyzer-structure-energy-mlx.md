---
id: research-analyzer-structure-energy-mlx
type: task
title: "Research AnalyzerStructure/Energy + open models (MLX/license) for EXO"
status: open
owner: gudjon
priority: P2
created: "2026-07-17"
defers_to:
  - kanban/knowledge/world-model-experience-ontology.md
  - kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike
  - kanban/federation/signal/2026-07-17-open-music-world-model-signal.md
related:
  - initiative-experience-ontology
  - initiative-apple-silicon
---

# Research — section/energy analyzers + on-device models

## Why
EXO spike can hand-author energy/sections. Production needs **worker-thread** analyzers
(`AnalyzerStructure`, `AnalyzerEnergy` — names indicative) feeding sidecars. Grok signal flagged
open-weight section/energy predictors; **license + MLX/Apple Silicon runnability** must be verified
before any dossier imports a model.

## Done when
- [ ] Inventory: current `src/analyzer/*` (beat/key/gain/silence/waveform/ebur128) — no structure/energy  
- [ ] Shortlist 1–3 open models/papers for section + energy (with **license** SPDX or equivalent)  
- [ ] MLX / arm64 feasibility note (or “CPU-only v1”)  
- [ ] Recommendation: build classic DSP first vs import model; RT-safety: **worker only** (`P-02`, `P-17`)  
- [ ] Either open a dossier prefix (e.g. under EXO/FSL) or close as “hand-author only for v1”  

## Non-goals
- RT-thread inference  
- Closed cloud-only models for the local co-pilot path  

## Provenance
Folded from federation mail `grok-signal-claude-code-2026-07-17-001-open-music-world-model`
(signal brief is illustrative placeholders — re-scout real sources before model pick).
