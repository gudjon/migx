---
id: P-24
type: pattern
title: "Build native arm64 with tuned flags for perf work"
status: active
severity: SHOULD
domain: build
related: [P-03, P-25, AP-08]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-24 — Build native arm64 with tuned flags for perf work

## Statement
Any build used for a performance measurement or ship is a native `arm64` build with CPU tuning
enabled — never an `x86_64` binary under Rosetta, and never an untuned generic build. The recorded
baseline (`P-25`) names the exact arch and flags.

## Why
The north-star is Apple Silicon perf; a Rosetta-translated x86_64 binary measures the emulator, not
the machine, and hides the very SIMD/NEON and memory-model behavior we're optimizing for. Native
arm64 is also the gate that unlocks the platform's fast paths (NEON intrinsics, and — once we adopt it
— Accelerate/vDSP for DSP; not wired in today). An untuned build leaves the tail on the table and
makes deltas between machines incomparable. The flags are part of the measurement, so they must be
pinned.

## How to apply
- Product floor is **macOS 26+ Apple Silicon only** (`ADR-006`); set `CMAKE_OSX_DEPLOYMENT_TARGET=26.0`.
- Configure CMake for `arm64` explicitly (e.g. `CMAKE_OSX_ARCHITECTURES=arm64`); confirm the binary is
  not translated (`arch`/`file` on the artifact, not "running under Rosetta").
- Enable CPU tuning appropriate to the target (an `-mcpu`/`-mtune` for the Apple core family) in the
  Release/benchmark config, and record the exact flags in the baseline.
- Build Release (or the dedicated benchmark config) for any number that gates a change — never a Debug
  binary, and never a stale one (`AP-08`).
- When DSP moves onto Accelerate/vDSP, that dependency is arm64-native too; note it in the baseline.

## Example — wrong
> Benchmarked the app that happened to be open — an x86_64 Debug build launched under Rosetta — and
> reported the fps as the M4 number.

## Example — right
> Benchmark artifact: `arm64` Release, `-mcpu=apple-m1` (or newer target), verified non-translated.
> Baseline `EVD-0031` records arch + flags + M4 (10-core). All deltas measured against it.

## Detection
Review: a perf number whose baseline doesn't state arch + tuning flags; a benchmark binary reporting
`x86_64` or Rosetta translation; a Debug build behind a perf claim.

## Cross-references
Feeds `P-03`; the baseline that records the flags is `P-25`. Measuring a stale/mis-built binary is
`AP-08`.
