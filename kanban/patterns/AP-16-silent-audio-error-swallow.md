---
id: AP-16
type: antipattern
title: "Silent audio-error swallow"
status: active
severity: MUST-NOT
domain: engine
related: [P-01, P-32, AP-01]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-16 — Silent audio-error swallow

## What it looks like
An error on the audio path — a dropped buffer, an underrun, a failed decode, a device xrun, a NaN in
the signal — is caught and the code continues without recording it anywhere: an empty `catch`, a
zeroed buffer with no counter, a "return early on failure" with no signal to any observer.

## Why it's harmful
Audio degradation is only actionable if it's visible. Swallowing the error means the app keeps playing
(good) but the failure never enters any sensor (bad): no counter, no log, no `ControlObject`, nothing
for a benchmark or session to close a loop on (MG-1). The dropout the user hears has no corresponding
signal in the data, so the perf/quality loop is blind exactly where it matters most. It's a hidden open
loop (`AP-01`) inside the RT engine.

## What to do instead
- Continue *and* record: bump an underrun/error counter, write a status `ControlObject`, or push to a
  lock-free diagnostics ring — using only RT-safe means (no alloc/lock/log-from-`process()`, `P-02`);
  the GUI/worker side reads and surfaces it.
- Make the counter part of the perf gate: tail-latency plus a zero-underrun assertion (`P-18`), checked
  in tests (`P-32`).
- Name the loop that consumes the signal (`P-01`) — an error nobody reads is still an open loop.

## Detection
Review: an empty/bare `catch`, a silent early-return, or a zeroed buffer on an audio-path error with no
counter/signal; a `process()` failure branch that updates no observable state.

## Cross-references
Leaves the loop open (`P-01`, `AP-01`); the counter is asserted by `P-18`/`P-32`; recording must stay
RT-safe per `P-02`. The non-RT surface (library/DB/decode) is governed by `P-34`
(fail-classified-never-silent-fallback), which this antipattern is the RT-adjacent instance of.
