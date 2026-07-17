---
id: arch-vinylcontrol
type: ddd-bounded-context
title: "vinylcontrol — timecode-vinyl signal processing into deck control"
owns:
  - src/vinylcontrol/           # VinylControlManager, VinylControlProcessor, VinylControlXwax, SteadyPitch, signal widget
exclude: []
thread_domain: rt-audio
rt_safety: hard
subdomain: supporting
upstream: [arch-audio-io, arch-control-messaging]
downstream: [arch-engine-realtime]
maturity: operational
fork_delta: upstream-tracking
agents_md: src/vinylcontrol/AGENTS.md
last_audited: "2026-07-17"
---

# vinylcontrol — bounded context

Turns a timecode-vinyl (or CDJ) input signal into deck rate and position. `VinylControlProcessor`
receives the control-vinyl input buffers on the **audio callback thread**, decodes the timecode via
`VinylControlXwax` (the xwax DSP), smooths it with `SteadyPitch`, and writes the resulting pitch/scratch
back to the engine deck through `ControlObject`s. Because it runs on the RT input callback it is
`rt_safety: hard`. Enable/disable, lead-in, and mode selection are ordinary GUI-thread config. Pointers,
never copies — `src/vinylcontrol/` is the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `VinylControlManager` | `vinylcontrol/vinylcontrolmanager.cpp` | GUI-side lifecycle; binds inputs to processors |
| `VinylControlProcessor` | `vinylcontrol/vinylcontrolprocessor.cpp` | RT-side input consumer; drives per-deck `VinylControl` |
| `VinylControl` | `vinylcontrol/vinylcontrol.cpp` | abstract per-deck decode → rate/position |
| `VinylControlXwax` | `vinylcontrol/vinylcontrolxwax.cpp` | xwax timecode DSP implementation |
| `SteadyPitch` | `vinylcontrol/steadypitch.cpp` | pitch smoothing / steady-state estimation |
| `VinylControlSignalWidget` | `vinylcontrol/vinylcontrolsignalwidget.cpp` | GUI signal-quality scope (off-RT) |

## Invariants (an agent MUST respect these)
- **RT boundary (hard, `P-02`/`AP-02`):** the input-callback path (`VinylControlProcessor` →
  `VinylControl::analyzeSamples`) allocates nothing, locks nothing, does no I/O, never blocks.
- **Cross-thread out via ControlObject (`P-16`):** decoded pitch/position reach the engine deck through
  the lock-free `ControlObject` bus, never a shared lock or synchronous slot.
- **Object lifetime off the RT thread (`P-17`):** processors/decoders are created and destroyed by
  `VinylControlManager` on the GUI thread; never `new`/`delete` on the callback.
- **Single writer (`P-06`/`AP-03`):** vinyl is the authoritative writer of the deck rate control only
  while engaged; it must not race the engine's own rate writer.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `timecode` | the control-tone encoded on the vinyl/CD | a track's musical time / beatgrid (arch-track-model) |
| `pitch` | decoded playback-speed ratio from the signal | musical key/pitch (arch-analyzer keys) |
| `signal quality` | timecode decode confidence | audio signal level / VU |
| `lead-in` | needle-drop start region before lock | a track intro cue (arch-track-model) |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| in | control-vinyl input buffer | arch-audio-io | `SoundManager` input callback | boundaries/engine-to-soundio.md |
| out | deck rate / scratch / position | arch-engine-realtime | `ControlObject` atomics | boundaries/control-to-engine.md |
| in | enable / mode / lead-in config | arch-control-messaging | `ControlProxy` | — |

## Key patterns (cited, not restated)
`P-02`, `AP-02`, `P-16`, `P-17`, `P-06`, `AP-03` — see `kanban/patterns/`. Root house rules: `/AGENTS.md`.
This context is a second RT-input consumer alongside the engine, held to the same audio-deadline physics.
