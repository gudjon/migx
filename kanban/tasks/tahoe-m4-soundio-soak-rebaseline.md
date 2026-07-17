---
id: tahoe-m4-soundio-soak-rebaseline
type: task
title: "P0: Tahoe 26 + M4 SoundIO soak + underrun re-baseline (validate, don't rewrite)"
status: open
owner: gudjon
priority: high
initiative: initiative-apple-silicon
parent_dossier: ""
depends_on: []
authored_by: claude-code
authored_kind: agent
triggered_by: "Harvest of apple-audio-frameworks-os26-wwdc25.md §3.8/§5 P0 seed + ADR-006 (macOS 26 floor). Build box is on macOS 26.2 (25C56), M4, coreaudiod alive — actionable now."
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  Defensive survival check for the north-star ("zero underruns while co-pilot is live") on the ONLY
  supported OS (macOS 26, ADR-006). Produce an EVD-* record under initiative-apple-silicon that:
  - Runs a bounded audio soak on macOS 26.x + M4: sustained playback across device changes
    (built-in ↔ external ↔ AirPods), exclusive vs shared mode, sample-rate switches — logging
    underruns/xruns, coreaudiod device-flake events, and any NSSound/caulk SIGILL (§3.8 field risks).
  - Re-measures the buffer/underrun baseline (p99/max, zero-underrun gate) vs the pinned MTL EVD-0001
    baseline, since OS jumps drift latency/safety-offset (P-03/P-18/P-25). Records the OS build
    (26.2/25C56) in the baseline — OS version is now a baseline axis, not just commit + M4 core config.
  - Verdict: SoundIO on 26.x is solid (validate) OR names specific flake modes as follow-up cards.
  House physics: measurement only touches non-RT paths; no RT-thread change (P-02). "Validate, don't
  rewrite" — this is not a CoreAudio-direct rewrite (that's a separate bet).
---

# Tahoe 26 + M4 SoundIO soak + underrun re-baseline

Harvested P0 seed from [[apple-audio-frameworks-os26-wwdc25]] (§3.8 Tahoe field risks, §5 "Survival").
Migx now targets **macOS 26 only** (ADR-006), and the build box is already on **26.2 (25C56), M4,
coreaudiod alive** — so this is runnable now. The risk is real: community reports of coreaudiod
flakiness / "no devices" / caulk SIGILL on 26.x, plus latency/safety-offset drift after OS jumps that
moves the underrun baseline the whole Apple-Silicon perf bet is judged against.

Closed loop (MG-1): **Trigger** an audio soak on 26.x/M4 · **Capture** underrun + device-flake EVD ·
**Intelligence** delta vs EVD-0001 (is the RT path still glitch-free on the target OS?) · **Adjustment**
validate + advance the baseline, or open flake-specific cards. Cites `arch-audio-io`, `arch-engine-realtime`.
