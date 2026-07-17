---
id: P-12
type: pattern
title: "Freeze a golden of retired code before deleting it"
status: active
severity: SHOULD
domain: testing
related: [P-11, P-09, P-10]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-12 — Freeze a golden of retired code before deleting it

## Statement
Before deleting code that a replacement is proven *against* — a DSP kernel, a mixing path, a summary
generator — commit a frozen **golden**: recorded output (with measured fidelity) of the old code on a
defined signal, so the replacement's equivalence stays checkable after the original is gone.

## Why
`P-11` says migrate-and-delete, but once the old implementation is deleted you lose the only reference
that says what "correct" sounded/looked like. A golden captures that reference as data: the retired
path's output on a bounded input, at a stated fidelity. It turns "trust me, it's equivalent" into a
differential test the evaluator (`P-08`) can run forever — and it's what lets you delete confidently
instead of hoarding dead code. This is the capture half of a promotion loop (`P-10`).

## How to apply
- Record the old path's output on the defined signal/dataset *before* deleting it; store it as a
  fixture with its fidelity bound (bit-exact, or ≤ −Xdb error).
- Keep the differential test that compares the new path to the golden in the suite (`P-09`, GIVEN/WHEN/
  THEN per `P-31`).
- Note the commit the golden was captured at, so it's reproducible.
- Then delete the old code — the golden, not the source, is the reference.

## Example — wrong
> Deleted the old waveform summary generator the moment the new one "matched in a quick listen." No
> recorded reference — a later regression against the old behavior is now undetectable.

## Example — right
> Captured `golden/waveform-summary-v1.bin` (bit-exact, commit `deda627b`) before deleting the old
> generator; a differential test asserts the new generator matches it within the stated bound.

## Detection
Review: deletion of a differentially-validated path with no committed golden + comparison test; a
"matches the old behavior" claim with nothing recorded to compare against.

## Cross-references
Completes the delete step of `P-11`; the comparison is a `P-09` contract run by `P-08`; it's the
capture for `P-10`.
