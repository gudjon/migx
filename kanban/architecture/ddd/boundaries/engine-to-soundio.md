# Seam: engine → soundio (the master buffer to the device callback)

**Contexts:** `arch-engine-realtime` (src/engine/) → `arch-audio-io` (src/soundio/).
**Direction:** the engine produces; soundio consumes. But the *clock* runs the other way — soundio's
callback originates the RT thread and **pulls** from the engine. Data-down, deadline-up.

## What crosses
The mixed master (and headphone) buffer: a block of interleaved `CSAMPLE` for one callback's worth of
frames. This is the single audio payload leaving the engine each buffer.

## The mechanism
`EngineMixer` (`engine/enginemixer.h`) is an `AudioSource` (`soundio/soundmanagerutil.h`).
`SoundManager` registers it via `registerOutput(AudioOutput, AudioSource*)`; on each device tick the
backend's `callbackProcess` (e.g. `SoundDevicePortAudio::callbackProcess`) calls
`onDeviceOutputCallback`, which pulls the buffer from the registered source and writes it to the
device. The engine's `process()` runs *inside* that callback stack — same RT thread, no thread hop.

## The invariant this seam enforces
- **The callback is the deadline (`P-02`/`AP-02`):** everything reachable from the pull — the whole
  engine `process()` graph — must allocate nothing, lock nothing, do no I/O, never block. A miss is an
  audible underrun.
- **Pull, not push (`P-20`/`AP-14`):** soundio requests the buffer; it never drives engine object
  lifetime and the engine never delivers a synchronous slot onto the callback.
- **Tail-gated perf (`P-03`/`P-18`/`AP-11`):** changes to this path prove p99/max latency and zero
  underruns, not a mean.

## Notes
Because there is no thread boundary here (the engine runs *on* the audio callback), the seam is one of
*discipline*, not handoff — the lock-free handoffs are at the seam's edges (`control-to-engine.md` in,
`engine-to-waveform.md` out).
