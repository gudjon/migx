# AGENTS.md — soundio/ (sound-device layer; origin of the RT audio thread)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-audio-io.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
The bridge to the audio hardware. `SoundManager` opens the devices, wires each backend's audio
callback, and **originates the real-time thread**: the driver calls back into a `SoundDevice*`, which
pulls the mixed master buffer from the engine (registered as an `AudioSource`) and hands it to the
device. This callback is the deadline every downstream `rt_safety: hard` context must meet.

## Key files
- `soundmanager.cpp/.h` — opens devices, registers `AudioSource`s, owns `onDeviceOutputCallback` wiring.
- `sounddevice.cpp/.h` — abstract device; the per-buffer `callbackProcess` contract.
- `sounddeviceportaudio.cpp` — PortAudio backend; the `paV19Callback`/`callbackProcess` RT origin.
- `sounddevicepipewire.cpp` — PipeWire backend. `sounddevicenetwork.cpp` — network sink.
- `portaudioenumerator.cpp`, `pipewireenumerator.cpp`, `networkenumerator.cpp` — GUI-thread discovery.
- `soundmanagerconfig.cpp` — persisted sample-rate/buffer/routing config.
- `soundmanagerutil.h` — `AudioSource`/`AudioOutput`/`AudioInput` — the pull interface the engine implements.

## Invariants you MUST respect
- **The callback is the RT deadline source:** `callbackProcess`-reachable code allocates nothing, locks
  nothing, does no I/O, never blocks — a missed deadline is an audible underrun. `P-02`, `AP-02`.
- **Enumeration & config are off-RT:** `*Enumerator` and `SoundManagerConfig` run on the GUI/worker
  thread; device open/close and buffer sizing happen there, never inside the callback. `P-17`.
- **Pull, don't push:** the callback *requests* the master buffer from a registered `AudioSource`; it
  does not drive engine object lifetime. No synchronous Qt slot on the callback. `P-20`, `AP-14`.
- **Perf changes need a tail benchmark** (p99/max + zero underruns), not a mean. `P-03`, `P-18`, `AP-11`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R SoundManager` (GoogleTest; e.g. `soundmanagerconfig_test`,
  `soundproxy_test` and related I/O tests in `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Any allocation, lock, or blocking call on a `callbackProcess`-reachable path.
- Opening/closing devices or resizing buffers from inside the callback.
- Letting a downstream context push work synchronously into the callback thread.

## Cross-references
Downstream: `src/engine/AGENTS.md` — the engine's `EngineMixer` is the `AudioSource` this callback
pulls, and the callback is the clock its hard invariants are measured against. Config in from
`src/preferences/`. Seam: `kanban/architecture/ddd/boundaries/engine-to-soundio.md`.
