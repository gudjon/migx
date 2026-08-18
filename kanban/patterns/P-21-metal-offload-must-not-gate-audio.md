---
id: P-21
type: pattern
title: "GPU/waveform work never gates the audio callback deadline"
status: active
severity: MUST
domain: gpu
related: [P-02, P-22, P-23, AP-12, AP-14]
created: "2026-07-17"
lastUpdated: "2026-08-18"
---

# P-21 — GPU/waveform work never gates the audio callback deadline

## Statement
GPU and waveform-rendering work runs off the audio thread. The audio callback (`process*()`) shall
never wait on GPU submission, texture upload, fence/queue completion, or the render loop; GPU latency
must not enter the buffer-deadline budget.

## Why
The audio thread has a hard deadline (`P-02`, MG-6); the GPU does not. On macOS the rendergraph draws
through Qt RHI/scenegraph (Metal *via* RHI — there is no direct Metal path today), and RHI submission,
driver stalls, and display-link jitter are all unbounded from the audio thread's point of view. If the
callback ever blocks on any of that, one slow frame becomes an audible dropout. The two clocks are
independent and must stay that way (`P-23`).

## How to apply
- The render side reads a lock-free snapshot the engine publishes (`P-16`); it never calls back into
  `process()` and the audio thread never calls into the rendergraph.
- Keep waveform data in GPU-accessible buffers across frames (`P-22`); do not round-trip through the
  CPU on the audio thread.
- Drive redraw from the display/guitick clock, not the buffer period (`P-23`).
- Any GPU offload of DSP must publish results asynchronously; the audio path uses last-good if the GPU
  result isn't ready — it never stalls waiting.

## Example — wrong
```cpp
// Reachable from the audio callback:
m_rhi->finish();                 // block until the GPU drains → unbounded stall on the RT deadline
uploadWaveformTexture(buffer);   // texture upload from process() → underrun under GPU load
```

## Example — right
```cpp
// Audio thread: publish a snapshot lock-free (P-16), return immediately.
// Render thread (display clock): read snapshot, update GPU buffers (P-22), draw via RHI. No shared lock.
```

## Detection
Review: any RHI/scenegraph/GPU call, fence wait, or texture upload reachable from `process*()`;
TSan + allocation-counting allocator on engine tests (`P-32`).

## Cross-references
Serves `P-02`; pairs with `P-22` (zero-copy) and `P-23` (display clock). The blocking violation is
`AP-12`, a special case of `AP-14`.

## Scope extension — the visual compositor (2026-08-18)

Written for waveform rendering; it governs **every GPU consumer**, and the one now arriving is the
wall: projectors, LED, lasers behind the DJ. The industry treats DJ+visuals as one booking, so this
stops being a niche and becomes a second output the same night drives.

**Clock direction is the whole rule.** Audio is the clock; the wall subscribes.

| Consumer | Budget | On a miss |
| --- | --- | --- |
| audio callback | a buffer period (<3 ms) | an underrun — the night |
| booth TUI | a redraw | nobody notices |
| visual compositor | a display frame | a blemish |

So the compositor **samples** lock-free taps — beat, phase, energy, section, now/next, technique — and
never calls into the engine, never holds a lock the callback can want, and never becomes something the
callback waits on. A stalled renderer must not stall a deck. That is the same law as waveform offload,
with more at stake because a projector failing is visible to a room.

Corollaries that follow from it, not from taste:

- **One renderer for UI *and* wall is wrong** — different frame budgets. Booth chrome may drop a
  frame; the wall at 60 fps in front of a crowd is a different contract.
- **A generative layer is not a master clock.** WebGPU/WebView content is a *layer*, sampled like any
  other. `ADR-004` already refused a web stack as the performance surface; this extends that to the
  wall.
- **Live AI video generation is not the wall.** Latency plus surprise on a deadline nobody can retry.
  Bake loops offline into the Collection and play them like tracks.
- Rive is the **native chrome** layer (logo, stinger, "track incoming") per `ADR-004` — not the engine
  for a 20 m LED wall.
