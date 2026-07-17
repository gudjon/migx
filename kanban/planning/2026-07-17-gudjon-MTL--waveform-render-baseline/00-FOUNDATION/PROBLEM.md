# Problem

## What's wrong today
We want Migx to render waveforms *blazingly fast* on Apple Silicon — but we have **no baseline**. Mixxx's
waveform path (`src/waveform/`, `src/rendergraph/`, `src/shaders/`) is written for cross-platform Qt RHI
portability; we don't yet know its frame-time distribution on an M4, whether Qt RHI is selecting the
Metal backend on macOS, or where per-frame CPU↔GPU copies happen. Without that, any "optimization" is a
guess measured against nothing — the "open loop" and "rehearse on an unstable base" breakages waiting to
happen.

## Who feels it
A DJ scrubbing or beat-matching on a loaded deck on an M4 MacBook — dropped waveform frames read as jank
and erode trust in the software. And every future MTL optimization dossier, which needs a number to beat.

## What "done" means (the bet)
This is a **baseline-only** dossier — the bet is small and about measurement, not speed:
1. **The problem is real** — we can measure the current M4 waveform render frame-time distribution and
   find headroom (an `EVD-*` baseline).
2. **The approach works** — a repeatable benchmark on this hardware, pinned to a commit, is stable
   enough to measure future deltas against (`P-25`).
3. **The gates catch failure** — the benchmark captures **p99/max frame time + dropped-frame count**
   under realistic load, not a mean (`P-18`), so a later regression can't hide.

## Non-goals
- **No optimization.** We do not change the render path here. Metal offload, zero-copy, and shader work
  are separate MTL dossiers that consume this baseline.
- Not touching the audio engine or the RT thread.

## Inheritance
Serves `initiative-apple-silicon`. Owning contexts `arch-waveform-render`, `arch-rendergraph`. Patterns:
`P-03` (benchmark contract), `P-18` (p99-not-mean), `P-25` (pin the baseline), `P-23` (render on display
clock), `P-21`/`AP-12` (GPU must not gate the audio deadline / no per-frame CPU round-trip).
