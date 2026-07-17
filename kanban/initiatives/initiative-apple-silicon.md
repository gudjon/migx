---
id: initiative-apple-silicon
type: initiative
status: active
title: "Migx runs blazingly fast on Apple Silicon (M4/M5 SoC)"
owner: gudjon
dossier: []                # ASI/MTL/DSP dossiers link here as they open (kanban/planning/)
depends_on: []
blocks: []
pm_overlay:
  hypothesis: "If we tune Migx's render and DSP paths for the M4/M5 SoC (Metal GPU offload, NEON/Accelerate audio, arm64-native build, unified-memory data paths), then it runs glitch-free at materially higher throughput than the portable upstream paths, because those paths are written for cross-platform portability, not this hardware."
  primary_metric: "worst-case (p99) frame/buffer time and throughput vs a pinned M4 baseline, glitch-free (zero underruns)"
  guardrail: "no real-time-safety regression (P-02/AP-02): zero RT-thread allocations, no locks on the audio callback, GPU never gates the audio deadline"
  validation: "per-dossier benchmark contract (P-03) with EVD-* baselines, scored at 91-LOOP-CLOSURE"
created: "2026-07-17"
lastUpdated: "2026-07-17"
related:
  - kanban/knowledge/apple-audio-frameworks-os26-wwdc25.md
  - kanban/knowledge/arcflow-m4-perf-techniques.md
---

# Migx blazingly fast on Apple Silicon

A thin lateral wrapper (MG-5: the dossier is the unit of work, not this) that gives the Apple-Silicon
performance bet one home — one hypothesis, one metric, one guardrail — and points at the **dossiers**
that execute it. Most work needs no initiative; this one earns its place because the bet spans
several dossiers (Metal render, audio DSP, build/SoC tuning) that all measure against the same metric.

## Problem statement
Migx forks Mixxx, whose rendering (Qt RHI / scenegraph) and DSP paths are written for cross-platform
portability, not for Apple Silicon specifically. That leaves throughput and battery on the table:
portable RHI where a tuned Metal path would win, scalar/portable DSP where NEON + Accelerate/vDSP
would win, and CPU/GPU copies that a unified-memory SoC makes unnecessary. Migx's differentiator is
that it is *tuned for this hardware*.

## Hypothesis
See `pm_overlay.hypothesis`. The bet has three parts (MG-1): the problem is real (baseline benchmarks
show headroom), the approach works (targeted Metal + Accelerate + arm64 tuning beat the portable
paths measurably), the gates catch failure (per-change benchmark contracts with p99 metrics and
zero-RT-allocation assertions).

## Scope → dossiers
Registered dossier prefixes (`kanban/planning/00-PORTFOLIO/prefix-registry.yaml`), each opened from
`kanban/planning/_template/` with `initiative: initiative-apple-silicon`:

| Prefix | Workstream | First move |
|---|---|---|
| `MTL` | Metal GPU offload — waveform / rendergraph / shaders | Baseline the render path on M4; confirm whether Qt RHI already selects Metal on macOS; find where a tuned path beats RHI. |
| `DSP` | M4 audio-engine DSP — NEON/SIMD via Accelerate/vDSP | Find the scalar hot loops (resampling, EQ, analysis); measure what vDSP buys, allocation-free (P-02). |
| `ASI` | Build + SoC tuning (umbrella) — arm64 flags, P/E-core awareness, unified-memory copy elimination | Confirm the mac build is arm64-native with the right flags; find avoidable GPU↔CPU copies. |

**Recommended first dossier:** `MTL` as a baseline-only "measure the waveform/render path on M4"
dossier that establishes the numbers everything else is judged against.

## The closed loop (MG-1)
Trigger: the nightly benchmark suite (the Dream cadence). Capture: `EVD-*` records per subsystem,
pinned to commits. Intelligence: delta vs baseline; regressions flagged. Adjustment: a win seals a
dossier + advances the baseline; a regression opens a `kanban/tasks/` card.

## Status
`active` once the first ASI/MTL/DSP dossier is executing. Until then: `proposed`/`research` while the
harness that runs it (the pattern catalogue, DDD map, benchmark tooling) is being stood up.
