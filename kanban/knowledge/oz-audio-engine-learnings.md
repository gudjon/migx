---
id: oz-audio-engine-learnings
type: knowledge
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: >
  Distilled by reading /Users/gudjon/code/oz-platform audio work. Files read:
  kanban/initiatives/initiative-audio-stack-2026-q3.md (the Q3 audio initiative),
  kanban/tasks/task-audio-ingest-tick-sync.md, task-audio-tdoa-localization.md,
  task-audio-broadcast-mixer.md (forward-looking ML/spatial tasks),
  apps/edge/venue_video_router/cushm2rawvideo/audioinput.cpp + audiooutput.cpp + audioinput.h
  (JACK RT capture/playback + SPSC ring buffer + drift reconciliation),
  apps/edge/venue_video_router/audiorouter/audiorouter.cpp + ladspawrapper.cpp
  (JACK LADSPA effects host: RT-capability gating, RT param-fading, inline metering),
  apps/edge/oz-audio-playback/ (GStreamer playback service, Python),
  kanban/planning/26-07-15-sunil-amc--audio-mixer-commentator-uplift/README.md
  (the "green probes, silent output" verification lesson).
  Cross-referenced against Migx: kanban/architecture/README.md, the arch-engine-realtime and
  arch-audio-io DDD cards, kanban/patterns/AGENTS.md (P-02/P-16/P-17/P-18/P-34...), and
  kanban/knowledge/arcflow-m4-perf-techniques.md (companion, not to be duplicated).
---

# oz-platform audio → Migx: transferable RT-audio-engine learnings

Research input for [[initiative-apple-silicon]] and the RT audio engine (arch-engine-realtime,
arch-audio-io). Companion to [[arcflow-m4-perf-techniques]] — where that note mines M4 *compute*
(vDSP/AMX, QoS, Metal), this one mines oz's *streaming audio* code for RT-safety and clock/handoff
technique. **We take the technique, not the code** — and oz's audio domain (robotics/CV) is dropped.

## TL;DR — honest scope of what oz has

oz-platform's audio splits cleanly in two, and only one half is transferable:

1. **A working Linux/JACK real-time audio router** (`apps/edge/venue_video_router/`, C-style C++). This
   is genuine RT streaming code — process callbacks, ring buffers, a LADSPA effects host, parameter
   fading, inline metering. **This is where the transferable technique lives**, and it maps almost
   1:1 onto Migx's `src/soundio` + `src/engine` + `src/engine/effects`.
2. **A forward-looking Q3-2026 "Audio Stack" initiative** (`initiative-audio-stack-2026-q3.md` + four
   `task-audio-*` files). This is ML/CV/robotics: 12-mic sports-event detection (PANNs CNN14 on CUDA),
   TDOA whistle localization (GCC-PHAT), Ambisonics broadcast mix (libspatialaudio), all glued with
   NATS + a `tickperframe` clock. **Almost none of this is transferable** — it is oz's domain. The one
   reusable idea buried in it is *media-clock alignment discipline* (learning L6).

**Apple-Silicon / M4 finding — say it plainly:** oz-platform contains **zero** Accelerate/vDSP,
CoreAudio, Metal, or Apple-Silicon-specific audio code. It targets Linux (JACK/GStreamer/LADSPA) on
edge servers and Jetson/CUDA on the GPU side. So on the **M4 DSP push specifically, oz adds nothing
beyond [[arcflow-m4-perf-techniques]]** — arcflow remains the sole internal source for vDSP/AMX/SME,
P-core QoS, and Metal-UMA technique. Do **not** expect a CoreAudio-workgroup or vDSP recipe here.

**Where oz beats arcflow as a reference:** arcflow is *throughput* compute (offline batch, GPU-first).
oz's audiorouter is *genuine hard-real-time streaming* — a driver-driven callback on a deadline, the
same shape as Migx's `SoundManager` callback. On the **RT-safety / lock-free-handoff / clock-sync**
axis oz is a closer analogue to Migx than arcflow is. That is its value: it *reinforces* P-02/P-16/P-17
with a concrete second implementation (and a couple of cautionary bugs), and it surfaces three
engine-side pattern candidates arcflow did not.

