---
description: "Planning happens in dossiers — compound before create, name the loop, seal honestly"
paths:
  - kanban/planning/**
---

# Rule — the planning harness (MG-5)

Planning happens in **dossiers**, not tickets. A dossier is one 1–4-day closed-loop sprint
(`kanban/planning/<date>-<owner>-<PFX>--<slug>/`), scaffolded from `kanban/planning/_template/`.

## Before you scaffold
1. **Register the prefix.** The 3-letter dossier prefix must be in
   `kanban/planning/00-PORTFOLIO/prefix-registry.yaml` before any file uses it.
2. **Compound before create.** Prove no OPEN dossier already owns this scope; if one does, fold your
   work into it. New scope → new dossier. Never route fresh work into a sealed/dormant dossier.
3. **Name the closed loop** (`P-01`). State Trigger / Capture / Intelligence / Adjustment. For perf
   work: the benchmark is trigger+capture, the delta is intelligence, the merged change is adjustment.

## Foundation
Each problem gets one `PS-<PFX>-NN` (default: ONE per dossier) opening with an **EARS** sentence and a
machine-consumable `acceptance:` block — a numeric threshold + the benchmark/test that checks it. That
contract is what closes the loop. Root claims in real `file:line`, opened at HEAD.

## Execution
Waves in `90-EXECUTION/00-PHASE-PLAN.md`, each ending at a verifiability gate; commit per wave. House
physics guardrails apply every wave (`P-02` etc.). Running unattended → the autonomous decision cascade
(`.claude/rules/agentic-decision-authority.md`).

## Seal
Score the bet at `91-LOOP-CLOSURE/` — verdict · 5-pass retro · wiring ledger · forecast-vs-actual.
Seal `met`/`partial` only with the benchmark/test cited, or **halt honestly** (`halted` + named
successor + owner + re-fire condition). Never green-over-red (`AP-01`). Before `sealed: true`, re-home
durable learnings into `patterns/`, ADRs, `architecture/`, or annotations — a sealed dossier is a dated
snapshot of THEN, not current truth. See `.claude/rules/dossier-lifecycle.md`.
