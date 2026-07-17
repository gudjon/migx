# Migx

**The co-pilot sits in the mix — not in a chat pane beside it.**

Migx is an **AI-DJing** instrument: decks, library, controllers, and a real-time audio engine that an
agent can *read and shape*. Same muscle memory DJs expect, built for a different destiny: **Cursor for
music**. Migx is free software under the GNU GPL v2 (see `LICENSE` and `NOTICE`).

| | |
|---|---|
| **Author** | Gudjon Mar Gudjonsson (OZ) |
| **Platforms** | macOS (Apple Silicon first), Linux, Windows |
| **North star** | Blazingly fast on M4/M5 — zero underruns while co-pilot is live |
| **Home** | Early public on this repo → later [agora](https://github.com/orgs/agora) |

---

## Why Migx exists

Streaming DJ apps won catalog convenience. Pro suites won hardware and stems. Nobody won **depth of
permission** for an agent that understands a *set* — energy, Camelot, cue points, the next three
tracks — the way Cursor understands a codebase.

Migx steals Cursor’s pattern, not Cursor’s product:

| Cursor | Migx |
|---|---|
| Fork the editor | Fork the DJ instrument |
| Rewrite context flow | Agent seams on the ControlObject bus |
| Repo-wide index | Song + **session experience ontology** (EXO) |
| Composer in the loop | Co-pilot in the **mix flow** |
| Closed app + AI on MIT base | Same operating model ([ADR-003](kanban/architecture/decisions/ADR-003-licensing-and-openness.md)) |

We do **not** rebuild the engine from zero. We do **not** bolt a web chatbot onto Serato. We own the
instrument, the seams, and the Intelligence.

---

## The three layers

```text
LAYER C   Intelligence     multi-model co-pilot, ranking, freemium → Pro, privacy mode
LAYER B   Agent seams      session mirror · intents · ontology · QML co-pilot chrome
LAYER A   Instrument       RT engine · decks · controllers · library · Metal / QML
```

All three are product. Open-sourcing pieces later is optional marketing — not the plan’s load-bearing
beam. Full map: [`kanban/Strategy-Current.md`](kanban/Strategy-Current.md).

---

## Product thesis: AI-DJing

- **Session as graph.** Tracks carry structure, energy curves, harmonic journey, cues-as-experience.
  A set is edges between songs — not a flat playlist.
- **Co-pilot with permission.** Propose order, set cues, flag energy/key collisions, suggest
  transitions — from live state, not GUI scraping.
- **House physics.** The audio callback never allocates, locks, or takes network I/O. A “smarter”
  feature that glitches audio is a regression, not a feature.
- **Dark console surface.** QML-primary UI, design tokens in [`res/design/DESIGN.md`](res/design/DESIGN.md)
  → Theme bridge. Near-black decks, cool accent, transport-first density — a supercar cockpit, not a
  marketing site inside a window.
- **Streaming honesty.** Spotify dual-deck via public APIs is a closed partner path. Migx’s near-term
  path is **prep + ontology + local multi-deck** (Octave-style sequence for DRM), not DRM theatre.

---

## What we kept from Mixxx

The load-bearing instrument:

- Real-time multi-deck engine, effects, vinyl/DVS paths  
- MIDI/HID controllers and the ControlObject bus  
- Library, analysis hooks, QML skin surface  

What we do not pretend to be: an upstream-tracking soft fork. **Hard fork, own destiny**
([ADR-002](kanban/architecture/decisions/ADR-002-hard-fork-no-upstream-merge.md)). Upstream authors
keep attribution — [`kanban/AUTHORS.md`](kanban/AUTHORS.md).

---

## Near-term plan (the board)

| Priority | Thrust | Why |
|---|---|---|
| **1** | **Apple Silicon trust** — Metal waveforms, DSP, p99/max + zero underruns | Co-pilot dies if audio dies |
| **2** | **EXO / world model** — song + session ontology, hybrid crates, paste-import for stream IDs | Music “index” for agents |
| **3** | **QML shell + design tokens** — DESIGN.md → Theme, co-pilot chrome | Product surface |
| **4** | **Agent seams** — session mirror, intent inbox, ControlObject-safe proposals | Cursor-depth permission |
| **5** | **Intelligence path** — freemium co-pilot shape, privacy mode (in-process OK) | Moat users pay for |
| **6** | **Org home** — public early → agora; secrets never in public history | Velocity + hygiene |

Anti-goals: Electron-for-everything, AI on the RT thread, dual Spotify stream hacks, “wait for a
license file rewrite before shipping.”

Strategy SSoT: [`kanban/Strategy-Current.md`](kanban/Strategy-Current.md) ·
initiatives under [`kanban/initiatives/`](kanban/initiatives/).

---

## Build (Apple Silicon first)

Full guide: [CONTRIBUTING.md](CONTRIBUTING.md) · M4 runbook:
[`kanban/runbooks/build-setup-macos-m4.md`](kanban/runbooks/build-setup-macos-m4.md).

```shell
source tools/macos_buildenv.sh setup
cmake -S . -B build -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$MIXXX_VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DCMAKE_OSX_ARCHITECTURES=arm64
cmake --build build --parallel
```

Task graph (thin orchestrator, not a second build system):

```shell
brew install just   # once
just build          # configure + compile
just test
just lint-changed   # fast gate before commit
just theme-check    # DESIGN.md ↔ Theme.qml
just exo-fixtures-check
just fleet          # federation inbox priority
```

---

## How Migx is developed

Migx is built with an **agent harness** — markdown-as-code memory, closed-loop dossiers, and
git-mediated multi-agent mail. The product is agent-native because the *engineering system* is.

| Surface | What |
|---|---|
| [`AGENTS.md`](AGENTS.md) | House physics + harness entry |
| [`kanban/`](kanban/AGENTS.md) | Doctrine, playbook, patterns, dossiers, strategy |
| [`kanban/federation/`](kanban/federation/FEDERATION.md) | Peers: **Claude** (implement) · **Codex** (verify) · **Grok** (signal) |
| [`CLAUDE.md`](CLAUDE.md) / [`GROK.md`](GROK.md) | Thin tool routing |
| [`.claude/`](.claude/) | Rules, skills, workflows for Claude Code |

**Operating rules agents live by:** everything is a closed loop; everything load-bearing is code;
one owner per path; real-time safety is non-negotiable. Patterns are cited by ID (`P-02`, `P-03`, …)
under [`kanban/patterns/`](kanban/patterns/).

EXO fixtures and Spotify **prep-only** identity tooling live under the experience-ontology spike and
`tools/exo/` — sequence and ontology first; partner multi-deck streaming later if ever.

---

## Design language

Dark DJ console. Near-black surfaces (`#1e1e1e` / sunken `#0C0C0C`), light text, accent blue for
transport, green for active, red for danger. Tokens are SSoT in
[`res/design/DESIGN.md`](res/design/DESIGN.md); regenerate Theme with
`just theme-check` / `tools/design/gen_theme_from_design.py`. UI stack decision: QML-primary
([ADR-004](kanban/architecture/decisions/ADR-004-ui-stack-qml-vs-rive-vs-react.md)).

---

## Status & license posture

- **Licensed under the GNU GPL v2** — see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE). Product-model
  and proprietary-layer aspirations are tracked in ADR-003 and remain subject to that license.  