---

## A. Transferable technique (RT audio engine)

### L1 — The RT process callback does only memcpy + arithmetic; no alloc/lock/I/O
- **What oz does** (`audioinput.cpp:34` `audioinputprocess`, `audiooutput.cpp:35`,
  `ladspawrapper.cpp:16` `jackaudioinputprocess`): every JACK `process` callback is pure — it fetches
  port buffers, `memcpy`s samples, runs the plugin's `run()`, computes peak/phase in a tight loop, and
  returns. No `malloc`, no mutex, no file I/O, no JACK graph mutation on that thread. All allocation
  (`malloc`/`calloc` of port arrays and plugin buffers) happens in `init_*`/the constructor, off the
  callback.
- **Why it helps Migx**: this is P-02 realised in a second, independent codebase. A JACK `process`
  callback and a CoreAudio/PortAudio callback carry the *identical* contract — a missed deadline is an
  audible xrun. oz is a clean worked example to point new engine contributors at.
- **Maps to**: **P-02** (never allocate/lock on the RT thread), **AP-14** (RT thread blocks). Migx
  subsystem: `src/soundio` `callbackProcess`, `src/engine` `process*()`.
- **Dossier?** No new dossier — it *confirms* an existing hard invariant.

### L2 — SPSC ring buffer for the RT→consumer handoff (+ a cautionary data-race bug)
- **What oz does** (`audioinput.cpp`): the JACK callback is the producer, writing into a shared
  `audiobuffer[65536]` via `buf_in`; a non-RT consumer drains it via `getaudiosamples()`/`buf_out`.
  Classic single-producer/single-consumer ring — the RT side never blocks on the reader.
- **The cautionary part (take the shape, not the impl)**: oz's indices are plain `uint16_t`
  (`buf_in`, `buf_out`) shared across threads with **no atomics and no memory barriers**, relying on
  natural `uint16` wraparound at exactly 65536. That is a textbook data race (torn/stale reads, UB) and
  would trip TSan instantly. Migx's `util/fifo.h` (the P-16 canonical handoff) is the *correct* version
  of this idea: atomic indices, acquire/release ordering, power-of-two masking.
- **Why it helps Migx**: reinforces P-16 by showing both the right instinct (lock-free SPSC ring across
  the RT boundary) and the exact trap (non-atomic indices) that P-32's TSan gate exists to catch. Good
  teaching contrast.
- **Maps to**: **P-16** (lock-free GUI↔engine handoff), **P-32** (engine tests assert TSan-clean).
  Migx subsystem: `util/fifo.h`, the engine↔waveform and engine↔GUI taps.
- **Dossier?** No — cite it as the "why we use util/fifo.h and TSan" cautionary example.

### L3 — Async clock/rate reconciliation by drop-one/dup-one frame (resampler-free)
- **What oz does** (`audioinput.cpp:103` `getaudiosamples`): the JACK capture clock and the downstream
  consumer clock run free and drift. Instead of a resampler, oz watches the ring fill level: if
  `available > 3×ideal` it **drops one frame** (`buf_out += bytes_per_frame`); if `available < 2×ideal`
  it **duplicates one frame** (copies the last 4 bytes forward). This keeps the buffer from over/under-
  running without a sample-rate converter.
- **Why it helps Migx**: Migx has to reconcile two independent clocks whenever a device's real rate
  drifts from the nominal rate, or across the network sink (`SoundDeviceNetwork`, broadcast/record).
  Drop/dup is the cheap, RT-safe fallback when a full async resampler is too expensive or not yet
  wired. **Caveat to carry**: drop/dup is audible (a click/pitch blip) — it is a *fallback*, not the
  primary path; Migx should prefer proper async resampling (P-14: prove the candidate) and reserve
  drop/dup for degraded/emergency reconciliation, gated behind a benchmark.
