---
id: copilot-transition-intelligence
type: knowledge
title: "Co-pilot transition intelligence — learn 'what plays next' from a corpus of real DJ sets"
status: design
owner: gudjon
created: "2026-07-23"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/architecture/decisions/ADR-005-open-core-plus-proprietary-intelligence.md
  - kanban/initiatives/initiative-experience-ontology.md
related:
  - kanban/knowledge/copilot-product-assumptions.md
  - kanban/knowledge/nextgen-community-signal-data-sourcing.md
  - kanban/knowledge/world-model-experience-ontology.md
  - res/design/wireframes/arrange-nexttrack-list.md
  - tools/exo/copilot_why_next.py
---

# Co-pilot transition intelligence

**The idea (owner, 2026-07-23):** the co-pilot's "NEXT" pick shouldn't come from harmonic/tempo theory
alone — it should be **learned from tons of real DJ setlists**: "DJs who played *this* track (or one like
it) played *that* next," blended with what's **trending**. Mixability says what you *can* play; the
setlist corpus says what actually *works*.

## Why this is the moat (ADR-005)
Harmonic + tempo scoring is table-stakes maths any app can copy. A **transition model learned from a
large, growing corpus of real sets is a network-effect asset**: more sets processed → better "what plays
next" → more DJs → more sets. That is the "proprietary Migx Intelligence (Layer C)" ADR-005 names, and it
is the layer no competitor currently ships (digitaldjtips: smart suggestion "remains emergent"). It also
answers the open flag in [[copilot-product-assumptions]] **A5** ("harmonic + tempo + energy is enough
signal" — likely false) and reinforces **A4** (next-track selection is the useful job).

## The co-pilot NEXT pick = a blend of signals
The ranked pick composes four signals; the **reason chip names which one drove it** (explainable, not a
black box):

| Signal | Question it answers | Source | Status |
|---|---|---|---|
| **Mixability** (harmonic + tempo) | *Can* I mix it cleanly? | Camelot + `tempo_compat` (local analysis) | built (`copilot_why_next.py`) |
| **Transition co-occurrence** | Do real DJs play this *after* what's on now? | corpus of **ordered** setlists → P(next=Y \| cur=X) | **new — this note** |
| **Similarity expansion** | Cold-start: what follows tracks *like* this one? | audio / artist / key-energy cluster | planned (EXO) |
| **Trending / popularity** | Is it hot right now (fresh, crowd-tested)? | Beatport charts, YT, setlist heat | research ([[nextgen-community-signal-data-sourcing]]) |

Weights are **learned/recalibrated against real DJ accept/override telemetry**, not hand-set — the closure
discipline of [[copilot-product-assumptions]] (fixture-green ≠ product-closed). A crowd-proven transition
may *outrank* a merely-harmonic one when the corpus is confident.

## The model (extends what exists)
`tools/exo/copilot_why_next.py` already builds an `edge_index` and scores a `planned-transition` relation
from a **single session graph**. Transition intelligence is that idea at **corpus scale**:
- Ingest ordered tracklists → a weighted directed graph `X → Y` (edge weight = co-occurrence count /
  recency-decayed). Store as an EXO ontology artifact (sidecar), consumed the same way the session graph
  is today.
- **Cold-start / coverage** (most of a DJ's library won't be in the corpus): fall back to
  *similarity expansion* — treat "tracks like X" as sources of transitions — and to mixability. The pick
  is never empty; it degrades to local scoring, always non-modal.
- **Blend, then rank**; surface the top reason. Keep the whole hot path **cached/offline** (the
  `ng-music-judge` no-network floor) — the corpus/model is precomputed, never fetched mid-set.

## Data sourcing (Grok lane — extends the community-signal brief)
[[nextgen-community-signal-data-sourcing]] already mapped popularity sources. Transition learning needs
**ordered** setlists specifically: **1001Tracklists** is the richest ordered corpus (but anti-scrape, no
open API → licensing/partner path), Beatport = chart *heat* not order, Mixcloud/SC = partial. Open item
for `grok-signal`: what ordered-setlist corpus is **licensable/obtainable at scale**, coverage vs a real
DJ library, and the matching key (ISRC/artist-title) — v1 fetchable vs v2 licensed.

## Open assumptions (declared open — needs evidence before it's a product win)
1. **Does crowd-transition data actually help a DJ pick better?** (vs feeling generic/derivative — DJs
   prize originality). Test: real-DJ accept/override on transition-driven vs mixability-only picks.
2. **Corpus coverage** of an individual DJ's crate may be low (underground/promo tracks absent) →
   similarity expansion carries more weight than hoped.
3. **Licensing/ToS** of setlist corpora at scale is unresolved (1001Tracklists has no open API).
4. **Freshness vs safety** — trending can push untested tracks; weight must not overwhelm mixability.

These join the [[copilot-product-assumptions]] table (as **A6**); revisit trigger = first real DJ evidence
via the continuous-customer-evidence loop.
