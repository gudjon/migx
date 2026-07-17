---
id: arch-mixer-decks
type: ddd-bounded-context
title: "mixer-decks — deck/sampler/player lifecycle owner straddling RT and GUI"
owns:
  - src/mixer/                  # PlayerManager, Deck, Sampler, PreviewDeck, Microphone, Auxiliary, BaseTrackPlayer, SamplerBank
exclude: []
thread_domain: rt-audio + gui
rt_safety: hard
subdomain: core
upstream: [arch-control-messaging, arch-library-db, arch-audio-io]
downstream: [arch-engine-realtime]
maturity: hardened
fork_delta: upstream-tracking
agents_md: src/mixer/AGENTS.md
last_audited: "2026-07-17"
---

# mixer-decks — bounded context

The lifecycle owner of the playback objects: `PlayerManager` creates every `Deck`, `Sampler`,
`PreviewDeck`, `Microphone`, and `Auxiliary`, wires each to its `EngineChannel` and audio I/O, and
loads tracks into them. It **straddles two thread domains** — players are constructed/owned on the GUI
thread (Qt object tree) yet each one's engine node processes on the RT thread. Getting the ownership
handoff right is the whole job; the RT-safe processing itself lives in arch-engine-realtime. Pointers,
never copies — `src/mixer/` is the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `PlayerManager` | `mixer/playermanager.cpp` | creates/owns all players; maps `[ChannelN]` groups to objects |
| `BaseTrackPlayer` / `BaseTrackPlayerImpl` | `mixer/basetrackplayer.cpp` | shared deck-like player: track load, engine wiring |
| `Deck` | `mixer/deck.cpp` | a playback deck (`BaseTrackPlayerImpl`) |
| `Sampler` | `mixer/sampler.cpp` | a sampler slot (`BaseTrackPlayerImpl`) |
| `PreviewDeck` | `mixer/previewdeck.cpp` | library preview player |
| `Microphone` | `mixer/microphone.cpp` | mic input player (`BasePlayer`) |
| `Auxiliary` | `mixer/auxiliary.cpp` | aux input player (`BasePlayer`) |
| `SamplerBank` | `mixer/samplerbank.cpp` | save/restore of sampler slot state |
| `PlayerInfo` | `mixer/playerinfo.cpp` | current-track lookup across players |

## Invariants (an agent MUST respect these)
- **Parent before parented_ptr (`P-19`/`AP-13`):** every player QObject gets a parent before its
  `parented_ptr` destructs; `PlayerManager` is the object-tree owner. Creation/teardown is GUI-thread only.
- **Lifetime off the RT thread (`P-17`):** a player's `EngineChannel` is constructed and destroyed on
  the GUI thread and handed to the engine by pointer; never `new`/`delete` a player on the callback.
- **Thread affinity (`P-20`/`AP-14`):** players are GUI QObjects; the RT engine touches their channel
  processing state, not the QObject. No synchronous slot delivery across the RT boundary.
- **Single writer per channel control (`P-06`/`AP-03`):** the player owning `[ChannelN]` is the
  authoritative writer of its state controls; other contexts read via proxy.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `player` | a `BasePlayer`/`BaseTrackPlayer` GUI-owned object | an `EngineChannel` RT node it wires |
| `deck` | a `Deck` player (`[ChannelN]`) | a controller "deck" mapping (arch-controllers-mapping) |
| `channel group` | the `[ChannelN]`/`[SamplerN]` string a player owns | a physical audio channel (arch-audio-io) |
| `load` | binding a `Track` into a player | disk decode of that track (arch-sources-decode) |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| out | `EngineChannel` nodes + wiring | arch-engine-realtime | pointer handoff, GUI-constructed | boundaries/control-to-engine.md |
| in | `[ChannelN],*` control state | arch-control-messaging | `ControlProxy` / `ControlObject` | boundaries/control-to-engine.md |
| in | loaded `Track` objects | arch-library-db | `TrackPointer` load requests | — |
| in | I/O registration | arch-audio-io | `SoundManager` in/out registration | — |

## Key patterns (cited, not restated)
`P-19`, `AP-13`, `P-17`, `P-20`, `AP-14`, `P-06`, `AP-03` — see `kanban/patterns/`. Root house rules:
`/AGENTS.md`. This context is where Qt ownership (`P-19`) and the RT-lifetime rule (`P-17`) meet.
