---
id: dj-vj-wall-and-transition-files
type: knowledge
title: "The wall and the glue — visuals and transition audio as one session clock"
status: active
owner: gudjon
authored_by: claude-code
created: "2026-08-18"
lastUpdated: "2026-08-18"
related: [P-21, P-02, ADR-004, ADR-011, initiative-swift-tui-workstation]
---

# The wall and the glue

Field read, 2026: the room already expects a wall of image behind the DJ. A booking is audio **and**
visuals. If Migx is only decks, it is half of what the night needed.

## The opening is not "add a renderer"

Incumbents stay split — a DJ app, plus Resolume or TouchDesigner, plus a hardware box between them,
with a human reconciling three clocks. **The opening is one session object driving both.** Not a
better layer blend mode; Resolume wins that and will keep winning it.

So the bet is: *the wall knows what the DJ knows* — beat, phase, energy, section, now/next, which
technique is running — because it samples the same session the faders write.

## Authoring splits three ways, and one renderer cannot serve all three

| Job | Tool the field actually uses |
| --- | --- |
| Fullscreen generative / reactive | shader-first (WebGPU, Metal) — not a scene graph |
| 3D scene, camera, GLTF | Three/R3F or native Metal |
| Brand, logo, stinger, "now playing" | Rive — native Apple runtime (`ADR-004`) |
| Festival wall, mapping, lasers | Resolume · TouchDesigner · Notch · Pangolin |

**One renderer is a 2019 answer.** The shape is a compositor with several layer authors — which also
means designers ship `.riv` and coders ship shaders without either touching the audio path.

Nobody in the field is asking for a specific web framework in the booth. They are asking for a wall
that does not die. That is a reliability requirement, and it lands on `P-21`: clock direction, budgets
per consumer, a stalled renderer never stalls a deck.

## Transition audio is the honest half of "transitions"

Two different things share the word:

- **Consumer auto-blend** (Apple Music / Spotify DJ) is popular and is our anti-identity: it *plays*
  the night. A pretty crossfade that nobody chose.
- **Club craft** is older and is a *library* problem: risers, impacts, sweepers, acapella stabs,
  4–16 bar FX beds. The DJ chooses the glue.

We own the second. It needs no new subsystem:

- `kind: sfx` in the package frontmatter (a closed vocabulary field, so it cannot drift)
- one inode in `Collection/` like anything else; crated under `Crates/transitions/`
- sidecar carries `fits_after` / `fits_before`, key, length **in bars**, and the technique it serves
- `set.plan` and Arrange may **stage** one; AVAudioEngine plays it as a third node
- **never auto-fired.** An FX bed firing without a receipt is silent Automix in a smaller costume.

Transition packs are becoming a market like sample packs. Identity (ISRC where it exists, sidecar,
crate) indexes them the same way as music.

## What not to build

Three.js as the app shell (`ADR-004` refused this path) · one GPU engine for booth UI and wall — the
budgets differ · live-generated AI video as the wall (latency plus surprise on a deadline nobody can
retry — bake loops offline and play them like tracks) · a Resolume clone · an auto-visualizer as the
product, because club LED is *directed*.

## Where this lands

`P-21` scope extension (clock direction, per-consumer budgets) · `VIS` dossier, after `AUD` · `kind`
in `vocab.CLOSED_FIELDS`. The visual engine is a **consumer** of session state, never a producer —
which is what lets it be built later, by someone else, or not at all, without touching audio or
library architecture.
