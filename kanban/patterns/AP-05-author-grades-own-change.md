---
id: AP-05
type: antipattern
title: "The author grades their own change"
status: active
severity: MUST-NOT
domain: harness
related: [P-08, P-09, AP-01]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-05 — The author grades their own change

## What it looks like
The same operating unit that wrote a change also declares it passing — running a check it wrote, or
eyeballing its own result — with no independent evaluator between "I made it" and "it's done."

## Why it's harmful
The author shares the change's blind spots and is motivated to see green; they can (often
unconsciously) shape the check to the code. A self-graded pass is an open loop wearing a green badge:
the sensor isn't independent of the actuator, so the verdict carries no information (MG-1). It's the
mechanism behind green-over-red closure (`AP-01`) — the change *looks* validated and isn't.

## What to do instead
- Freeze the evaluation contract before the work (`P-09`), then have a party that didn't write the
  change run it (`P-08`): a fresh session with only the contract, a CI gate, or a differential harness.
- The generator proposes "done"; an independent evaluator's run is what makes it done.
- For audio behavior, put the verdict at the shadow/live gate (`P-10`).

## Detection
Review: a change whose only passing evidence came from the authoring session; a test written and run
by the same unit in the same breath; no independent verdict recorded.

## Cross-references
Violates `P-08`; needs the frozen contract `P-09`; it's how `AP-01` (green-over-red) happens.
