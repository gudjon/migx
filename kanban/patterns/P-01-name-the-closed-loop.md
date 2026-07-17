---
id: P-01
type: pattern
title: "Name the closed loop before you ship"
status: active
severity: MUST
domain: harness
related: [P-03, AP-01]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-01 — Name the closed loop before you ship

## Statement
Before shipping any load-bearing process or change, you shall be able to name its four beats —
**Trigger · Capture · Intelligence · Adjustment** — and the adjustment shall be automatic,
repeatable, and verifiable against the same trigger.

## Why
The default failure mode is the *open* loop: work that produces an output nobody consumes and no
sensor re-checks. Closed loops are the whole discipline (MG-1). If you can't name the four beats,
the work isn't done — it's a wish.

## How to apply
State it in one line in the PR/dossier:
> Trigger: `<benchmark run / commit / schedule / merged PR>` · Capture: `<data at a stable path>` ·
> Intelligence: `<what reads it and produces a verdict>` · Adjustment: `<what changes, re-checked by
> the same trigger>`.

## Example — right (a Migx optimization loop)
Trigger: nightly benchmark suite · Capture: `EVD-*` fps/frame-time records · Intelligence:
`derive-closure-metrics` compares to pinned baseline · Adjustment: a regression opens a `tasks/`
card; a win seals the dossier's `91-LOOP-CLOSURE`.

## Detection
Review question: "What re-closes this loop?" No answer ⇒ open loop ⇒ not done.

## Cross-references
For perf work the loop's contract is `P-03`. Failing to close it at seal time is `AP-01`.
