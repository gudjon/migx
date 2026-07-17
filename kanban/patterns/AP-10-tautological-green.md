---
id: AP-10
type: antipattern
title: "Tautological green"
status: active
severity: MUST-NOT
domain: testing
related: [P-09, P-31, AP-01]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-10 — Tautological green

## What it looks like
A test is rewritten to assert the new code against *itself* — the expected value is recomputed from the
implementation under test, a golden is regenerated from the new output, or the assertion is relaxed
until it passes. It goes green and stays green no matter what the code does, so it tests nothing.

## Why it's harmful
The test now encodes "the code does what the code does," a tautology. It gives false confidence: the
suite is green while the behavior is unverified, and a real regression sails through because the oracle
moves with the implementation. It's the testing form of grading your own change (`AP-05`) and a direct
route to green-over-red closure (`AP-01`) — the contract (`P-09`) becomes decorative.

## What to do instead
- The oracle must be independent of the implementation: a hand-derived expected value, a frozen golden
  captured *before* the change (`P-12`), or an equivalent reference — not output regenerated from the
  new code.
- Freeze the acceptance contract before implementing (`P-09`); if it was wrong, supersede it
  explicitly, don't quietly edit it to pass.
- Keep tests behaviour-first: GIVEN a defined input, WHEN the action, THEN an independently-known
  result (`P-31`).

## Detection
Review: a test whose expected value is derived from the implementation under test; a golden regenerated
in the same change that changed the behavior; an assertion loosened until green with no rationale.

## Cross-references
Defeats `P-09`; the independent-oracle discipline is `P-12`/`P-31`; a sibling of `AP-05` and a path to
`AP-01`.
