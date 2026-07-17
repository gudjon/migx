---
id: AP-01
type: antipattern
title: "Green-over-red closure"
status: active
severity: MUST-NOT
domain: harness
related: [P-01, P-03]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-01 — Green-over-red closure

## What it looks like
A dossier is sealed (`sealed: true`) with a "met" verdict while acceptance criteria are actually
unmet, unmeasured, or the retro is boilerplate — declaring success over an unfinished or unverified
result.

## Why it's harmful
The closure corpus is a learning instrument (`mine-dossier-retrospectives`). A green-over-red seal
poisons it: future dossiers inherit a false lesson, and the open work silently disappears instead of
spawning a follow-on. It also breaks MG-1 — the loop was never actually closed.

## What to do instead
- Seal **met/partial** only with the benchmark/test cited in the Verdict (`P-03`).
- If the bet didn't land, **halt honestly**: `sealed: true` with a `halted` verdict, a named
  successor dossier, an owner, and the re-fire condition. That is a valid, respectable closure.
- Never seal with an empty retrospective — the Phase-3 lint
  `verify-sealed-dossier-has-closure.py` blocks it.

## Detection
`91-LOOP-CLOSURE` Honest-gate checklist unchecked; a "met" criterion with no cited benchmark; a
boilerplate retro. Lint-enforced in Phase 3.

## Cross-references
Violates `P-01`; the guard for perf claims is `P-03`.
