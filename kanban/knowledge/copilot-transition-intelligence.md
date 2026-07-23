---
id: copilot-transition-intelligence
type: knowledge
title: "Co-pilot transition intelligence — why 'learn what plays next' is the core moat"
status: design
owner: gudjon
created: "2026-07-23"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/knowledge/arrange-nexttrack-copilot-scoring.md
  - kanban/architecture/decisions/ADR-005-open-core-plus-proprietary-intelligence.md
  - kanban/initiatives/initiative-experience-ontology.md
related:
  - kanban/knowledge/copilot-product-assumptions.md
  - kanban/knowledge/nextgen-community-signal-data-sourcing.md
  - res/design/wireframes/arrange-nexttrack-list.md
  - tools/exo/copilot_why_next.py
---

# Co-pilot transition intelligence — the strategic frame

> **Scope boundary (cooperation).** `grok-signal` owns the **scoring policy + build spec** —
> [`arrange-nexttrack-copilot-scoring`](arrange-nexttrack-copilot-scoring.md) is the SSoT for the score
> **layers, weights, fixtures, and build order** (build from *that*). This note owns only the **strategic
> frame**: *why* "learn what plays next" is the core-domain moat, its DDD capability, and the open product
> bet. **No scoring detail is duplicated here** — see Grok's brief. (This note was reconciled after it and
> Grok's brief were written in parallel; the lesson is folded into `FEDERATION.md` lane discipline.)

## The idea (owner, 2026-07-23)
The co-pilot's "NEXT" pick should be **learned from tons of real DJ setlists** — "DJs who played *this*
(or a similar track) played *that* next" — blended with what's **trending**. Mixability says what you
*can* play; the setlist corpus says what actually *works*. Encoded as ordered score layers in Grok's
brief (mixability always first → crate → setlist co-occurrence → trend → personal history).

## Why it is the moat (ADR-005)
Harmonic + tempo scoring is table-stakes maths any app can copy. A **transition model learned from a
large, growing corpus of real sets is a network-effect asset**: more sets processed → better "what plays
next" → more DJs → more sets. That is the "proprietary Migx Intelligence (Layer C)" of ADR-005, and the
layer no competitor ships (digitaldjtips: smart suggestion "remains emergent"). It answers the open flag
[[copilot-product-assumptions]] **A5** ("harmonic + tempo + energy is enough signal" — likely false) and
reinforces **A4** (next-track selection is the useful job). This is captured as `cap-transition-intelligence`
(core) in the capability catalogue.

## Open product bet (declared open — assumption A6)
This is a **bet, not a proven win** (fixture-green ≠ product-closed). The open questions, tracked as
`copilot-product-assumptions` **A6**:
1. Does crowd-transition data actually help a DJ pick better (vs feeling derivative — DJs prize originality)?
2. Corpus **coverage** of an individual crate may be low → similarity-expansion carries more weight than hoped.
3. **Licensing/ToS** of ordered-setlist corpora at scale is unresolved (1001Tracklists has no open API).
4. **Freshness vs safety** — trending must never overwhelm mixability (`✗ clash` always sorts last).

Revisit trigger: first real-DJ evidence via the continuous-customer-evidence loop; Grok feasibility on an
obtainable ordered-setlist corpus. Both are **v2** — v1 ships mixability + a fixture transition stub (Grok brief).
