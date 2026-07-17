# Seam: engine → waveform (lock-free tap of play position)

**Contexts:** `arch-engine-realtime` (src/engine/) → `arch-waveform-render` (src/waveform/).
**Direction:** the engine publishes; the renderer samples. Crucially, the two run on **different
clocks** — the engine on the audio callback, the renderer on the display/vsync clock.

## What crosses
Play position and related visual state — where each deck's playhead is, for waveform and spinny
rendering. Read-only snapshots, never a handle into engine state.

## The mechanism
`EngineBuffer` writes into a `VisualPlayPosition` (`waveform/visualplayposition.h`), whose payload
`VisualPlayPositionData` is stored in a `ControlValueAtomic<VisualPlayPositionData>` — a lock-free
double-buffer. The engine calls `set()` on the audio thread; the renderer reads the latest published
snapshot on the GPU/display thread. No lock, no allocation, no blocking on either side.

## The invariant this seam enforces
- **Lock-free RT handoff (`P-16`):** the atomic double-buffer is the only shared state; the audio
  thread never waits on the render thread and vice versa.
- **Render on the display clock, not the audio clock (P-16/P-23 spirit):** the renderer samples the
  latest snapshot at vsync and interpolates; a slow or stalled GPU frame can **never** gate the audio
  deadline (`AP-02`/`AP-14`). Dropping a video frame is fine; dropping an audio buffer is not.
- **Lifetime off RT (`P-17`):** the `VisualPlayPosition` object graph is managed off the callback.

## Notes
This is the reference example of "the audio deadline owns no downstream latency": the waveform tap is
deliberately one-way and eventually-consistent so the render pipeline can be as slow as it needs to be
without ever touching house physics.
