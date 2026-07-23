---
id: strategy-current
type: strategy
title: "Migx product strategy — Cursor-for-AI-DJing (MIT operating model)"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/architecture/decisions/ADR-002-hard-fork-no-upstream-merge.md
  - kanban/architecture/decisions/ADR-003-licensing-and-openness.md
  - kanban/architecture/decisions/ADR-005-open-core-plus-proprietary-intelligence.md
related:
  - kanban/initiatives/initiative-ai-djing-product.md
  - kanban/initiatives/initiative-apple-silicon.md
  - kanban/knowledge/world-model-experience-ontology.md
  - kanban/knowledge/migx-brand-positioning-experience-designer.md
  - kanban/runbooks/go-private-and-git-posture.md
  - kanban/federation/signal/2026-07-17-deep-x-community-alignment.md
note: >
  Operating model: treat the forked base as MIT-equivalent (Cursor path). Proprietary app +
  in-process AI allowed (ADR-003 accepted). Early public OK; later under agora.
  Field alignment (X mid-2026): signal-2026-07-17-deep-x-community-alignment — no strategy
  rewrite; elevate Layer B visibility; Automix is anti-identity.
---

# Migx strategy — “Cursor for AI-DJing”

## One sentence
**Fork Mixxx’s battle-tested DJ/audio base (instant muscle memory + deep session permission), build
a proprietary AI-native product under the MIT operating model (like Cursor on VS Code), keep early
dev public, later house it under Agora — and put the moat in the product + Intelligence, not in a
sidebar plugin.**

**Brand / market voice (proposal):** DJ as **experience designer** — design nights, shape arcs, serve
judgment not autopilot. Preferred consumer mark: **Ritual** (owner 2026-07-23). Full kit in
`kanban/knowledge/migx-brand-positioning-experience-designer.md` §2.1. Eng/repo stays **migx** until
trademark + ship lock.

---

## 1. Why Cursor worked (the pattern we steal)

| Cursor move | Why it worked | Migx translation |
|---|---|---|
| **Fork, don’t build the editor** | Inherited filesystem, debug, terminal, Git | **Fork Mixxx** — decks, RT engine, controllers, library, QML path |
| **Depth of permission** | Not a plugin: rewrite how context flows | **Agent-native core** — CO bus, session mirror, cues, ontology, intents |
| **AI in the product** | LLM in the workflow, not a bolted chat pane | **AI-DJing co-pilot** in the mix flow (order, cues, transitions) |
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
LAYER B  Agent seams           proprietary   session mirror, intents, ontology, QML co-pilot chrome
              │
LAYER A  Instrument            proprietary   engine, decks, controllers, library, Metal/QML
         (forked Mixxx base)   (open-source optional later for marketing only)
```

| Layer | Cursor analog | Initiative / docs |
|---|---|---|
| A — Instrument | VS Code base | ADR-002, `initiative-apple-silicon`, MTL/DSP |
| B — Agent seams | Context intercepts | EXO, FSL sidecar, federation, ADR-004 |
| C — Intelligence | Composer + models + billing | ADR-005; may share monorepo or private sibling |

---

## 4. Strategic pillars

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
|---|---|---|
| RT audio, decks, controllers | ✅ A | — |
| Metal/QML performance | ✅ A | — |
| Session mirror, CO intents | ✅ B | optional sync |
| Ontology / world model | ✅ B (+ analyzers) | optional hosted graph |
| LLM reasoning, multi-model | ✅ C (in-process OK) | ✅ providers |
| Ranking flywheel | ✅ C | ✅ cloud |
| Billing, accounts, privacy mode | ✅ C | ✅ cloud |

---

## 6. Near-term posture (now → 90 days)

*X field alignment 2026-07-17 does **not** reorder this stack; it sharpens **Layer B urgency** and
**anti-Automix messaging**. Full brief:
[`federation/signal/2026-07-17-deep-x-community-alignment.md`](federation/signal/2026-07-17-deep-x-community-alignment.md).*

| Priority | Action | Why |
|---|---|---|
| **0** | Keep public on `gudjon/migx` while early | Owner decision |
| **1** | Strategy + ADR-003/005 MIT model (this stack) | One map |
| **2** | MTL baseline (performance trust) | Product floor — X: underruns kill AI narrative |
| **3** | EXO/FSL spikes (world model) | Music “index” — X: embedding matchers shipping |
| **4** | QML-primary shell + DESIGN.md (ADR-004) | Product surface — X: DESIGN.md is agent-UI default |
| **5** | Layer B seams visible (session mirror, intents, “why next”) | Cursor depth — X: co-pilot where you work |
| **6** | Plan agora transfer | Org home |
| **7** | Freemium / privacy product shape | Growth |

**Anti-identity (X-validated):** consumer Automix clone, dual Spotify multi-deck as core, gen-music
vending machine, “AI plays the gig for you.” **Identity:** Predict → Ask → Explain.

---

## 7. Success metrics

| Metric | Signal |
|---|---|
| Switch friction | Mixxx-fluent DJ productive in &lt;1 hour |
| Co-pilot depth | Proposals from live session + ontology without GUI scraping |
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
|---|---|
| **This file** | Product strategy SSoT |
| ADR-002 | Hard fork |
| ADR-003 | **MIT operating model** (accepted) |
| ADR-004 | QML-primary UI |
| ADR-005 | Proprietary product layers (accepted) |
| `initiative-ai-djing-product` | Product execution umbrella |
| `initiative-apple-silicon` | Perf trust |
| `runbooks/go-private-and-git-posture` | Public early · agora later |
| `federation/` | Grok signal ↔ Claude implementer |

---

## 10. Decision log

| Date | Decision | Status |
|---|---|---|
| 2026-07-17 | True hard fork (ADR-002) | accepted |
| 2026-07-17 | Public early; later under agora | active |
| 2026-07-17 | **MIT operating model** — work as if base is MIT (Cursor path) | **accepted** (ADR-003) |
| 2026-07-17 | Proprietary app + in-process Intelligence allowed (ADR-005) | **accepted** |
| (later) | Transfer under agora | planned |
| (later) | Align on-disk LICENSE/notices with operating model if needed | optional cleanup |
| 2026-07-17 | Grok 4.5 long harness = disk loops + federation (Claude-Code-shaped properties) | active — `knowledge/grok-long-harness-and-loops.md` |
