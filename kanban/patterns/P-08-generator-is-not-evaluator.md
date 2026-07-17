---
id: P-08
type: pattern
title: "The author of a change does not grade it"
status: active
severity: MUST
domain: harness
related: [P-09, P-10, AP-05]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-08 — The author of a change does not grade it

## Statement
The operating unit that generates a change is not the one that declares it passing. An **independent
evaluator** — a separate session, a CI job, a differential harness — runs the frozen evaluation
contract (`P-09`) and returns the verdict.

## Why
The author is the worst-positioned party to judge their own work: they share its blind spots, they're
motivated to see green, and they can (often unconsciously) tune the check to the change. Separating
*generator* from *evaluator* is what makes a verdict trustworthy — the evaluator only sees the
contract and the artifact, not the intent. This is the structural guard behind every closed loop
(`P-01`): the sensor is independent of the actuator.

## How to apply
- Freeze the evaluation contract (`P-09`) *before* the change, so the evaluator runs criteria the
  author can't move.
- Run the verdict in a context that didn't write the change: a fresh session with only the contract, a
  CI gate, or a differential harness comparing against a frozen golden (`P-12`).
- The generator proposes "done"; the evaluator's independent run is what makes it done.
- For audio behavior, the evaluator sits in the shadow/live gate (`P-10`).

## Example — wrong
> The session that rewrote the resampler runs a check it also wrote, sees green, and declares the bet
> won (`AP-05`).

## Example — right
> Generator opens the change with a frozen `PS` acceptance contract; a separate evaluator run (fresh
> context / CI) executes that contract against the artifact and records the verdict as `EVD-*`.

## Detection
Review: a change whose only passing evidence was produced by the authoring session; no independent
evaluator invocation in the loop.

## Cross-references
Runs the contract `P-09`; is the independence half of `P-01`. Its violation is `AP-05`; the audio-path
rollout that enforces it is `P-10`.
