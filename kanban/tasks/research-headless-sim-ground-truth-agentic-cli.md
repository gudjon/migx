---
id: research-headless-sim-ground-truth-agentic-cli
type: task
title: "Research: simulation ground truth + headless agentic CLI for Migx (WAV fixtures, mix measure)"
status: open
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
parent_dossier: ""
depends_on: []
authored_by: grok-signal
authored_kind: agent
queued_by: gudjon
queued_at: "2026-07-18"
triggered_by: "User 2026-07-18 — queue thinking: sim ground truth (.wav) so agents can measure/mix headless; full CLI agentic mode?"
created: "2026-07-18"
lastUpdated: "2026-07-18"
related:
  - closed-loops-and-tdd-feedback-gaps
  - world-model-experience-ontology
  - pat-03-benchmark-as-contract
  - P-08
  - P-02
  - EVD-0001
  - EVD-0003
  - EVD-DSP-01
acceptance: |
  A knowledge note (kanban/knowledge/headless-sim-ground-truth-agentic-cli.md) that answers:
  1. Should Migx invest in a first-class **Simulation / ground-truth** layer for agent TDD?
  2. What already exists (mixxx-test, EngineBufferE2E, soundFileFormats WAVs, headless CGL benches,
     EXO offline fixtures) vs what is missing for "agent loads two decks, mixes, measures"?
  3. Architecture options ranked for house physics:
     a) Pure engine unit sim (buffers in/out, no SoundIO) — measure bit-exact or SNR vs golden WAV
     b) Headless SoundDeviceNull / file writer (master out → .wav) for multi-deck graph
     c) Full CLI product mode (`migx --headless` / agent RPC) driving CO intents + reporting metrics
  4. Ground-truth design: corpus of short stereo WAVs (tone, click-track, known BPM/key), golden
     mix stems, measurable contracts (BPM estimate error, crossfade energy, underrun=0, L/R null).
  5. Agentic CLI surface: commands or JSON API for load/play/crossfade/cue + capture path; maps to
     Layer B intents without GUI.
  6. Risks: RT purity (sim never on callback), CI cost, flaky timing, over-simulating DJ feel.
  7. Recommendation: go / no-go / phased (W0 fixtures → W1 engine sim → W2 CLI) with effort estimate.
  8. Ties to closed-loop/TDD gaps: RED tests agents can run without display hardware.
loop_queue: true
scout_topics:
  - headless DAW / audio engine test harnesses
  - golden WAV regression for mixers
  - agentic coding verification loops with audio
seed_existing:
  - "src/test/soundFileFormats/*.wav.bz2 — reference tones"
  - "src/test/engine* E2E — buffer processing without full app"
  - "mixxx-test --benchmark — headless EVD path"
  - "EXO fixtures + just exo-* — offline Layer B without engine"
  - "SoundIO soak tool — device-level, not mix graph"
---

# Research — Simulation ground truth + headless agentic CLI

## Intent (user ask)

Think through whether we should **build in a Simulation** so development here has **ground truth**:
e.g. **`.wav` fixtures** the agent can **load, mix headless, and measure** — and whether Migx should
also run **fully in CLI headless agentic mode** (not only GUI).

This is a **closed-loop / TDD investment** question: stronger sensors for Claude Code and Grok, not a
feature for club gigs first.

## Why it matters

| Today | Gap for agents |
|---|---|
| Unit/bench pieces of engine (filters, buffer E2E) | No standard “two-deck crossfade” scenario with golden out |
| Waveform EVD headless (CGL) | Display path, not mix product loop |
| EXO offline co-pilot | Plans sets; does not prove engine mix |
| GUI dogfood | Slow, non-CI, agent-hostile |

A sim layer would let the agent:

```text
RED:  run scenario S → assert metric M fails (or golden mismatch)
GREEN: change code → same command passes
EVAL: CI / second peer re-runs same command (P-08)
```

## Non-goals (for the research note)

- Replacing Core Audio for real gigs  
- Shipping a consumer “headless DJ product” first  
- Network multi-user sim  

## Loop instruction (grok-signal / Claude)

When advancing this task: prefer **architecture + recommendation** over implementing SoundDevice.
Cite `file:line` for existing test hooks. Map options to ADR-005 layers A/B/C.

## Deliverable

`kanban/knowledge/headless-sim-ground-truth-agentic-cli.md`  
Optional: `PS-SIM-01` draft only if go recommendation is clear (register prefix `SIM` first).
