---
id: AP-08
type: antipattern
title: "Stale binary after a source edit"
status: active
severity: MUST-NOT
domain: build
related: [P-25, P-03, P-24, AP-09]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-08 — Stale binary after a source edit

## What it looks like
Source is edited, then a benchmark or test is run without rebuilding (or against a different build dir
than the one just built). The numbers describe the **old** binary — the change under test isn't even
in the artifact being measured.

## Why it's harmful
It produces a confident, precise, wrong result. A "no change" (or a phantom win) gets attributed to
the edit, the loop closes on a lie (MG-1), and the real effect — good or bad — ships unmeasured. In a
perf effort where the whole point is attributing a delta to one change (`P-25`), measuring a stale
binary poisons every downstream decision.

## What to do instead
- Rebuild before every measurement; make the benchmark step depend on the build so it can't run stale.
- Measure the **same** artifact you just built — pin the build dir and confirm the binary's mtime is
  newer than the edit.
- Record commit + build config with the number (`P-25`, `P-24`) so a stale run is detectable after the
  fact.

## Detection
Review/CI: a benchmark invoked without a preceding build; a binary older than the source it claims to
measure; a number whose commit/build metadata doesn't match the working tree.

## Cross-references
Defeats `P-25` and `P-03`; the build config it must respect is `P-24`. Cousin drift failure: `AP-09`
(moving-main baseline).
