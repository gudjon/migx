---
id: ADR-005
type: decision
title: "Proprietary product stack — instrument + in-process Intelligence (Cursor/MIT model)"
status: accepted
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
related:
  - ADR-002
  - ADR-003
  - ADR-004
  - strategy-current
  - initiative-ai-djing-product
  - world-model-experience-ontology
note: >
  Under ADR-003 MIT operating model. Proprietary binary + in-process AI allowed (Cursor path).
  Open-core is optional, not required.
---

# ADR-005 — Proprietary Migx product (Cursor stack)

## Context
We build **Cursor for AI-DJing**: fork Mixxx’s instrument, embed deep AI, ship a product company
stack. Under **ADR-003 (MIT operating model)** we do **not** constrain the architecture to GPL
open-core-only. Closed app + closed AI (including in-process) is the design target.

Product strategy SSoT: `kanban/Strategy-Current.md`.

## Decision

### D1 — Three layers, one product (all may be proprietary)

```text
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER C — Migx Intelligence (proprietary)                              │
│  Multi-model router · session planner · ranking · co-pilot · billing    │
│  Privacy modes · freemium/Pro · optional cloud                          │
│  May run in-process, helper process, and/or cloud — product choice      │
└───────────────────────────────▲─────────────────────────────────────────┘
                                │ deep session context (not a weak plugin)
┌───────────────────────────────┴─────────────────────────────────────────┐
│  LAYER B — Agent seams (product core)                                   │
│  Session mirror · intent path · ontology · CO-safe control · QML chrome │
│  “Depth of permission” — Cursor’s intercept analog                      │
└───────────────────────────────▲─────────────────────────────────────────┘
                                │ ControlObject, visual taps, library
┌───────────────────────────────┴─────────────────────────────────────────┐
│  LAYER A — Instrument (forked Mixxx base)                               │
│  RT engine · decks · FX · controllers · library · waveforms · QML       │
│  Hard fork free to prune (ADR-002) · Apple Silicon north-star           │
└─────────────────────────────────────────────────────────────────────────┘
```

| Layer | Name | Posture (MIT model) | Contents |
|---|---|---|---|
| **A** | Instrument | Proprietary product (or selective open later) | Engine, decks, FX, controllers, library, waveforms, QML |
| **B** | Agent seams | Proprietary product | Session mirror, intents, ontology formats, CO hooks |
| **C** | Intelligence | Proprietary (always for secret sauce) | Models, planner, ranking, billing, privacy, cloud |

**No legal requirement** that C stay out-of-process. Prefer boundaries for *engineering* reasons
(crash isolation, multi-model hosting, team ownership) — not for copyleft.

### D2 — Depth of permission (Layer B) — non-negotiable product surface

Expose and accept (with house physics: single CO writer `P-06`, no RT alloc `P-02`):

- Live deck/player state, playhead, loaded tracks  
- Cue / loop / intro-outro markers  
- Crate / upcoming order  
- Ontology + energy/harmonic graph (EXO)  
- Intent proposals the engine accepts/rejects/queues  

Homes: ControlObject bus, sidecars, session-mirror, intent-inbox, QML co-pilot chrome (ADR-004).

### D3 — Intelligence (Layer C) — Cursor’s closed AI analog

| Capability | Cursor analog | Migx |
|---|---|---|
| Multi-model | Claude/GPT/Gemini switch | Router in product |
| Autonomous agent | Composer | Session planner / multi-track proposals |
| Whole-project context | Shadow workspace | Song+session world model |
| Privacy / ZDR | Enterprise privacy | Co-pilot privacy mode |
| Freemium → Pro | Completions quota | Free tier → Pro |
| Distribution | Closed app updates | Proprietary Migx builds (+ optional cloud) |

**In-process AI is allowed** (deepest product integration). Cloud remains for multi-model, sync, billing.

### D4 — Repo home (unchanged phase plan)
- Early: public `gudjon/migx` OK  
- Later: [`agora`](https://github.com/orgs/agora)  
- May go fully private for product velocity under MIT model  
- Runbook: `runbooks/go-private-and-git-posture.md`

### D5 — Open source as optional marketing, not architecture law
We may open-source **selected** libraries, docs, or controller mappings for growth. That is a
**product choice**. Default ship is a **proprietary Migx application** with proprietary Intelligence.

### D6 — House physics still bind
MIT model does not relax RT safety, CO single-writer, or parented_ptr rules. A faster proprietary
feature that allocates on the audio thread is still a regression (`P-02`).

## Boundary checklist (engineering, not copyleft)

1. **Secret sauce / models / billing?** → Layer C (can still be same monorepo or private sibling).  
2. **Needs RT / CO / QML?** → A or B; respect `P-02` / `P-06` / `P-20`.  
3. **Crash isolation useful?** → optional helper process for C.  
4. **Public tree?** → no secrets.  

## Consequences
- Full Cursor economics: closed product + freemium AI + privacy story.  
- Agents implement co-pilot **in the product**, not only as a side web app.  
- Prior “must arm’s-length or violate GPL” guidance is **withdrawn** under ADR-003.  
- Performance (Apple Silicon) remains trust for any AI feature.

## Status
**Accepted** under ADR-003 MIT operating model (2026-07-17).
