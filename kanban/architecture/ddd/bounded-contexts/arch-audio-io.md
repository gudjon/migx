---
id: arch-audio-io
type: ddd-bounded-context
title: "audio-io — the sound-device layer that originates the RT audio thread"
owns:
  - src/soundio/                # SoundManager, SoundDevice*, PortAudio/Pipewire/Network backends, enumerators, SoundManagerConfig
exclude: []
thread_domain: rt-audio origin
rt_safety: hard
subdomain: core
upstream: [arch-engine-realtime]
downstream: [arch-engine-realtime]
maturity: hardened
fork_delta: upstream-tracking
agents_md: src/soundio/AGENTS.md
last_audited: "2026-07-17"
---

# audio-io — bounded context

The bridge to the audio hardware. `SoundManager` opens the devices, wires each backend's audio
callback, and **originates the real-time thread** — the driver calls back into `SoundDevice*`, which is
the deadline every downstream `rt_safety: hard` context must meet. The callback pulls the mixed master
buffer from the engine (registered as an `AudioSource`) and hands it to the device. Device
enumeration and configuration are ordinary GUI/worker-thread code. Pointers, never copies —
`src/soundio/` is the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `SoundManager` | `soundio/soundmanager.cpp` | opens devices, registers `AudioSource`s, owns the callback wiring |
| `SoundDevice` | `soundio/sounddevice.cpp` | abstract device; per-buffer `callbackProcess` contract |
| `SoundDevicePortAudio` | `soundio/sounddeviceportaudio.cpp` | PortAudio backend; the `paV19Callback` RT origin |
| `SoundDevicePipewire` | `soundio/sounddevicepipewire.cpp` | PipeWire backend |
| `SoundDeviceNetwork` | `soundio/sounddevicenetwork.cpp` | network sink (broadcast/record clock) |
| `*Enumerator` | `soundio/portaudioenumerator.cpp`, `pipewireenumerator.cpp`, `networkenumerator.cpp` | GUI-thread device discovery |
| `SoundManagerConfig` | `soundio/soundmanagerconfig.cpp` | persisted sample-rate/buffer/routing config |
| `AudioSource` / `AudioOutput` | `soundio/soundmanagerutil.h` | the pull interface the engine implements |

## Invariants (an agent MUST respect these)
- **The callback is the RT deadline source (`P-02`/`AP-02`):** `callbackProcess`-reachable code
  allocates nothing, locks nothing, does no I/O, never blocks. A missed deadline is an audible underrun.
- **Enumeration & config are off-RT:** `*Enumerator` and `SoundManagerConfig` run on the GUI/worker
  thread; device open/close and buffer sizing happen there, never inside the callback (`P-17`).
- **Pull, don't push:** the callback *requests* the master buffer from a registered `AudioSource`
  (the engine) — it does not drive engine object lifetime. Cross-thread signalling via `ControlObject`/
  lock-free handoff, never a synchronous Qt slot on the callback (`P-20`, `AP-14`).
- **Perf work on this path needs a tail benchmark** (p99/max + zero underruns), not a mean (`P-03`/`P-18`).

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `callback` | the driver-invoked per-buffer RT entry point | a Qt signal/slot callback (GUI) |
| `device` | a `SoundDevice*` audio interface | an `EngineChannel` (arch-engine-realtime) |
| `channel` | a physical interface in/out channel | an `EngineChannel` deck/bus |
| `buffer size` | frames per callback (latency knob) | a decoded track buffer (arch-sources-decode) |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| in | mixed master `CSAMPLE` buffer | arch-engine-realtime | `AudioSource::requestBuffer` on the callback | boundaries/engine-to-soundio.md |
| out | the RT deadline / callback tick | arch-engine-realtime | driver → `callbackProcess` origin | boundaries/engine-to-soundio.md |
| in | device selection / routing | arch-preferences | `SoundManagerConfig` | — |

## Key patterns (cited, not restated)
`P-02`, `AP-02`, `P-17`, `P-20`, `AP-14`, `P-03`, `P-18` — see `kanban/patterns/`. Root house rules:
`/AGENTS.md`. This context *is* the RT clock the engine card's hard invariants are measured against.
