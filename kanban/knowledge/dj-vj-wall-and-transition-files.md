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

## Lyrics as a prep-time producer (VIS scope, after AUD)

Transcription (Whisper-class) is a **subprocess that writes the package**, same class as
`migx-analyze`: prep-time, never live, never near a deadline. Analysis writes the sidecar; the model
reads the sidecar; nothing listens in real time.

Outputs land in three different homes, and conflating them is the failure:

| Output | Home | Why |
| --- | --- | --- |
| Timestamped lyrics | `lyrics.json` in the package | large; word-level timing is the payload |
| Theme · emotion · temperature | `notes.md` frontmatter | the index — what you filter on |
| Full transcript | package body file | deep read, loaded per candidate |
| **Set theme · storytelling arc** | the **set / session** | an arc is a property of the night, not a record |

A track has no "set theme". Putting one there would make every record claim an arc it cannot know.

### Two failure modes to design against before building it

**Provenance, not just values.** BPM is *measured*, lyrics are *transcribed*, theme and emotion are
*inferred*. Those carry wildly different trust, and `theme: heartbreak` guessed from a mumbled vocal
must not look identical to a BPM from DSP. `pairs.py` already has the shape — every edge stamps
`layer` and `source`. Inferred frontmatter carries how it was derived and a confidence, or it is a
confident lie (`P-34`).

Transcription of club music is wrong **often**: heavy processing, vocal chops, non-English, and
instrumentals with a two-word hook.

**Vocabulary drift.** A model will happily emit `melancholic`, `wistful`, `bittersweet` where the pack
says `dark` — three spellings of one idea, the exact drift `vocab.CLOSED_FIELDS` exists to stop. AI-
proposed frontmatter is **checked against the pack and warned**, never written free.

### What VIS actually wants from this

**Timestamped lyrics, not theme.** Word-level timing is a real tap the compositor can subscribe to —
typographic visuals locked to the vocal is an established VJ technique, and it samples like beat and
phase (`P-21`). Theme and emotion are more use to `set.plan` than to the wall.
