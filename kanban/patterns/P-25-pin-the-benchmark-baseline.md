---
id: P-25
type: pattern
title: "Pin the benchmark baseline to a commit and recorded hardware"
status: active
severity: MUST
domain: build
related: [P-03, P-14, P-24, AP-09]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-25 — Pin the benchmark baseline to a commit and recorded hardware

## Statement
A performance baseline is pinned to a specific commit SHA and a recorded hardware/build configuration
(machine, core count, arch, flags), stored as an `EVD-*` record. Every perf delta is measured against
that pinned baseline — never against a moving `main`.

## Why
A perf delta is only meaningful relative to a fixed reference. If the baseline drifts — because `main`
moved, or the machine/build changed between the "before" and "after" run — the number you report mixes
your change with everyone else's and with machine noise, and the loop can't be closed (`P-03`, MG-1).
Pinning the commit + HW makes the delta attributable to exactly one change and reproducible by the next
agent. Measuring against a churning tree is the `AP-09` breakage.

## How to apply
1. Record the baseline once: commit SHA, machine + core config (e.g. M4 10-core), arch + flags
   (`P-24`), and the benchmark filter/command — as an `EVD-*` in the dossier's `results/`.
2. Measure the candidate on the **same machine**, same build config, changing only your commit.
3. Report the delta against the pinned `EVD-*`, citing its ID; do not re-baseline mid-experiment.
4. Re-baseline deliberately (new `EVD-*`) when HW or the build config changes — and say so.

## Example — wrong
> "20% faster than main." (Which `main`? measured a week apart on whatever HEAD was, on an unrecorded
> machine — the delta is noise plus everyone else's commits; `AP-09`.)

## Example — right
> Baseline `EVD-0031` @ `deda627b` on M4 (10-core), arm64 Release `-mcpu=apple-m1`,
> `--benchmark_filter=Waveform`. Candidate `feat/x` on same box: p99 −18% vs `EVD-0031`.

## Detection
Review: a perf claim without a pinned baseline `EVD-*` (commit + HW + flags), or one whose "before" and
"after" were taken against different tree states or machines.

## Cross-references
Makes `P-03` and `P-14` measurable; records the build config from `P-24`. Its violation is `AP-09`;
a stale binary defeats it via `AP-08`.
