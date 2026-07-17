---
id: P-09
type: pattern
title: "Acceptance criteria are measurable, runnable, and frozen at creation"
status: active
severity: MUST
domain: harness
related: [P-03, P-08, P-01, AP-10]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-09 — Acceptance criteria are measurable, runnable, and frozen at creation

## Statement
A change's acceptance criteria form a contract that is **measurable** (a numeric threshold or a
bit-exact/bounded comparison), **runnable** (a named benchmark/test/query anyone can execute), and
**bounded** (a defined signal, dataset, and machine) — and it is **frozen at creation**, before the
work starts.

## Why
An evaluation you can't run and re-run isn't a sensor; a criterion written *after* the result is just
a description of what happened (MG-1, MG-2). Freezing the contract up front is what lets an independent
evaluator (`P-08`) judge the artifact without the author moving the target, and what stops a test from
being rewritten to pass its own new code (`AP-10`). In Migx this contract is the `PS` `acceptance:`
block — the machine-consumable unit that closes the loop.

## How to apply
- Write acceptance in the `PS` before implementing: the numeric threshold, the runnable command
  (`ctest`/benchmark filter/query), and the bounded inputs (signal, dataset, M4 core config).
- Make it re-runnable by anyone: no hidden state, no "on my machine" steps.
- Freeze it — the artifact under test may change; the contract may not. If the contract was wrong,
  supersede it explicitly, don't silently edit it.
- For perf it *is* the benchmark contract (`P-03`); for audio behavior it's what the shadow/live gate
  runs (`P-10`).

## Example — wrong
> Acceptance: "sounds better and is faster." Not measurable, not runnable, not bounded — nothing to
> re-check.

## Example — right
> `PS-ASI-04` acceptance: "p99 buffer time ≤ 60% of the 5.8 ms period, 0 underruns over 10 min, output
> bit-exact vs golden, on M4 10-core. Run: `mixxx-test --benchmark_filter=Mixer`." Frozen at creation.

## Detection
Review: an acceptance clause with no number, no runnable command, or written after the result; a
contract edited to match the change instead of the change meeting the contract.

## Cross-references
The perf specialization is `P-03`; the independent runner is `P-08`; it's the contract half of `P-01`.
Editing it to pass is the road to `AP-10`.
