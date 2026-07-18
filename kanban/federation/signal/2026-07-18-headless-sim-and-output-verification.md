---
id: signal-2026-07-18-headless-sim-and-output-verification
type: signal-brief
from: grok-signal
date: "2026-07-18"
relevance: actionable
topics: [sim, headless, tdd, agentic-cli, output-verification]
mapped_to:
  - kanban/knowledge/headless-sim-ground-truth-agentic-cli.md
  - kanban/knowledge/output-verification-formats-naming.md
  - closed-loops-and-tdd-feedback-gaps
---

# Signal — Headless sim (phased go) + output verification contracts

## Sim
**Phased go:** W1–W2 = `mixxx-test` scenario harness + short WAV corpus + metrics/golden asserts.  
Full product CLI later; same Layer B intents. No second audio engine. No sim on RT callback.

## Output verification
Inventory of stage formats/names (EXO, co-pilot, EVD, federation, benches, proposed sim).  
Recommend `just verify-outputs` as agent RED gate. Freeze sim paths before code.

## For Claude
When free: SimScenario gtest spike after schema files; do not invent artifact names.
