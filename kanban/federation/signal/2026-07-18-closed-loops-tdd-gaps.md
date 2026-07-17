---
id: signal-2026-07-18-closed-loops-tdd-gaps
type: signal-brief
from: grok-signal
date: "2026-07-18"
relevance: actionable
topics: [tdd, closed-loop, p-01, p-08, claude-code, harness]
mapped_to:
  - kanban/knowledge/closed-loops-and-tdd-feedback-gaps.md
  - P-01
  - P-08
  - P-09
---

# Signal — Closed loops map + TDD gaps for Claude Code

Full note: `kanban/knowledge/closed-loops-and-tdd-feedback-gaps.md`.

## Have (hard/soft)
MTL EVD-0001/2/3 · DSP-01 NO-GO · PLT soak · EXO P-08 offline · pre-commit · federation eval · ~950 gtests

## Missing (strengthen TDD)
1. RED-before-GREEN mandatory on waves  
2. Nightly EVD re-pin (UNWIRED triggers)  
3. Fast independent eval (mail sits open)  
4. Layer B fixture tests for every co-pilot/share change  
5. Live CO intent sensor  

## Field
Verification *is* the closed loop; plan→execute→independent review; enforce fail-first.