- **Maps to**: clock/sync in `src/engine/sync` + `src/soundio` (device-vs-engine rate). Pattern:
  **NEW pattern candidate** — *"Reconcile two free-running audio clocks with a bounded fill-window;
  prefer async resample, fall back to drop/dup only under a measured jitter budget."* Relates to P-18
  (the tail is where under/overrun shows).
- **Dossier?** Weak seed only — could inform a future `src/soundio` network/clock-sync dossier; not
  worth a standalone dossier on its own.

### L4 — RT-safe parameter smoothing (de-zippering) computed inside the callback
- **What oz does** (`ladspawrapper.cpp:22-36`): when a control value changes, it isn't snapped. The
  callback ramps each fading control toward `targetvalue` by `rate = diff * (nframes/samplerate) /
  fadetime` per block, clamping when it arrives. `dt` for the ramp is derived from the block size
  (`(float)nframes / 48000`). This is classic control smoothing / de-zippering done allocation-free on
  the RT thread; the *decision* to fade (target + fadetime) is set from the non-RT config path.
- **Why it helps Migx**: exactly the shape Migx wants for gain/EQ/crossfader/effect-param changes —
  ControlObject (non-RT) sets a target; the engine ramps toward it per buffer with an explicit `dt`.
  Prevents zipper noise without locking or reading Qt on the RT thread.
