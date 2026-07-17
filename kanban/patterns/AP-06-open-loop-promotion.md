---
id: AP-06
type: antipattern
title: "Open-loop promotion"
status: active
severity: MUST-NOT
domain: harness
related: [P-10, P-01, P-09, AP-01]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-06 — Open-loop promotion

## What it looks like
A change — especially to audio behavior — is promoted on an impression: "sounds smoother, ship it."
No recorded baseline, no re-checkable contract, no shadow stage, no named loop that re-closes against
the same trigger.

## Why it's harmful
An impression is not code (MG-2) and can't be re-run, so nothing catches a later regression and no one
can reproduce the "win." Promoting straight to live also puts an unproven path in front of the
audience with the RT constraints (`P-02`) that make it hard to debug in the moment. It's the loop left
open at the most expensive point — the audio output (MG-1) — and it's how `AP-01` closes red as green.

## What to do instead
- Promote through offline → shadow → live (`P-10`), each stage passing a frozen contract (`P-09`).
- Name the loop's four beats before shipping (`P-01`): what triggers the re-check, what it captures,
  what judges it, what it adjusts.
- Record the baseline and the verdict as `EVD-*` so the win is a number, not a memory.

## Detection
Review: an audio-behavior (or perf) change promoted with no baseline, no shadow stage, and no named
re-check loop; "feels better" as the acceptance evidence.

## Cross-references
Skips `P-10` and `P-01`; lacks the contract `P-09`; a special case of `AP-01`.
