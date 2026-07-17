---
id: AP-12
type: antipattern
title: "GPU↔CPU copy in the render hot path"
status: active
severity: MUST-NOT
domain: gpu
related: [P-21, P-22, P-23, AP-02]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-12 — GPU↔CPU copy in the render hot path

## What it looks like
Every frame, waveform/texture data is copied GPU→CPU→GPU: a full re-upload of the waveform vertices or
texture, a framebuffer/texture read-back, or rebuilding the whole GPU buffer from scratch inside the
per-frame render path.

## Why it's harmful
Apple Silicon is unified-memory — the copy moves bytes that were already addressable by both
processors, burning bandwidth, CPU time, and latency for nothing. It makes the waveform renderer scale
with track length instead of the visible delta, becomes the frame-time bottleneck under load, and — if
any of it leaks onto the audio thread — turns into a dropout. It's a prime source of the
"fast at idle, glitches under GPU load" regression (`AP-02`).

## What to do instead
- Keep waveform buffers persistent in GPU memory and update only the changed region (`P-22`); scroll
  via a shader uniform, not by re-uploading vertices.
- Never read the framebuffer or a texture back to the CPU inside the frame path.
- Keep all of it off the audio deadline (`P-21`) and on the display clock (`P-23`).

## Detection
Profile: per-frame full buffer/texture upload or read-back in the waveform renderer; GPU upload
bandwidth scaling with track length rather than the visible scroll delta; per-frame CPU allocation in
the render path.

## Cross-references
Violates `P-22`; defeats `P-21`'s off-the-deadline goal; the wrong clock is `P-23`. Feeds `AP-02`.
