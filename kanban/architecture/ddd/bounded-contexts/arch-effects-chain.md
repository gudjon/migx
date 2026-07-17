---
id: arch-effects-chain
type: ddd-bounded-context
title: "effects-chain — the effect graph processed inside the RT engine"
owns:
  - src/engine/effects/         # EngineEffectsManager, EngineEffect, EngineEffectChain, EngineEffectsDelay — the RT side
  - src/effects/                # EffectsManager, EffectChain, EffectSlot, backends/, chains/, presets/, EffectsMessenger — the GUI side
exclude: []
thread_domain: rt-audio + gui
rt_safety: hard
subdomain: core
upstream: [arch-control-messaging, arch-engine-realtime]
downstream: [arch-engine-realtime]
maturity: operational
fork_delta: upstream-tracking
agents_md: src/effects/AGENTS.md
last_audited: "2026-07-17"
---

# effects-chain — bounded context

The effect graph, split across the RT boundary. The **GUI side** (`src/effects/`) owns the object model
— `EffectsManager`, the `EffectChain`/`EffectSlot` tree, the loaded backends and the preset store — and
is edited on the GUI thread. The **RT side** (`src/engine/effects/`) is what the engine actually runs
per buffer: `EngineEffectsManager` applies each `EngineEffectChain` inside the mix. State crosses the
two halves through `EffectsMessenger`, a lock-free message queue — never a shared lock. Everything
reachable from an `EngineEffect::process()` is `rt_safety: hard`. Pointers, never copies —
`src/effects/` + `src/engine/effects/` are the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `EffectsManager` | `effects/effectsmanager.cpp` | GUI-side root; owns chains, backends, presets, messenger |
| `EffectChain` / `EffectSlot` | `effects/effectchain.cpp`, `effects/effectslot.cpp` | GUI-side chain and per-slot effect model |
| `EffectsBackendManager` | `effects/backends/effectsbackendmanager.cpp` | loads backends (builtin, LV2, AudioUnit) |
| `BuiltInBackend` | `effects/backends/builtin/builtinbackend.cpp` | native DSP effects |
| `AudioUnitBackend` | `effects/backends/audiounit/audiounitbackend.mm` | macOS Audio Unit host (Obj-C++) |
| `EffectsMessenger` | `effects/effectsmessenger.cpp` | GUI→RT lock-free message queue |
| `EffectChainPresetManager` | `effects/presets/effectchainpresetmanager.cpp` | save/restore chain presets |
| `EngineEffectsManager` | `engine/effects/engineeffectsmanager.cpp` | RT-side: runs the effect graph per buffer |
| `EngineEffect` / `EngineEffectChain` | `engine/effects/engineeffect.cpp`, `engineeffectchain.cpp` | RT-side effect node / chain |

## Invariants (an agent MUST respect these)
- **RT boundary (hard, `P-02`/`AP-02`):** `EngineEffect::process()`-reachable code allocates nothing,
  locks nothing, does no I/O, never blocks. A slow effect is an audible underrun (`AP-11`).
- **State crosses via the messenger, not a lock (`P-16`):** GUI edits reach the RT graph as
  `EffectsMessenger` messages over a lock-free queue; the RT side never dereferences a GUI `EffectSlot`.
- **Object lifetime off the RT thread (`P-17`):** effects are constructed/loaded/destroyed on the GUI
  thread and handed to the engine by pointer; never `new`/`delete` an effect on the callback.
- **Single writer per parameter control (`P-06`/`AP-03`):** each effect-parameter `[Group],key` has one
  authoritative writer; other contexts read via `ControlProxy`.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `chain` | an `EffectChain` of ordered `EffectSlot`s | the RT signal chain sources→engine→soundio |
| `effect` | a loaded DSP unit (`EffectSlot` GUI / `EngineEffect` RT) | an "effect" as a side effect of a call |
| `messenger` | the `EffectsMessenger` GUI→RT queue | the `[Group],key` control bus (arch-control-messaging) |
| `backend` | a source of effects (builtin/LV2/AudioUnit) | an audio device backend (arch-audio-io) |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| out | processed audio in the mix | arch-engine-realtime | `EngineEffectsManager` called from `process()` | boundaries/engine-to-soundio.md |
| in | effect-graph edits | arch-engine-realtime | `EffectsMessenger` lock-free queue | — |
| in | parameter/meta controls | arch-control-messaging | `ControlObject` / `ControlProxy` | — |

## Key patterns (cited, not restated)
`P-02`, `AP-02`, `P-16`, `P-17`, `P-06`, `AP-03`, `AP-11` — see `kanban/patterns/`. Root house rules:
`/AGENTS.md`. The GUI/RT split here is the effects-domain instance of the engine's hard RT boundary.
