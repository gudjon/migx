---
id: initiative-<slug>
type: initiative
status: proposed          # proposed | research | active | complete | archived (paused as a side state)
title: "<display title>"
owner: <member>
dossier: []               # → kanban/planning/<dossier>/ the dossiers this wraps (≥1 once status ≥ research, else it's "isolated" — a smell)
depends_on: []            # bidirectional: update the counterpart's blocks: in the same commit
blocks: []
pm_overlay:
  hypothesis: "If we <do X>, then <outcome> because <reason>."
  primary_metric: ""      # the ONE north-star metric this bet moves
  guardrail: ""           # the invariant it must not regress
  validation: ""          # how the metric is measured (benchmark/test)
created: "YYYY-MM-DD"
lastUpdated: "YYYY-MM-DD"
---

# <Initiative title>

> The dossier is the unit of work (MG-5); this is only a thin lateral "why" wrapper pointing at the
> dossiers that execute the bet. If it wraps no dossier, it isn't ready to be an initiative — it's a
> note. See `kanban/initiatives/AGENTS.md`. Keep ≤120 lines.

## Problem statement
<One paragraph — what's broken / the gap that motivates this bet.>

## Hypothesis
<Restate pm_overlay.hypothesis in prose. Why now; what changes if we ship it.>

## Scope → dossiers
<Which dossiers (by prefix/id) execute this, each with its first move. Register prefixes in
kanban/planning/00-PORTFOLIO/prefix-registry.yaml first.>

## The closed loop (MG-1)
Trigger / Capture / Intelligence / Adjustment for the bet as a whole.

## Status
<Current state; which wrapped dossier is executing.>
