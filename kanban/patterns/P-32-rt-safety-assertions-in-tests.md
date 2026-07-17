---
id: P-32
type: pattern
title: "Engine tests assert house physics: zero RT allocations and TSan-clean"
status: active
severity: MUST
domain: testing
related: [P-02, P-16, P-18, AP-14]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-32 — Engine tests assert house physics: zero RT allocations and TSan-clean

## Statement
A test that exercises an audio-path (`process*()`) code path asserts the house physics, not just the
output: **zero heap allocations** on the RT path (via an allocation-counting allocator) and **no data
races** (under ThreadSanitizer), alongside the behavioral GIVEN/WHEN/THEN assertion (`P-31`).

## Why
House physics — no alloc, no lock, no cross-thread block on the audio thread (`P-02`, `P-16`, `AP-14`) —
is invisible to an output-only test: code that allocates on `process()` still returns the right
samples, right up until it causes a dropout under load. Making the RT-safety property a *test
assertion* is what turns "we're careful" into a gate a machine enforces — an allocation-counting
allocator fails the test the moment a `process()` path allocates, and TSan fails it on the first race.
This is the sensor behind `AP-02`/`AP-14`.

## How to apply
- Wrap the `process()`-reachable section with an allocation counter (a counting global allocator /
  scoped guard) and assert the count is zero; run engine tests under `-fsanitize=thread`.
- Pair with tail-latency/underrun assertions where the test is also a benchmark (`P-18`).
- Include the RT-safety assertion whenever a test drives an engine callback path — not only in
  dedicated "RT safety" tests.
- Keep the behavioral assertion independent of the implementation (`P-31`).

## Example — wrong
```cpp
TEST(EngineTest, Processes) {
  buf = engine.process(in);
  EXPECT_EQ(buf, expected);   // output-only — an alloc/lock on process() passes silently
}
```

## Example — right
```cpp
TEST(EngineTest, ProcessIsAllocationFree) {
  ScopedAllocCounter alloc;                 // counts heap allocs in this scope
  buf = engine.process(in);                 // the RT path under test
  EXPECT_EQ(alloc.count(), 0);              // house physics asserted (P-02)
  EXPECT_EQ(buf, expected);                 // + behavior (P-31); suite also runs under TSan
}
```

## Detection
Review: an engine/`process()` test that asserts only output; a CI engine suite not run under TSan or
without an allocation-counting check.

## Cross-references
Enforces `P-02` and the lock-free rule `P-16`; pairs with tail metrics `P-18`; it's the automated
catcher for `AP-14`/`AP-02`. Behavioral shape from `P-31`.
