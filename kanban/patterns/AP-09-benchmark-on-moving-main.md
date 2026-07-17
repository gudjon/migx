---
id: AP-09
type: antipattern
title: "Benchmark on a moving main"
status: active
severity: MUST-NOT
domain: build
related: [P-25, P-03, P-14, AP-08]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-09 — Benchmark on a moving main

## What it looks like
A perf delta is measured against whatever `main` happened to be at "before" time versus "after" time,
instead of a pinned baseline. The two runs differ by your change *plus* every other commit that landed
in between *plus* machine/build drift.

## Why it's harmful
The reported delta is no longer attributable to your change — it's a sum of unrelated effects and
noise. A regression can hide behind someone else's win; a phantom win can be someone else's
optimization. The loop can't close honestly (MG-1) and the next agent can't reproduce the number.
This is the specific breakage `P-25` exists to prevent.

## What to do instead
- Pin the baseline to a commit SHA + recorded HW/flags as an `EVD-*` (`P-25`); measure the candidate on
  the same machine changing only your commit.
- Report the delta against that pinned `EVD-*`, citing its ID — not "faster than main."
- Re-baseline deliberately (new `EVD-*`) only when HW/build config changes, and say so.

## Detection
Review: a perf claim with no pinned baseline `EVD-*`, or whose before/after runs sit on different tree
states or machines; "X% faster than main" phrasing with no SHA.

## Cross-references
Violates `P-25`; undermines `P-03` and `P-14`. Cousin: `AP-08` (stale binary) — the other way a perf
number lies.
