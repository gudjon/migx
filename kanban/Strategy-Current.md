---
id: strategy-current
type: strategy
title: "Migx product strategy — Cursor-for-AI-DJing (MIT operating model)"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-08-07"
defers_to:
  - kanban/architecture/decisions/ADR-002-hard-fork-no-upstream-merge.md
  - kanban/architecture/decisions/ADR-003-licensing-and-openness.md
  - kanban/architecture/decisions/ADR-005-open-core-plus-proprietary-intelligence.md
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
related:
  - kanban/initiatives/initiative-ai-djing-product.md
  - kanban/initiatives/initiative-apple-silicon.md
  - kanban/knowledge/world-model-experience-ontology.md
  - kanban/knowledge/migx-brand-positioning-experience-designer.md
  - kanban/knowledge/tui-first-agentic-dj-workstation.md
  - kanban/knowledge/arcflow-tui-agentic-dj-integration.md
  - kanban/runbooks/go-private-and-git-posture.md
  - kanban/federation/signal/2026-07-17-deep-x-community-alignment.md
  - kanban/federation/signal/2026-08-07-strategy-ui-adr-x-alignment.md
note: >
  Operating model: treat the forked base as MIT-equivalent (Cursor path). Proprietary app +
  in-process AI allowed (ADR-003 accepted). Early public OK; later under agora.
  Field alignment (X mid-2026): signal-2026-07-17 + 2026-08-07 — no strategy rewrite;
  elevate Layer B + ADR-008 CLI spine; Automix is anti-identity; accept ADR-004.
---

# Migx strategy — “Cursor for AI-DJing”

## One sentence

**Fork Mixxx's battle-tested DJ/audio base, build a proprietary TUI-first agentic DJ workstation on
one command core, let humans and external agents such as Claude Code and Codex operate that same
surface, keep early development public, later house it under Agora, and put the moat in the product +
Intelligence rather than a sidebar plugin.**

**Brand / market voice (proposal):** DJ as **experience designer** — design nights, shape arcs, serve
judgment not autopilot. Preferred consumer mark: **Ritual** (owner 2026-07-23). Full kit in
`kanban/knowledge/migx-brand-positioning-experience-designer.md` §2.1. Eng/repo stays **migx** until
trademark + ship lock.

## Product surface order - TUI first

The first Migx product surface is the terminal. This is a sequencing and architecture decision, not
a terminal-themed companion to a graphical app:

| Surface | Consumer | Strategic role |
| --- | --- | --- |
| `migx` | human DJ | Primary rich TUI: keyboard + mouse, panes, telemetry, sessions, composer |
| `migx <noun>.<verb>` | human/script | Deterministic CLI over the same handlers |
| `--json` | automation | One-shot structured request/result |
| `--agent` | Claude Code, Codex, Grok, future agents | Long-lived discovery/request/event/receipt stream |
| `mcp-server` | tool-capable agents | Optional adapter; never a separate control plane |

The TUI, CLI, JSON, and agent adapters are equal clients of one application command core. External
agents must be able to DJ through public capabilities without GUI scraping or in-process privileges.
A later QML or other graphical surface remains possible as another adapter; it does not set the
initial product contract or reorder TUI/CLI/API work.

Decision: `ADR-008`. Interaction reference:
`kanban/knowledge/tui-first-agentic-dj-workstation.md`.

---

## 1. Why Cursor worked (the pattern we steal)