- **Attribution** to prior contributors is retained in [`NOTICE`](NOTICE) and in source-file headers.  
- **Public early** on this tree is intentional; product home may move under agora and may go private
  for velocity. Never commit secrets here.

---

## Load-bearing links

| Doc | Role |
|---|---|
| [Strategy-Current](kanban/Strategy-Current.md) | Product strategy SSoT |
| [ADR-002](kanban/architecture/decisions/ADR-002-hard-fork-no-upstream-merge.md) | Hard fork |
| [ADR-003](kanban/architecture/decisions/ADR-003-licensing-and-openness.md) | MIT operating model |
| [ADR-004](kanban/architecture/decisions/ADR-004-ui-stack-qml-vs-rive-vs-react.md) | QML-primary UI |
| [ADR-005](kanban/architecture/decisions/ADR-005-open-core-plus-proprietary-intelligence.md) | Layers A/B/C |
| [initiative-apple-silicon](kanban/initiatives/initiative-apple-silicon.md) | Perf trust |
| [initiative-ai-djing-product](kanban/initiatives/initiative-ai-djing-product.md) | Product umbrella |
| [world-model / EXO](kanban/knowledge/world-model-experience-ontology.md) | Music as graph |
| [CONTRIBUTING](CONTRIBUTING.md) | Build, style, PRs |

---

*Migx — instrument in Layer A, permission in Layer B, Intelligence in Layer C. The mix is the
context window.*
