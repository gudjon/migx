---
id: P-23
type: pattern
title: "Redraw on the display clock, never the audio buffer period"
status: active
severity: SHOULD
domain: gpu
related: [P-21, P-22, P-02]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-23 — Redraw on the display clock, never the audio buffer period

## Statement
Visual redraw is driven by the display refresh / guitick / `VisualPlayPosition`, decoupled from the
audio buffer period. The number of frames drawn is a function of the screen's refresh rate, not of how
many audio buffers were processed.

## Why
The audio clock and the display clock are independent and run at different, unrelated rates — a 64k
buffer at 44.1 kHz fires far more often than a 60 Hz (or 120 Hz ProMotion) display refreshes, and
coupling them means either drawing frames nobody sees or letting render cadence leak into the audio
deadline (`P-02`). Migx already separates them: the engine publishes playback position (e.g.
`VisualPlayPosition`) and the GUI samples it on its own vsync-aligned tick. Redraw belongs on the
display clock so the GPU work stays off the audio path (`P-21`) and the waveform interpolates smoothly
between engine updates.

## How to apply
- Trigger redraw from the GUI/display tick (guitick / frame-swap / display link), and read the latest
  engine-published position at that moment — do not schedule a redraw from `process()`.
- The engine writes position/state to a lock-free snapshot (`P-16`); the render thread interpolates to
  the current display time between snapshots.
- Cap and align to the display's refresh; on ProMotion, let the display link pick the rate rather than
  free-running.

## Example — wrong
```cpp
// In the audio callback: nudge the GUI to repaint every processed buffer.
emit bufferProcessed();   // couples redraw cadence to the audio period; wrong clock, RT-adjacent work
```

## Example — right
```cpp
// GUI display tick: sample the engine's published position and redraw once per refresh.
double pos = VisualPlayPosition::getAtNextVSync();   // engine-published, read on the display clock
waveform->render(pos);
```

## Detection
Review: a repaint/redraw scheduled from `process*()` or gated on buffer count; frame rate that tracks
the audio buffer rate instead of the display refresh.

## Cross-references
Keeps GPU work off the audio deadline (`P-21`); pairs with `P-22`. Protects `P-02`.