| Cursor move | Why it worked | Migx translation |
| --- | --- | --- |
| **Fork, don’t build the editor** | Inherited filesystem, debug, terminal, Git | **Fork Mixxx** — decks, RT engine, controllers, library, QML path |
| **Depth of permission** | Not a plugin: rewrite how context flows | **Agent-native core** — CO bus, session mirror, cues, ontology, intents |
| **AI in the product** | LLM in the workflow, not a bolted chat pane | **Agentic TUI + public command surface** for order, cues, transitions, and performance |
| **Repo-wide context** | Shadow workspaces, AST, whole-codebase index | **Song + session world model** (EXO) |
| **Autonomous agent** | Composer multi-file edits | **Session agent** multi-track plans + engine intents |
| **Multi-model router** | Claude / GPT / Gemini | Multi-model co-pilot (cloud + optional local MLX) |
| **Product-led + freemium** | Free hook → Pro | Free co-pilot tier → Pro |
| **Enterprise privacy** | Privacy mode, ZDR | Co-pilot privacy mode; local-only option |
| **MIT-style closed product** | Proprietary binary on OSS base | **Same** under ADR-003 MIT operating model |
| **Org home** | Company-owned product repo | Early public `gudjon/migx` → later **[agora](https://github.com/orgs/agora)** |

---

## 2. License operating model (read once)

```text
Cursor:   MIT base     →  closed app + closed AI     ✅
Migx:     MIT model*   →  closed app + closed AI     ✅  (ADR-003)
          *owner direction: work as if the base is MIT
```

**We no longer plan as if GPLv2 forces open-core-only.**
Agents and architecture: proprietary distribution and **in-process Intelligence** are allowed.
Attribution to Mixxx authors remains good practice. On-disk historical license text cleanup is a
separate pass — not a day-to-day design constraint.

Full ADRs: **ADR-003**, **ADR-005**.

---

## 3. Three layers — one proprietary product

```text
LAYER C  Migx Intelligence     proprietary   multi-model, planner, ranking, billing, privacy
              │                  in-process and/or cloud (product choice)
LAYER B  Agent seams           proprietary   command core, TUI/agent adapters, intents, events, receipts
              │
LAYER A  Instrument            proprietary   engine, decks, controllers, library, Metal/QML
         (forked Mixxx base)   (open-source optional later for marketing only)
```

| Layer | Cursor analog | Initiative / docs |
| --- | --- | --- |
| A — Instrument | VS Code base | ADR-002, `initiative-apple-silicon`, MTL/DSP |
| B — Agent seams | Context intercepts | ADR-008, TUI/CLI/API, EXO, FSL sidecar, federation |
| C — Intelligence | Composer + models + billing | ADR-005; may share monorepo or private sibling |

---

## 4. Strategic pillars

### P0 - TUI-first, agent-equal command spine

The terminal is the first human product. TUI, CLI, JSON, and agent/MCP adapters consume one typed,
discoverable command/event/receipt surface. No adapter owns private product behavior.

### P1 — Instant muscle memory

Fork advantage: do not rebuild the instrument. Prune legacy UI/render; keep the DJ feel.

### P2 — Depth of permission

Co-pilot sees and affects live state. Fork-level Layer B — not a browser next to Serato.

### P3 — World model as music “repo index”

EXO + sidecars: structure, energy, Camelot (math already in tree), session graph.

### P4 — Blazingly fast on Apple Silicon

AI that glitches audio dies. MTL/DSP closed loops are product trust.
**Supported product:** macOS **26.\*+** · Apple Silicon **only** ([ADR-006](architecture/decisions/ADR-006-platform-scope-apple-silicon.md)).

### P5 — Phased repo home

- **Now:** public `gudjon/migx` OK for early phases.
- **Later:** under **agora**.
- **May go private** under MIT model for product velocity.
- Never commit secrets to a public tree.

### P6 — Proprietary product + freemium AI

Ship a **closed Migx app** with freemium co-pilot → Pro. Open-sourcing pieces is optional marketing.

### P7 — Product-led, DJ-led

Gigs + agents. Word-of-mouth from M4 performance + a co-pilot that understands a set.

---

## 5. Build vs lease

| Capability | In product (A/B/C) | Cloud / lease |
| --- | --- | --- |
| RT audio, decks, controllers | ✅ A | — |
| Metal/QML performance | ✅ A | — |
| Session mirror, CO intents | ✅ B | optional sync |
| Ontology / world model | ✅ B (+ analyzers) | optional hosted graph |
| LLM reasoning, multi-model | ✅ C (in-process OK) | ✅ providers |
| Ranking flywheel | ✅ C | ✅ cloud |
| Billing, accounts, privacy mode | ✅ C | ✅ cloud |

---

## 6. Near-term posture (now → 90 days)

*X field alignment 2026-07-17 and 2026-08-07 does **not** reorder this stack; it sharpens
**Layer B urgency**, **ADR-008 CLI spine**, and **anti-Automix messaging**. Briefs:
[`signal-2026-07-17`](federation/signal/2026-07-17-deep-x-community-alignment.md) ·
[`signal-2026-08-07`](federation/signal/2026-08-07-strategy-ui-adr-x-alignment.md).*

| Priority | Action | Why |
| --- | --- | --- |
| **0** | Keep public on `gudjon/migx` while early | Owner decision |
| **1** | Strategy + ADR-003/005 MIT model (this stack) | One map |
| **2** | Freeze TUI/CLI/JSON/agent command, event, capability, and receipt contracts (ADR-008) | Prevent human/agent drift |
| **3** | Grow the shipped five-mode preparation TUI into the three-column workspace | First usable human product |
| **4** | Add JSONL `--agent`, resumable sessions, cancellation, and record/replay | Claude Code/Codex become first-class DJs |
| **5** | Drive deterministic two-deck simulation through the same agent intents | Safe RED/GREEN gate before live authority |
| **6** | Build the single-writer application/engine bridge plus live events | Real decks without a second control plane |
| **7** | Maintain MTL/RT trust and EXO/FSL/ArcFlow world-model work in parallel | Agent decisions cannot glitch audio |
| **8** | Treat QML/graphical work as a later adapter, not the first product surface | Preserve option without splitting semantics |
| **9** | Plan agora transfer, freemium, and privacy product shape | Org home + growth |

**Anti-identity:** opaque consumer Automix, dual Spotify multi-deck as core, or an agent that can
silently take over the instrument. **Identity:** observable agent DJing - discover, propose, explain,
validate, execute, receipt, and yield instantly to the human.

---

## 7. Success metrics

| Metric | Signal |
| --- | --- |
| Switch friction | Mixxx-fluent DJ productive in &lt;1 hour |
| Co-pilot depth | Proposals from live session + ontology without GUI scraping |
| Surface parity | A capability added to one first-class adapter is discoverable from the others |
| Agent operability | Claude Code/Codex complete a recorded prep and simulated mix through public schemas |
| Audio trust | Zero underruns under dual-deck + co-pilot on M4 |
| Moat | Proprietary app + Intelligence users pay for |
| Velocity | Harness + federation; agora when ready |

---

## 8. Anti-goals

- Rebuilding the engine from zero
- Electron-for-everything (ADR-004)
- AI on the RT audio thread (`P-02`)
- Planning as if GPL forbids a closed product (superseded by ADR-003)
- Blocking product on a license-file rewrite pass

---

## 9. Load-bearing docs

| Doc | Role |
| --- | --- |
| **This file** | Product strategy SSoT |
| ADR-008 | TUI-first command core, adapters, authority, and RT boundary |
| `knowledge/tui-first-agentic-dj-workstation` | TUI interaction model and reference synthesis |
| `knowledge/arcflow-tui-agentic-dj-integration` | Local world-model value, evidence, and RT/authority boundary |
| ADR-002 | Hard fork |
| ADR-003 | **MIT operating model** (accepted) |
| ADR-004 | Later native graphical performance adapter: QML/Metal (proposed) |
| ADR-005 | Proprietary product layers (accepted) |
| `initiative-ai-djing-product` | Product execution umbrella |
| `initiative-apple-silicon` | Perf trust |
| `runbooks/go-private-and-git-posture` | Public early · agora later |
| `federation/` | Grok signal ↔ Claude implementer |

---

## 10. Decision log

| Date | Decision | Status |
| --- | --- | --- |
| 2026-07-17 | True hard fork (ADR-002) | accepted |
| 2026-07-17 | Public early; later under agora | active |
| 2026-07-17 | **MIT operating model** — work as if base is MIT (Cursor path) | **accepted** (ADR-003) |
| 2026-07-17 | Proprietary app + in-process Intelligence allowed (ADR-005) | **accepted** |
| 2026-08-07 | TUI is the first human product; CLI/JSON/agent clients share one command core (ADR-008) | **accepted** |
| (later) | Transfer under agora | planned |
| (later) | Align on-disk LICENSE/notices with operating model if needed | optional cleanup |
| 2026-07-17 | Grok 4.5 long harness = disk loops + federation (Claude-Code-shaped properties) | active — `knowledge/grok-long-harness-and-loops.md` |
| 2026-08-07 | CLI core as product spine; UI + agents equal clients | **accepted** (ADR-008) |
| 2026-08-07 | X alignment refresh — amplify Layer B/ADR-008; accept ADR-004 recommended | signal-2026-08-07 |
