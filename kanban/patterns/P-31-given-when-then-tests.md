---
id: P-31
type: pattern
title: "GoogleTest cases are structured GIVEN / WHEN / THEN"
status: active
severity: SHOULD
domain: testing
related: [P-09, P-32, AP-10]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-31 — GoogleTest cases are structured GIVEN / WHEN / THEN

## Statement
A GoogleTest case tests one behavior and is structured GIVEN (arrange a defined input/state) · WHEN
(perform the single action under test) · THEN (assert an independently-known result). One behavior per
test; the expected result comes from an oracle independent of the code under test.

## Why
A test's job is to make a behavior legible and re-checkable (MG-1). GIVEN/WHEN/THEN forces a defined
input, a single action, and an explicit expected outcome — so a failure names exactly what broke, and
the expected value is visibly derived from the *spec*, not the implementation. A test that bundles
several behaviors, or that recomputes its expectation from the code under test, tells you nothing when
it goes green (`AP-10`). Structured cases are also what an evaluation contract (`P-09`) compiles down
to in the suite.

## How to apply
- One behavior per `TEST`/`TEST_F`; arrange the GIVEN, do one WHEN, assert the THEN — the three
  sections readable at a glance.
- The THEN value is independent of the implementation: hand-derived, or a frozen golden captured before
  the change (`P-12`) — never regenerated from the code under test (`AP-10`).
- Name the test for the behavior it pins, not the method it calls.
- For engine code, pair the behavioral assertions with the RT-safety assertions (`P-32`).

## Example — wrong
```cpp
TEST(MixerTest, Works) {           // vague, multi-behavior, expectation from the code itself
  Mixer m; m.process(buf);
  EXPECT_EQ(m.lastOutput(), m.compute(buf));   // asserts the code against itself (AP-10)
}
```

## Example — right
```cpp
TEST(MixerTest, GainOfHalfHalvesSample) {
  Mixer m; m.setGain(0.5);                     // GIVEN
  auto out = m.applyGain(1.0f);                // WHEN
  EXPECT_FLOAT_EQ(out, 0.5f);                  // THEN — expected known from the spec, not the impl
}
```

## Detection
Review: a test with no clear arrange/act/assert, several behaviors in one case, a vague name, or an
expectation derived from the implementation under test.

## Cross-references
Compiles a `P-09` contract into the suite; pairs with `P-32` for engine tests; its failure is `AP-10`.
