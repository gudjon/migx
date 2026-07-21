---
id: nextgen-shadow-app-proposal
type: knowledge
title: "NextGen shadow app — a parallel Agent-DJ build the fleet grows module-by-module (federation discussion)"
status: discussion
owner: gudjon
created: "2026-07-19"
lastUpdated: "2026-07-19"
related:
  - ai-code-migration-methodology
  - ui-non-modal-error-ux
  - nextgen-engine-reuse-boundary-codex
  - nextgen-music-management-mode
  - nextgen-dj-ux-modes-and-signal
  - mod-music-management-mode
  - nextgen-community-signal-data-sourcing
  - initiative-ui-modernization
  - ADR-004-ui-stack-qml-vs-rive-vs-react
  - ADR-005-open-core-plus-proprietary-intelligence
  - ADR-006-platform-scope-apple-silicon
  - migx-cursor-model
decision_target: "ADR-007 — NextGen UI engine + shadow-app strategy"
---

# NextGen shadow app — federation discussion

**Owner direction (2026-07-19):** don't migrate the legacy UI in place. Stand up a **NextGen / Agent-DJ
version as a parallel shadow build** — the full new development — and move **one module at a time, done
right**, DESIGN.md-driven, on the **most optimized UI engine that is both fast and good to work with
agents** (Claude Code, Grok CLI, Codex). This doc anchors the fleet discussion; it converges into
**ADR-007**.

**Cursor-path framing (owner, same day):** like Cursor shipping a VS Code fork first and then
promoting the new **Agent UI**, Migx keeps classic as the working base and does **all new UI work in
the NextGen framework** until the old surface is fully strangled. End state = one product on the new
UI — not permanent dual roadmaps. Detail: `nextgen-agent-dj-shadow-product.md` §Owner intent.

**Music-management refinement (owner, 2026-07-21):** the core live-DJ problem is not only a better
deck skin. It is often arrangement under pressure: quickly finding the next song, recognizing the
right version, seeing tags/playlists/community context, staging it, and loading it without increasing
cognitive load in a busy club. NextGen should therefore include a first-class full-screen
**music-management mode** that the DJ can switch into and out of quickly while playback continues.
Detail: `nextgen-music-management-mode.md`.

## The strategy: strangler-fig at the APP level
Instead of untangling legacy skin XML component-by-component *inside* the running app (in-place
migration), build a **new app shell alongside** it:

- **Reuse Layer A unchanged** — the proven C++ RT audio engine, decks, effects, ControlObject bus
  (`[Group],key`). It works; it is not the problem. NextGen links/talks to it, does not rewrite it.
- **New Layer B/C** — a clean, agent-first UI shell + the co-pilot/EXO seams, built fresh.
- The current app keeps shipping/testable; NextGen grows until it *is* the product. Each module lands
  behind the migration **judge** (equivalence vs the legacy behaviour + the non-modal-UX criterion), so
  "shadow" never means "unverified."
- **Forward work rule:** classic UI is keep-alive only; product UI investment is NextGen-only,
  module-by-module, until migration is complete.

Why shadow beats in-place here: the legacy skin stack is deeply entangled and is the source of the UX
failures (modal dialogs mid-set). A clean shell lets every module be **done right from line one**
against DESIGN.md tokens, instead of inheriting legacy structure. It also gives each agent a bounded,
low-collision surface. The Cursor analogy is the product story; strangler + CO facade is the engineering
method.

## The open decision: which UI engine? (the crux — needs the fleet)
Requirements: **fast on Apple-Silicon/Metal** (ADR-006 macOS-arm64-only unlocks native options),
**declarative + DESIGN.md-token-driven**, **agent-legible** (Claude/Grok/Codex can read+edit a module
and a judge can verify it), and **cheap to bind to the existing C++ engine**.

| Engine | For | Against |
|---|---|---|
| **QML, done as a real design system** (ADR-004 target) | Declarative + agent-legible; binds C++ cleanly (engine already Qt); Metal via Qt RHI; 212 QML files already exist | Qt/QML↔C++ boilerplate; "QML" today = the legacy skin baggage we're fleeing unless restructured |
| **Slint** (Rust/C++ declarative DSL) | Very clean agent-friendly markup; fast; native C++ binding; small | Younger ecosystem; another dep; waveform/GPU custom-node story unproven |
| **SwiftUI** (native macOS) | Truly native, Metal-backed, Apple's flagship; macOS-only is fine now | Swift↔C++ RT-engine bridge is costly; least mature for our agents; hard macOS lock |
| **Web / React / Tauri** | Agents know it best | 120fps Metal waveform in a webview is doubtful; it is the README's "Electron-for-everything" anti-goal |

**My (claude-code) seed POV:** the honest default is **QML-as-a-real-design-system** (reaffirm ADR-004,
lowest engine-bind cost, already partly built) with **Slint as the challenger worth a bake-off**. Rather
than argue it — run the blog's "stress-test on 3 samples" pattern: **build the SAME first module (one
deck strip: transport + waveform + a few controls) in QML and in Slint**, then score both on (a) agent
edit/verify ergonomics, (b) frame perf on M4, (c) C++-engine bind cost, (d) DESIGN.md-token fit. Decide
ADR-007 on evidence, not taste (DC-PDCL-2.7).

## Open questions for the fleet
1. **Engine** — QML-design-system vs Slint vs SwiftUI vs web? (bake-off or straight call?)
2. **Engine-reuse boundary** — NextGen links `mixxx-lib` in-process and reads the ControlObject bus? Or
   a thin IPC/agent-seam boundary? (this decides Layer-A coupling)
3. **First module** — deck strip (transport+waveform), co-pilot panel, or the music-management mode
   that owns next-queue decisions?
4. **App target** — a new `migx-ng` build target beside `migx`, or a runtime skin/flag switch?

## Roles in this discussion
- **grok-signal**: scout the 2026 field — what UI engine are *agent-first, real-time, native* teams
  actually using; agent-ergonomics + Metal perf signal; Slint vs QML vs SwiftUI maturity; and which
  music/community signals are legitimate enough to show in the next-track mode.
- **codex-cli**: map the **engine-reuse boundary** — how NextGen cleanly links Layer A (mixxx-lib / CO
  bus) without dragging in the legacy skin/widget stack; feasibility + risks; the judge shape for
  both performance modules and music-management mode.
- **claude-code**: synthesize into ADR-007 + prototype the bake-off module(s) + run build/verify.
