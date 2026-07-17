---
id: AP-11
type: antipattern
title: "Mean hides the underrun"
status: active
severity: MUST-NOT
domain: engine
related: [P-18, P-03, AP-02]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-11 — Mean hides the underrun

## What it looks like
A performance change is gated on a single mean or throughput number ("+8% average"). The average
improves while the **tail** (p99/max buffer time) gets worse — the occasional stall that produces an
audible click is averaged away and never appears in the metric.

## Why it's harmful
DJ software is judged on worst-case glitch-free playback, not averages. A mean-only gate rewards
exactly the trade that hurts users: faster-on-average, worse-at-the-tail. It lets a real regression
merge under a green number, and it makes the benchmark contract (`P-03`) decorative instead of
protective.

## What to do instead
- Gate on the tail: p50 *and* p99/max, plus an explicit underrun count that must be zero (`P-18`).
- Measure under realistic contention (GPU active, library scanning) where the tail actually appears.
- State the acceptance threshold as a tail number, not an average.

## Detection
Review: a perf claim citing only a mean/throughput figure; a benchmark with no tail metric or underrun
count.

## Cross-references
Violates `P-18`; undermines `P-03`; it's the measurement blind spot that lets `AP-02` through.