- **The AP-15 smell to *not* copy**: oz hardcodes `48000` in the `dt` computation. Migx must derive
  `dt` from the actual engine sample rate (P-17's explicit-dt discipline; AP-15 no hardcoded tuning).
- **Maps to**: **P-17** (explicit dt off the RT thread's control), the control→engine seam
  (`boundaries/control-to-engine.md`), `src/engine` gain/EQ stages, `src/engine/effects`. Pattern:
  **NEW pattern candidate** — *"Smooth control changes with a per-buffer ramp toward a target set
  off-RT; derive dt from the real sample rate, never a literal."*
- **Dossier?** Good candidate to fold into an effects-chain / engine-control smoothing dossier.

### L5 — Enforce the RT contract at the plugin-admission boundary
- **What oz does** (`ladspawrapper.cpp:85`): before instantiating any LADSPA plugin it checks
  `LADSPA_IS_HARD_RT_CAPABLE(...)` and **throws/refuses** if the plugin isn't hard-RT-capable — "In
  initial version only support plugins that fit directly with Jack's model of zero latency callbacks."
  The RT-safety contract is checked *where third-party code is admitted*, not hoped-for at runtime.
- **Why it helps Migx**: Migx hosts third-party-ish DSP (LADSPA/LV2 via `src/effects`, plus native
  effects). The lesson: gate on the RT-capability flag at load/instantiate time and reject
  non-RT-capable units (or route them to a non-RT bus), rather than discovering the violation as an
  xrun in the field. Turns a runtime hazard into a load-time classified failure.
- **Maps to**: **P-02** enforced at the boundary, **P-34** (fail classified, not silent), arch-effects-
  chain. Pattern: **NEW pattern candidate** — *"Admit an effect onto the RT graph only if it declares
  RT-capability; reject or sandbox the rest at load time."*
- **Dossier?** Fold into an effects-chain hardening dossier.

### L6 — Media-clock alignment: stamp every buffer, derive samples-per-tick at runtime
- **What oz does** (`task-audio-ingest-tick-sync.md`): every audio buffer is stamped with
  `{tick_count, generation, framerate}` against a master clock; `SAMPLES_PER_TICK` is **computed from
  the `framerate` field at runtime, never hardcoded** (the task explicitly "eliminates hardcoded
  48000/50 = 960"); a `generation` counter handles tick rollover; startup fails fast if the clock
  source never arrives.
- **Why it helps Migx (technique only)**: the *discipline* transfers even though the mechanism
  (NATS `tickperframe`, sports ticks) is pure oz-domain. Any time Migx aligns audio to another clock —
  beat-grid/tempo sync (`EngineSync`/`InternalClock`), broadcast/record sample-accurate timestamps,
  waveform play-position — the rules are the same: (a) derive samples-per-unit from the live rate, not
  a literal; (b) carry an explicit generation/rollover counter; (c) fail fast if the clock is absent.
- **Maps to**: **P-17** (explicit dt / derive from rate), **AP-15** (no hardcoded 44100/48000), **P-34**
  (fail-fast, no silent fallback), `src/engine/sync`. 
- **Dossier?** No — a discipline reminder, already covered by P-17/AP-15.

### L7 — Fail-fast device handling; device identity comes from config, never hardcoded
- **What oz does** (`task-audio-ingest-tick-sync.md` AC 8-9): "Service fails fast with
  `IntegrationError` if audio device not available at startup — **no fallback**"; "Loads audio device
  config from `edge.json` — **no hardcoded device names**." The broadcast-mixer task echoes it:
  a missing mic channel logs a warning and degrades explicitly, "**no silent failure**."
- **Why it helps Migx**: matches Migx's own `P-34` (fail classified — never a silent fallback) and
  `AP-16` (silent audio-error swallow). oz's `SoundManagerConfig` analogue confirms device selection /
  routing belongs in off-RT config, and an unavailable device is a *classified startup failure*, not a
  quiet drop to silence.
- **Maps to**: **P-34**, **AP-16**, arch-audio-io (`SoundManagerConfig`, enumeration off-RT).
- **Dossier?** No — reinforces existing patterns.

### L8 — Lightweight inline metering: peak + hold-and-decay, allocation-free
- **What oz does** (`audioinput.cpp:137`, `ladspawrapper.cpp:51-68`): peak amplitude and a stereo
  phase check are computed *in* the callback with a hold/decay counter (`peaktime++` until a window,
  then reset) — no allocation, just a running max and an integer timer. Feeds meters/monitoring.
- **Why it helps Migx**: the correct shape for VU/peak meters and phase/correlation displays — compute
  the reduction inline on the RT thread (it's cheap), publish the scalar lock-free to the GUI. Don't
  ship raw buffers to the GUI to meter them there.
- **Maps to**: **P-16** (publish the scalar, not the buffer), meter taps → `src/waveform`/GUI. Note the
  M4 angle from [[arcflow-m4-perf-techniques]] A1: if a meter reduction ever gets heavy, the vDSP
  `vDSP_maxmgv`/`vDSP_rmsqv` route applies — but prove it's alloc-free before using it on the RT path.
- **Dossier?** No — minor, folds into any metering work.

### L9 — Verification lesson: green health-probes that can't see the signal path
- **What oz found** (`26-07-15-sunil-amc--audio-mixer-commentator-uplift/README.md`): the entire
  broadcast carried **zero audio** while *every* health gate reported green — `jackd` answered,
  `audiorouter` listened on its port, the egress script contained the string `-c:a aac` — yet the JACK
  output bus `xfade:Output` had zero connections and nothing traversed the desk. The probes proved
  *liveness*, never *flow*. The fix replaced them with checks that measure whether audio is actually
  non-silent end-to-end.
- **Why it helps Migx**: a pure cross-domain reinforcement of Migx's harness doctrine. A benchmark or
  gate that asserts "the component is up / the flag is present" is a **tautological green** (AP-10 /
  AP-01 green-over-red). An RT-audio gate must assert the *observable output* — zero underruns, actual
  non-silent samples, the p99 deadline — not that the callback is registered. And the author's own
  probe is not the verdict (P-08 generator ≠ evaluator).
- **Maps to**: **P-03** (benchmark-as-contract), **P-18** (assert the tail, not liveness), **P-08**,
  **AP-01**, **AP-10**, **P-32**.
- **Dossier?** No — a doctrine reinforcement for how M4/RT benchmark contracts must be written.

---

## B. Explicitly oz-domain — drop these (not transferable)

These are oz's robotics/broadcast-CV problem, with no Migx analogue. Listed so a future reader doesn't
re-mine them:

- **ML game-event detection** — PANNs CNN14 (PyTorch/CUDA) fine-tuned on whistle/ball-contact/crowd,
  publishing `audio.events`. Migx has no ML-inference audio path.
- **TDOA source localization** — GCC-PHAT cross-correlation + hyperbolic lateration/RANSAC over a
  105×68 m 12-mic array to put a whistle on a pitch coordinate (`task-audio-tdoa-localization.md`).
  Pure sensor-fusion for sports; irrelevant to a DJ mixer.
- **Ambisonics / HOA broadcast mix** — libspatialaudio 3rd-order encode + stereo/binaural decode,
  camera-follow mic selection, event-driven ducking keyed to `cameracontrol.directive`
  (`task-audio-broadcast-mixer.md`). The *crossfade/gain-ramp mechanics* are the same math as L4 (so
  the technique is captured there); the *spatial-audio and camera-follow semantics* are oz-domain.
- **Transport & glue** — NATS topics (`audio.events`, `audio.mix.output`), the `tickperframe` protocol,
  Dante/AES67 venue cabling, `oz up`/`edge.json` orchestration. All oz infra.
- **GStreamer/JACK/LADSPA + Jetson/CUDA stack** — the whole runtime is Linux/edge-server, not
  macOS/CoreAudio. No Apple-Silicon carry-over.

---

## C. Where oz reinforces vs. differs from arcflow

| Axis | arcflow ([[arcflow-m4-perf-techniques]]) | oz-platform (this note) |
|---|---|---|
| Workload shape | Throughput compute (offline batch, GPU-first) | **Hard-real-time streaming** (driver callback on a deadline) — closer to Migx's engine |
| RT-safety technique | Implicit (compute, not RT) | **Explicit worked examples** (L1, L2, L4, L5) — a second implementation of P-02/P-16/P-17 |
| Apple-Silicon / M4 | Rich: vDSP/AMX/SME, P-core QoS, Metal UMA/heap/pipeline-cache | **None** — Linux/JACK/CUDA; contributes nothing new to the M4 push |
| Clock/sync | Not addressed | **Adds** drop/dup rate reconciliation (L3) + media-clock alignment discipline (L6) |
| Param smoothing / effect admission | Not addressed | **Adds** RT de-zippering (L4) and RT-capability gating at load (L5) |
| Verification doctrine | Bench methodology (warmup/median/baseline) | **Adds** the "green probe that can't see flow" failure mode (L9) |

Net: **no overlap or contradiction** with arcflow — the two are complementary. arcflow owns the M4
compute axis; oz owns the RT-streaming-safety axis. Neither changes the other's conclusions.

---

## D. Does this warrant a dossier?

**No new standalone DSP/ASI dossier — arcflow already seeds the two that matter** (DSP-ACCEL for
vDSP/analyzer, ASI-WORKER-POOL for QoS/morsel). oz contributes **no** M4/Accelerate technique to seed a
new perf dossier.

What oz *does* seed is **three engine-side pattern candidates** worth promoting into
`kanban/patterns/` and folding into existing engine/effects work (not a perf-benchmark dossier):

1. **RT parameter smoothing with off-RT target + real-sample-rate dt** (L4) — effects-chain / control seam.
2. **Admit an effect onto the RT graph only if it declares RT-capability; reject/sandbox at load** (L5) — effects-chain hardening.
3. **Bounded fill-window clock reconciliation (prefer resample, drop/dup as measured fallback)** (L3) — `src/soundio` clock/network sync.

Plus L2 (util/fifo.h + TSan cautionary example) and L9 (how to *write* the RT benchmark gate so it
asserts flow, not liveness) as doctrine reinforcements. If any of these three is pursued, it slots into
an existing effects-chain or soundio dossier rather than a fresh one.
